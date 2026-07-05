"""
Data preparation: clean and standardise the raw NTPF extract.

Steps (documented for reproducibility):
  1. Strip whitespace from text columns
  2. Standardise specialty casing (fixes mixed UPPER/Title case)
  3. Remove exact duplicate rows
  4. Validate time bands against the known NTPF band set
  5. Add analysis features: ordered band category, long-wait flag,
     Slaintecare breach proxy, year_month
  6. Export a clean analysis table + Power BI-ready extracts
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW = Path("data/sample/ntpf_waiting_lists.csv")
PROCESSED = Path("data/processed")

BAND_ORDER = ["0-3 Months", "3-6 Months", "6-9 Months", "9-12 Months",
              "12-18 Months", "18+ Months"]
# Slaintecare maximum wait targets: 10 weeks (OPD), 12 weeks (IPDC).
# The open data's finest band is 0-3 months, so ">3 months waiting" is
# used as a conservative proxy for a target breach (documented limitation).
BREACH_BANDS = BAND_ORDER[1:]
LONG_WAIT_BANDS = ["12-18 Months", "18+ Months"]


def main() -> None:
    df = pd.read_csv(RAW)
    n_raw = len(df)

    # 1-2. Text hygiene
    for col in ("hospital_group", "hospital", "specialty", "time_band"):
        df[col] = df[col].astype(str).str.strip()
    df["specialty"] = df["specialty"].str.title().str.replace(" & ", " & ")
    df["specialty"] = df["specialty"].replace({"Ear Nose & Throat": "Ear Nose & Throat",
                                               "Gastro-Enterology": "Gastro-Enterology"})

    # 3. Duplicates
    df = df.drop_duplicates()
    n_dupes = n_raw - len(df)

    # 4. Validate bands
    bad_bands = ~df["time_band"].isin(BAND_ORDER)
    assert bad_bands.sum() == 0, f"Unknown time bands: {df.loc[bad_bands, 'time_band'].unique()}"

    # 5. Features
    df["archive_date"] = pd.to_datetime(df["archive_date"])
    df["year_month"] = df["archive_date"].dt.strftime("%Y-%m")
    df["time_band"] = pd.Categorical(df["time_band"], categories=BAND_ORDER, ordered=True)
    df["is_long_wait"] = df["time_band"].isin(LONG_WAIT_BANDS)
    df["is_breach_proxy"] = df["time_band"].isin(BREACH_BANDS)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "waiting_lists_clean.csv", index=False)

    # 6. Power BI-ready extracts (star-schema style)
    dim_hospital = (df[["hospital_group", "hospital", "adult_child"]]
                    .drop_duplicates().reset_index(drop=True))
    dim_hospital.insert(0, "hospital_key", dim_hospital.index + 1)
    fact = df.merge(dim_hospital, on=["hospital_group", "hospital", "adult_child"])
    fact = fact[["archive_date", "year_month", "hospital_key", "specialty",
                 "case_type", "time_band", "waiting", "is_long_wait", "is_breach_proxy"]]
    dim_hospital.to_csv(PROCESSED / "powerbi_dim_hospital.csv", index=False)
    fact.to_csv(PROCESSED / "powerbi_fact_waiting.csv", index=False)

    print(f"Cleaned: {len(df):,} rows ({n_dupes} duplicates removed) -> {PROCESSED}/")


if __name__ == "__main__":
    main()
