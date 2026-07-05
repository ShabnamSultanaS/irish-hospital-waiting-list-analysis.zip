"""
Core analysis: KPIs, trends, and publication-quality charts.

Answers five business questions:
  Q1  How has the national waiting list evolved, and is it accelerating?
  Q2  Which specialties drive the backlog, and which are growing fastest?
  Q3  What share of patients breach the Slaintecare wait-time target?
  Q4  How much do hospital groups vary (equity of access)?
  Q5  Is the long-wait tail (12+ months) improving?

Outputs: outputs/charts/*.png, outputs/kpis.csv, outputs/insights.json
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

CLEAN = Path("data/processed/waiting_lists_clean.csv")
CHARTS = Path("outputs/charts")
OUT = Path("outputs")

plt.rcParams.update({
    "figure.facecolor": "white", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True,
    "grid.alpha": 0.25, "font.size": 11,
})
TEAL, CORAL, GRAY, PURPLE = "#0F6E56", "#D85A30", "#5F5E5A", "#534AB7"


def fmt_k(ax):
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))


def main() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CLEAN, parse_dates=["archive_date"])
    latest_month = df["year_month"].max()
    first_month = df["year_month"].min()
    latest = df[df["year_month"] == latest_month]
    insights: dict = {"latest_month": latest_month, "first_month": first_month}

    # ---------------- Q1: national trend ----------------
    trend = df.groupby("year_month")["waiting"].sum()
    total_now = int(trend.iloc[-1])
    total_start = int(trend.iloc[0])
    yoy = trend.iloc[-1] / trend.iloc[-13] - 1 if len(trend) > 12 else None
    insights["total_waiting_latest"] = total_now
    insights["growth_since_start_pct"] = round((total_now / total_start - 1) * 100, 1)
    insights["yoy_growth_pct"] = round(yoy * 100, 1) if yoy is not None else None

    fig, ax = plt.subplots(figsize=(10, 5))
    by_ct = df.pivot_table(index="year_month", columns="case_type",
                           values="waiting", aggfunc="sum")
    ax.stackplot(range(len(by_ct)), by_ct["OPD"], by_ct["IPDC"],
                 labels=["Outpatient (OPD)", "Inpatient/Day Case (IPDC)"],
                 colors=[TEAL, CORAL], alpha=0.85)
    ticks = range(0, len(by_ct), 6)
    ax.set_xticks(list(ticks))
    ax.set_xticklabels([by_ct.index[i] for i in ticks], rotation=0)
    fmt_k(ax)
    ax.legend(loc="upper left", frameon=False)
    ax.set_title("National hospital waiting list, monthly snapshots", loc="left", fontsize=13)
    fig.tight_layout()
    fig.savefig(CHARTS / "q1_national_trend.png", dpi=150)

    # ---------------- Q2: specialty drivers ----------------
    spec_now = latest.groupby("specialty")["waiting"].sum().sort_values(ascending=False)
    twelve_ago = df[df["year_month"] == sorted(df["year_month"].unique())[-13]]
    spec_prev = twelve_ago.groupby("specialty")["waiting"].sum()
    spec_growth = ((spec_now / spec_prev - 1) * 100).round(1)
    insights["top_specialty"] = spec_now.index[0]
    insights["top_specialty_waiting"] = int(spec_now.iloc[0])
    insights["fastest_growing_specialty"] = spec_growth.idxmax()
    insights["fastest_growing_pct"] = float(spec_growth.max())

    fig, ax = plt.subplots(figsize=(10, 6))
    top10 = spec_now.head(10)[::-1]
    colors = [CORAL if s == spec_growth.idxmax() else TEAL for s in top10.index]
    ax.barh(top10.index, top10.values, color=colors)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
    ax.set_title(f"Top 10 specialties by patients waiting ({latest_month})", loc="left", fontsize=13)
    fig.tight_layout()
    fig.savefig(CHARTS / "q2_specialty_backlog.png", dpi=150)

    # ---------------- Q3: Slaintecare breach proxy ----------------
    breach = df.groupby("year_month").apply(
        lambda g: g.loc[g["is_breach_proxy"], "waiting"].sum() / g["waiting"].sum(),
        include_groups=False) * 100
    insights["breach_rate_latest_pct"] = round(float(breach.iloc[-1]), 1)
    insights["breach_rate_start_pct"] = round(float(breach.iloc[0]), 1)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(range(len(breach)), breach.values, color=PURPLE, linewidth=2.2)
    ax.set_xticks(list(ticks))
    ax.set_xticklabels([breach.index[i] for i in ticks])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title("Share of patients waiting beyond 3 months\n(proxy for Slaintecare 10/12-week target breach)",
                 loc="left", fontsize=13)
    fig.tight_layout()
    fig.savefig(CHARTS / "q3_breach_rate.png", dpi=150)

    # ---------------- Q4: hospital group equity ----------------
    grp = latest.groupby("hospital_group").apply(
        lambda g: g.loc[g["is_long_wait"], "waiting"].sum() / g["waiting"].sum(),
        include_groups=False).sort_values() * 100
    insights["best_group_long_wait_pct"] = round(float(grp.iloc[0]), 1)
    insights["worst_group"] = grp.index[-1]
    insights["worst_group_long_wait_pct"] = round(float(grp.iloc[-1]), 1)
    insights["equity_gap_pp"] = round(float(grp.iloc[-1] - grp.iloc[0]), 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(grp.index, grp.values, color=[GRAY] * (len(grp) - 1) + [CORAL])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title(f"Patients waiting 12+ months, by hospital group ({latest_month})",
                 loc="left", fontsize=13)
    fig.tight_layout()
    fig.savefig(CHARTS / "q4_group_equity.png", dpi=150)

    # ---------------- Q5: long-wait tail ----------------
    tail = df.groupby("year_month").apply(
        lambda g: g.loc[g["is_long_wait"], "waiting"].sum(), include_groups=False)
    tail_pct = tail / trend * 100
    insights["long_wait_latest"] = int(tail.iloc[-1])
    insights["long_wait_share_start_pct"] = round(float(tail_pct.iloc[0]), 1)
    insights["long_wait_share_latest_pct"] = round(float(tail_pct.iloc[-1]), 1)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(range(len(tail)), tail.values, color=TEAL, alpha=0.4, label="12+ months (count)")
    ax2 = ax.twinx()
    ax2.plot(range(len(tail_pct)), tail_pct.values, color=CORAL, linewidth=2.2,
             label="12+ months (share)")
    ax.set_xticks(list(ticks))
    ax.set_xticklabels([tail.index[i] for i in ticks])
    fmt_k(ax)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.grid(False)
    ax.set_title("The long-wait tail: patients waiting 12+ months", loc="left", fontsize=13)
    fig.legend(loc="upper right", bbox_to_anchor=(0.98, 0.95), frameon=False)
    fig.tight_layout()
    fig.savefig(CHARTS / "q5_long_wait_tail.png", dpi=150)

    # ---------------- exports ----------------
    kpis = pd.DataFrame([
        ("Total waiting (latest)", f"{total_now:,}"),
        ("Growth since Jan 2023", f"{insights['growth_since_start_pct']}%"),
        ("Year-on-year growth", f"{insights['yoy_growth_pct']}%"),
        ("Waiting >3 months (breach proxy)", f"{insights['breach_rate_latest_pct']}%"),
        ("Waiting 12+ months", f"{insights['long_wait_latest']:,}"),
        ("Equity gap between hospital groups", f"{insights['equity_gap_pp']} pp"),
    ], columns=["kpi", "value"])
    kpis.to_csv(OUT / "kpis.csv", index=False)

    # monthly series for the dashboard
    insights["series"] = {
        "months": list(trend.index),
        "total": [int(x) for x in trend.values],
        "opd": [int(x) for x in by_ct["OPD"].values],
        "ipdc": [int(x) for x in by_ct["IPDC"].values],
        "breach_pct": [round(float(x), 1) for x in breach.values],
        "long_wait": [int(x) for x in tail.values],
        "top_specialties": {k: int(v) for k, v in spec_now.head(8).items()},
        "group_long_wait_pct": {k: round(float(v), 1) for k, v in grp.items()},
    }
    (OUT / "insights.json").write_text(json.dumps(insights, indent=2))
    print(kpis.to_string(index=False))
    print(f"\nCharts -> {CHARTS}/ | insights.json + kpis.csv -> {OUT}/")


if __name__ == "__main__":
    main()
