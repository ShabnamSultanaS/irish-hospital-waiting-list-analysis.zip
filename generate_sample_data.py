"""
Generate a realistic sample dataset matching the NTPF Open Data schema.

The real data is published monthly on data.gov.ie (Outpatient and
Inpatient/Day Case waiting lists). This generator mirrors that schema so
the entire analysis runs out-of-the-box; swap in the real CSVs by
following data/DOWNLOAD.md and every script works unchanged.

Schema (one row = number waiting in a time band, per snapshot):
  archive_date | hospital_group | hospital | specialty | adult_child |
  case_type (OPD / IPDC) | time_band | waiting
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

SEED = 7
rng = random.Random(SEED)

HOSPITAL_GROUPS = {
    "Dublin Midlands": ["St. James's Hospital", "Tallaght University Hospital",
                        "Naas General Hospital", "Midland Regional Tullamore"],
    "Ireland East": ["Mater Misericordiae", "St. Vincent's University Hospital",
                     "Wexford General Hospital"],
    "RCSI Hospitals": ["Beaumont Hospital", "Connolly Hospital",
                       "Our Lady of Lourdes Drogheda"],
    "Saolta": ["University Hospital Galway", "Sligo University Hospital",
               "Letterkenny University Hospital"],
    "South/South West": ["Cork University Hospital", "University Hospital Waterford",
                         "University Hospital Kerry"],
    "UL Hospitals": ["University Hospital Limerick", "Ennis Hospital"],
    "Children's Health Ireland": ["CHI at Crumlin", "CHI at Temple Street",
                                  "CHI at Tallaght"],
}

# (specialty, base OPD waiting, monthly growth factor)
SPECIALTIES = [
    ("Orthopaedics", 4200, 1.008), ("Ophthalmology", 3800, 1.006),
    ("Ear Nose & Throat", 3600, 1.009), ("Dermatology", 3100, 1.011),
    ("General Surgery", 2600, 1.004), ("Gynaecology", 2300, 1.007),
    ("Urology", 2100, 1.006), ("Cardiology", 1900, 1.003),
    ("Neurology", 1700, 1.010), ("Pain Relief", 1400, 1.005),
    ("Rheumatology", 1300, 1.004), ("Gastro-Enterology", 1250, 1.002),
    ("Vascular Surgery", 900, 1.001), ("Plastic Surgery", 850, 1.003),
    ("Endocrinology", 800, 1.005),
]

TIME_BANDS = ["0-3 Months", "3-6 Months", "6-9 Months", "9-12 Months",
              "12-18 Months", "18+ Months"]
# Long-wait tail slowly shrinking over time (Waiting List Action Plan effect)
BASE_BAND_WEIGHTS = [0.30, 0.20, 0.14, 0.11, 0.13, 0.12]

MONTHS = pd.date_range("2023-01-31", "2026-06-30", freq="ME")


# Structural differences between groups: some carry a heavier long-wait
# tail (capacity constraints), others clear lists faster.
GROUP_TAIL_FACTOR = {
    "Dublin Midlands": 1.05, "Ireland East": 0.85, "RCSI Hospitals": 0.95,
    "Saolta": 1.25, "South/South West": 1.10, "UL Hospitals": 1.45,
    "Children's Health Ireland": 0.70,
}


def band_weights(month_index: int, tail_factor: float = 1.0) -> list[float]:
    """Shift weight gradually from long to short bands over time,
    scaled by each group's structural tail factor."""
    shift = min(month_index * 0.0022, 0.08)
    w = BASE_BAND_WEIGHTS.copy()
    w[0] += shift * 0.6
    w[1] += shift * 0.4
    w[4] = max(0.01, (w[4] - shift * 0.45) * tail_factor)
    w[5] = max(0.01, (w[5] - shift * 0.55) * tail_factor)
    total = sum(w)
    return [x / total for x in w]


def main() -> None:
    rows = []
    for mi, archive_date in enumerate(MONTHS):
        seasonal = 1.0 + 0.03 * (1 if archive_date.month in (1, 2, 12) else 0) \
                       - 0.02 * (1 if archive_date.month in (6, 7) else 0)
        for group, hospitals in HOSPITAL_GROUPS.items():
            weights = band_weights(mi, GROUP_TAIL_FACTOR[group])
            paediatric = group == "Children's Health Ireland"
            for hospital in hospitals:
                hosp_scale = rng.uniform(0.55, 1.45)
                for specialty, base, growth in SPECIALTIES:
                    if paediatric and specialty in ("Gynaecology", "Vascular Surgery",
                                                    "Pain Relief", "Rheumatology"):
                        continue
                    for case_type, ct_scale in (("OPD", 1.0), ("IPDC", 0.22)):
                        level = (base * ct_scale * hosp_scale
                                 * (growth ** mi) * seasonal
                                 / len(hospitals) / 4.5)
                        noise = rng.uniform(0.9, 1.1)
                        for band, w in zip(TIME_BANDS, weights):
                            waiting = max(0, round(level * w * noise * rng.uniform(0.92, 1.08)))
                            if waiting == 0:
                                continue
                            rows.append({
                                "archive_date": archive_date.date().isoformat(),
                                "hospital_group": group,
                                "hospital": hospital,
                                "specialty": specialty,
                                "adult_child": "Child" if paediatric else "Adult",
                                "case_type": case_type,
                                "time_band": band,
                                "waiting": waiting,
                            })

    df = pd.DataFrame(rows)

    # Realistic imperfections for the cleaning step to handle
    idx = df.sample(frac=0.01, random_state=SEED).index
    df.loc[idx, "specialty"] = df.loc[idx, "specialty"].str.upper()
    idx = df.sample(frac=0.005, random_state=SEED + 1).index
    df.loc[idx, "hospital"] = df.loc[idx, "hospital"] + "  "
    dupes = df.sample(frac=0.003, random_state=SEED + 2)
    df = pd.concat([df, dupes], ignore_index=True)

    out = Path("data/sample")
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "ntpf_waiting_lists.csv", index=False)
    print(f"Generated {len(df):,} rows across {df['archive_date'].nunique()} monthly snapshots")


if __name__ == "__main__":
    main()
