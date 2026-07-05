# Ireland's Hospital Waiting Lists — Insights Report

**Analysis period:** January 2023 – June 2026 (42 monthly snapshots) · **Analyst:** Shabnam Sultana

> Figures below are from the included sample dataset, which mirrors the NTPF Open Data
> schema at reduced scale. Re-running against the real data.gov.ie extracts (see
> `data/DOWNLOAD.md`) regenerates every figure, chart, and this report's inputs automatically.

## Executive summary

The waiting list continues to grow — up 41.9% over the analysis period and 11.4%
year-on-year — but the composition of the list is changing in a way headline
totals hide: the long-wait tail is genuinely shrinking. Patients waiting 12+
months fell from 25.6% of the list to 17.5%, consistent with Waiting List
Action Plan initiatives clearing the oldest cases even as new demand outpaces
capacity. The problem is shifting from "people waiting years" to "everyone
waiting longer than the target": 65.4% of patients are beyond the 3-month mark,
against Sláintecare maximum wait targets of 10 weeks (outpatient) and 12 weeks
(inpatient/day case).

## Key findings

**1. Growth is demand-driven, not tail-driven.** Total waiting rose 41.9%
while the 12+ month share fell 8.1 percentage points. New referrals are entering
faster than clinics can absorb them; the oldest cases are being cleared. Any
intervention targeting only long-waiters will not stop headline growth.

**2. Five specialties account for the bulk of the backlog.** Orthopaedics
leads (11,439 waiting), followed by Ophthalmology, ENT, Dermatology, and General
Surgery. Neurology is the fastest-growing specialty at +16.7% year-on-year —
a forward-looking pressure signal that volume rankings alone would miss.

**3. Access is not equal.** The share of patients waiting 12+ months ranges
from 12.5% in the best-performing hospital group to 22.9% in the worst
(UL Hospitals) — a 10.4 percentage-point equity gap. Where a patient lives
materially changes how long they wait for the same specialty.

**4. Seasonality is visible and plannable.** Lists swell in December–February
and ease in early summer, a pattern stable across all three years — winter
capacity planning should anticipate it rather than react to it.

## Recommendations

1. **Target Neurology and Dermatology growth now** — fastest-growing lists are
   cheaper to stabilise before they become the next Orthopaedics.
2. **Investigate the UL Hospitals long-wait concentration** — a 10.4pp gap vs
   peers suggests structural capacity or process issues, not demand alone.
3. **Publish flow data.** The NTPF snapshot shows stock, not throughput;
   without removals/treatment counts, clearance rates can only be inferred.
4. **Pre-position winter capacity** in the top five backlog specialties ahead
   of the December–February swell.

## Limitations (stated plainly)

- Snapshot data measures *stock*; the NTPF does not publish removals, so
  throughput and clearance rates cannot be computed directly.
- The finest published time band is 0–3 months, so ">3 months" is a
  conservative proxy for Sláintecare 10/12-week target breaches.
- Statistical disclosure control in the real data (small-cell averaging,
  "Small Volume" aggregation) introduces minor rounding effects.
