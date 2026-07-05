# Ireland's Hospital Waiting List Crisis — A Data Analysis

![Python](https://img.shields.io/badge/python-3.12-blue)
![SQL](https://img.shields.io/badge/SQL-DuckDB-yellow)
![Data](https://img.shields.io/badge/data-NTPF%20Open%20Data-green)

Over 700,000 people are on Ireland's public hospital waiting lists. This project
analyses the National Treatment Purchase Fund (NTPF) open data — published
monthly on [data.gov.ie](https://data.gov.ie) — to answer five questions that
matter to patients, hospital managers, and policymakers:

1. **Is the national list growing, and is it accelerating?**
2. **Which specialties drive the backlog — and which are the next problem?**
3. **What share of patients breach the Sláintecare wait-time target?**
4. **How unequal is access across hospital groups?**
5. **Is the long-wait tail (12+ months) actually improving?**

The headline finding: **totals are rising, but the story underneath is more
hopeful and more actionable** — the 12+ month tail is shrinking while
short-wait volume grows, meaning the crisis is now about demand outpacing
capacity, not about neglected long-waiters. Full narrative in
[`reports/insights_report.md`](reports/insights_report.md).

## Deliverables

| Deliverable | Where |
|---|---|
| Interactive dashboard (KPIs + 4 charts, self-contained HTML) | [`dashboard/index.html`](dashboard/index.html) |
| Executive insights report with recommendations | [`reports/insights_report.md`](reports/insights_report.md) |
| Publication-quality charts (matplotlib) | [`outputs/charts/`](outputs/charts) |
| SQL analysis (CTEs, window functions, conditional aggregation) | [`sql/analysis_queries.sql`](sql/analysis_queries.sql) |
| Power BI-ready extracts (fact + dimension) | `data/processed/powerbi_*.csv` |
| Reproducible pipeline: clean → analyse → visualise | [`src/`](src) |

## Methodology (CRISP-DM)

1. **Business understanding** — framed five stakeholder questions against
   Sláintecare maximum wait targets (10 weeks OPD / 12 weeks IPDC).
2. **Data understanding** — NTPF monthly snapshots by hospital group, hospital,
   specialty, adult/child, and wait-time band; stock not flow; statistical
   disclosure control applied at source.
3. **Data preparation** — whitespace and casing standardisation, duplicate
   removal, band validation, feature engineering (ordered band categories,
   long-wait and breach-proxy flags). See [`src/prepare_data.py`](src/prepare_data.py).
4. **Analysis** — trend decomposition, YoY growth, conditional shares,
   equity comparison across hospital groups. See [`src/analysis.py`](src/analysis.py).
5. **Evaluation** — limitations stated explicitly (snapshot vs flow, band
   granularity, disclosure control) rather than hidden.
6. **Deployment** — self-contained HTML dashboard suitable for GitHub Pages,
   plus star-schema CSV extracts ready to model in Power BI.

## Run it

```bash
pip install -r requirements.txt
python src/generate_sample_data.py   # sample data mirroring the NTPF schema
python src/prepare_data.py           # clean + feature engineering
python src/analysis.py               # KPIs, charts, insights.json
python src/build_dashboard.py        # interactive HTML dashboard
```

Then open `dashboard/index.html` in a browser. To analyse the **real national
data**, follow [`data/DOWNLOAD.md`](data/DOWNLOAD.md) — every script works
unchanged.

## Sample of the findings

| KPI | Value |
|---|---|
| Total waiting (latest month) | 79,370 |
| Year-on-year growth | +11.4% |
| Waiting beyond 3 months (Sláintecare breach proxy) | 65.4% |
| Waiting 12+ months | 13,907 (share down from 25.6% to 17.5%) |
| Equity gap between hospital groups | 10.4 percentage points |

*(Sample-data figures; the pipeline regenerates all of them from the real
extracts.)*

## Skills demonstrated

Data cleaning and validation · exploratory and diagnostic analysis · KPI design
against policy targets · SQL (CTEs, window functions, ranking, conditional
aggregation) · Python (pandas, matplotlib) · data storytelling and executive
reporting · dashboard development · dimensional extracts for Power BI ·
honest treatment of data limitations.

## Author

**Shabnam Sultana** — Data Management Analyst, Dublin ·
MSc Data Analytics (Dublin Business School) · DP-900 certified ·
[LinkedIn](https://www.linkedin.com/in/YOUR_PROFILE)
