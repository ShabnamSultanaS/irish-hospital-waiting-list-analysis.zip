"""
Build an interactive, self-contained HTML dashboard from outputs/insights.json.

The result (dashboard/index.html) opens in any browser with no server —
data is embedded, charts render with Chart.js from a CDN. Enable GitHub
Pages on the repo to make it a live, shareable link for LinkedIn.
"""

import json
from pathlib import Path

data = json.loads(Path("outputs/insights.json").read_text())
s = data["series"]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ireland's Hospital Waiting Lists — Analysis Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
  :root {{ --teal:#0F6E56; --coral:#D85A30; --ink:#1c1c1a; --muted:#6b6a64; --bg:#faf9f5; --card:#ffffff; --line:#e6e4dc; }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif; background:var(--bg); color:var(--ink); padding:32px 20px 60px; }}
  .wrap {{ max-width:1080px; margin:0 auto; }}
  h1 {{ font-size:26px; font-weight:600; }}
  .sub {{ color:var(--muted); margin:6px 0 26px; font-size:14px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:14px; margin-bottom:26px; }}
  .kpi {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; }}
  .kpi .v {{ font-size:24px; font-weight:600; }}
  .kpi .l {{ font-size:12px; color:var(--muted); margin-top:4px; }}
  .kpi.bad .v {{ color:var(--coral); }}
  .kpi.good .v {{ color:var(--teal); }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:18px; }}
  .card h2 {{ font-size:15px; font-weight:600; margin-bottom:4px; }}
  .card p {{ font-size:12.5px; color:var(--muted); margin-bottom:12px; }}
  .full {{ grid-column:1 / -1; }}
  canvas {{ max-height:320px; }}
  .note {{ font-size:12px; color:var(--muted); margin-top:26px; line-height:1.6; }}
  @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Ireland's hospital waiting lists</h1>
  <p class="sub">NTPF open data analysis &middot; {data["first_month"]} to {data["latest_month"]} &middot; by Shabnam Sultana</p>

  <div class="kpis">
    <div class="kpi"><div class="v">{data["total_waiting_latest"]:,}</div><div class="l">Patients waiting ({data["latest_month"]})</div></div>
    <div class="kpi bad"><div class="v">+{data["yoy_growth_pct"]}%</div><div class="l">Year-on-year growth</div></div>
    <div class="kpi bad"><div class="v">{data["breach_rate_latest_pct"]}%</div><div class="l">Waiting beyond 3 months</div></div>
    <div class="kpi"><div class="v">{data["long_wait_latest"]:,}</div><div class="l">Waiting 12+ months</div></div>
    <div class="kpi good"><div class="v">{data["long_wait_share_start_pct"]}% &rarr; {data["long_wait_share_latest_pct"]}%</div><div class="l">Long-wait share, improving</div></div>
  </div>

  <div class="grid">
    <div class="card full">
      <h2>National waiting list over time</h2>
      <p>Total patients on outpatient and inpatient/day case lists, monthly snapshots.</p>
      <canvas id="trend"></canvas>
    </div>
    <div class="card">
      <h2>Top specialties by backlog</h2>
      <p>{data["top_specialty"]} leads with {data["top_specialty_waiting"]:,} waiting; {data["fastest_growing_specialty"]} is growing fastest (+{data["fastest_growing_pct"]}% YoY).</p>
      <canvas id="spec"></canvas>
    </div>
    <div class="card">
      <h2>Equity of access by hospital group</h2>
      <p>Share of patients waiting 12+ months — a {data["equity_gap_pp"]}pp gap between best and worst.</p>
      <canvas id="grp"></canvas>
    </div>
    <div class="card full">
      <h2>Beyond the Sl&aacute;intecare target</h2>
      <p>Share waiting more than 3 months (proxy for the 10/12-week Sl&aacute;intecare maximum wait targets).</p>
      <canvas id="breach"></canvas>
    </div>
  </div>

  <p class="note"><strong>Method notes:</strong> Built on the NTPF Open Data schema (data.gov.ie).
  The published data's finest time band is 0&ndash;3 months, so &ldquo;waiting &gt;3 months&rdquo; is used as a
  conservative proxy for Sl&aacute;intecare target breaches. Snapshot data measures stock, not flow &mdash;
  the NTPF does not publish removals/treatments. Full methodology, code, and SQL on GitHub.</p>
</div>

<script>
const S = {json.dumps(s)};
const teal = "#0F6E56", coral = "#D85A30", purple = "#534AB7", gray = "#B4B2A9";
Chart.defaults.font.size = 12;

new Chart(document.getElementById("trend"), {{
  type: "line",
  data: {{ labels: S.months, datasets: [
    {{ label: "Outpatient", data: S.opd, borderColor: teal, backgroundColor: "rgba(15,110,86,.15)", fill: true, pointRadius: 0, tension: .25 }},
    {{ label: "Inpatient/Day case", data: S.ipdc, borderColor: coral, backgroundColor: "rgba(216,90,48,.12)", fill: true, pointRadius: 0, tension: .25 }} ] }},
  options: {{ interaction: {{ mode: "index", intersect: false }}, scales: {{ x: {{ ticks: {{ maxTicksLimit: 8 }} }} }} }}
}});

new Chart(document.getElementById("spec"), {{
  type: "bar",
  data: {{ labels: Object.keys(S.top_specialties), datasets: [{{ data: Object.values(S.top_specialties), backgroundColor: teal }}] }},
  options: {{ indexAxis: "y", plugins: {{ legend: {{ display: false }} }} }}
}});

new Chart(document.getElementById("grp"), {{
  type: "bar",
  data: {{ labels: Object.keys(S.group_long_wait_pct), datasets: [{{ data: Object.values(S.group_long_wait_pct),
    backgroundColor: Object.values(S.group_long_wait_pct).map(v => v === Math.max(...Object.values(S.group_long_wait_pct)) ? coral : gray) }}] }},
  options: {{ indexAxis: "y", plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ ticks: {{ callback: v => v + "%" }} }} }} }}
}});

new Chart(document.getElementById("breach"), {{
  type: "line",
  data: {{ labels: S.months, datasets: [{{ data: S.breach_pct, borderColor: purple, pointRadius: 0, tension: .25 }}] }},
  options: {{ plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ ticks: {{ maxTicksLimit: 8 }} }}, y: {{ ticks: {{ callback: v => v + "%" }} }} }} }}
}});
</script>
</body>
</html>"""

Path("dashboard").mkdir(exist_ok=True)
Path("dashboard/index.html").write_text(html)
print("Dashboard built -> dashboard/index.html")
