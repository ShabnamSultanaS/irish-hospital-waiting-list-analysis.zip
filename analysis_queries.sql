-- ============================================================
-- NTPF Waiting List Analysis — SQL portfolio queries (DuckDB)
-- Run:  duckdb -c ".read sql/analysis_queries.sql"  (from repo root)
-- Demonstrates: CTEs, window functions, conditional aggregation,
-- ranking, and period-over-period comparisons.
-- ============================================================

CREATE OR REPLACE TABLE wl AS
SELECT * FROM read_csv_auto('data/processed/waiting_lists_clean.csv');

-- Q1. National monthly trend with month-over-month and YoY change
WITH monthly AS (
    SELECT year_month, sum(waiting) AS total_waiting
    FROM wl GROUP BY year_month
)
SELECT
    year_month,
    total_waiting,
    total_waiting - lag(total_waiting) OVER (ORDER BY year_month)      AS mom_change,
    round(100.0 * (total_waiting - lag(total_waiting, 12) OVER (ORDER BY year_month))
        / lag(total_waiting, 12) OVER (ORDER BY year_month), 1)        AS yoy_pct
FROM monthly
ORDER BY year_month;

-- Q2. Specialty league table: volume rank vs growth rank (latest vs 12 months prior)
WITH bounds AS (
    SELECT max(year_month) AS latest FROM wl
),
by_spec AS (
    SELECT
        specialty,
        sum(waiting) FILTER (WHERE year_month = (SELECT latest FROM bounds))  AS now_waiting,
        sum(waiting) FILTER (WHERE year_month =
            strftime(date_trunc('month', strptime((SELECT latest FROM bounds), '%Y-%m'))
                     - INTERVAL 12 MONTH, '%Y-%m'))                            AS prior_waiting
    FROM wl GROUP BY specialty
)
SELECT
    specialty,
    now_waiting,
    round(100.0 * (now_waiting - prior_waiting) / prior_waiting, 1)  AS yoy_growth_pct,
    rank() OVER (ORDER BY now_waiting DESC)                          AS volume_rank,
    rank() OVER (ORDER BY (now_waiting - prior_waiting)
                 / prior_waiting DESC)                               AS growth_rank
FROM by_spec
ORDER BY volume_rank;

-- Q3. Slaintecare breach proxy (>3 months) by case type, latest month
SELECT
    case_type,
    sum(waiting)                                                     AS total,
    sum(waiting) FILTER (WHERE is_breach_proxy)                      AS beyond_3m,
    round(100.0 * sum(waiting) FILTER (WHERE is_breach_proxy)
        / sum(waiting), 1)                                           AS breach_pct
FROM wl
WHERE year_month = (SELECT max(year_month) FROM wl)
GROUP BY case_type;

-- Q4. Hospital-level hotspots: top 10 hospitals by 12+ month waiters
SELECT
    hospital_group,
    hospital,
    sum(waiting) FILTER (WHERE is_long_wait)                         AS waiting_12m_plus,
    round(100.0 * sum(waiting) FILTER (WHERE is_long_wait)
        / sum(waiting), 1)                                           AS long_wait_share_pct
FROM wl
WHERE year_month = (SELECT max(year_month) FROM wl)
GROUP BY hospital_group, hospital
ORDER BY waiting_12m_plus DESC
LIMIT 10;

-- Q5. Adult vs Child comparison over the last 12 months
SELECT
    adult_child,
    year_month,
    sum(waiting) AS waiting,
    round(avg(sum(waiting)) OVER (PARTITION BY adult_child
        ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0)
        AS waiting_3mo_moving_avg
FROM wl
WHERE year_month >= strftime(current_date - INTERVAL 12 MONTH, '%Y-%m')
GROUP BY adult_child, year_month
ORDER BY adult_child, year_month;
