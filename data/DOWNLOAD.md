# Using the real NTPF data

This project runs out-of-the-box on the included sample data (same schema,
smaller scale). To run it on the real national data:

1. Go to data.gov.ie and search "NTPF" — or browse:
   - Outpatient Waiting List: https://data.gov.ie/dataset (search: outpatient waiting list)
   - Inpatient/Day Case Waiting List: https://data.gov.ie/dataset/inpatient-day-case-waiting-list
2. Download the monthly CSVs for the period you want to analyse.
3. Combine them into a single CSV with these columns (rename to match):
   archive_date, hospital_group, hospital, specialty, adult_child,
   case_type, time_band, waiting
4. Save as data/sample/ntpf_waiting_lists.csv
5. Run: python src/prepare_data.py && python src/analysis.py && python src/build_dashboard.py

Notes on the real data:
- OPD and IPDC come as separate files; add a case_type column when combining.
- Cells with <5 patients are averaged (statistical disclosure control).
- Specialties with <20 waiting are grouped under "Small Volume".
