# Healthcare Operations Reporting Automation

**Author:** Jomi Jose | Data & Operations Analyst  
**Stack:** Python · openpyxl · SQL · Google Sheets API · Pandas  
**Status:** Complete end-to-end pipeline

---

## Overview

An automated reporting pipeline for clinic operational data. Eliminates manual Excel-based workflows by generating formatted, multi-sheet Excel reports, running multi-source data reconciliation across CRM and operational systems, and exporting live weekly summaries to Google Sheets.

---

## Project Structure

```
healthcare-ops-reporting/
│
├── generate_data.py          # Generates raw operational datasets
├── clean_transform.py        # Cleans data, builds weekly/specialty/staff summaries
├── reconcile.py              # Multi-source reconciliation (CRM vs OPS)
├── generate_excel_report.py  # Formatted Excel report (4 sheets, conditional formatting)
├── export_to_sheets.py       # Google Sheets API export
├── run_pipeline.py           # Master runner
│
├── sql/
│   ├── schema.sql            # MySQL schema
│   └── queries.sql           # 7 operational SQL queries
│
├── data/
│   ├── patient_records.csv
│   ├── appointment_logs.csv
│   ├── staff_performance.csv
│   ├── crm_exports.csv       # Source A (with intentional discrepancies)
│   ├── operational_logs.csv  # Source B (ground truth)
│   └── cleaned/              # Clean outputs
│
├── excel_reports/
│   └── Healthcare_Ops_Weekly_Report.xlsx   # 4-sheet formatted report
│
├── reports/
│   ├── weekly_kpis.csv
│   ├── specialty_summary.csv
│   ├── staff_summary.csv
│   ├── reconciliation_report.csv   # All discrepancies flagged
│   └── reconciliation_summary.txt  # Plain text summary for management
│
└── requirements.txt
```

---

## Quickstart

```bash
git clone https://github.com/jomijose14/healthcare-ops-reporting.git
cd healthcare-ops-reporting
pip install -r requirements.txt
python run_pipeline.py
```

---

## Key Features

### 1. Automated Excel Report (`generate_excel_report.py`)
- 4 sheets: Weekly KPIs, Specialty Summary, Staff Performance, Follow-Up Actions
- Conditional formatting: colour scales on no-show rates, data bars on revenue, green/amber/red SLA ratings
- Embedded bar chart for weekly appointment volume
- Styled headers, alternating row colours, professional borders

### 2. Multi-Source Reconciliation (`reconcile.py`)
Compares CRM system exports against operational logs and flags:
- Status mismatches (CRM sync lag)
- Revenue discrepancies (rounding differences > AED 1)
- Scheduling conflicts (same patient, same day)
- Follow-up gaps (completed appointments with no reminder sent)

### 3. Google Sheets Live Export (`export_to_sheets.py`)
- Three tabs: Weekly KPIs, Specialty Summary, Staff Performance
- Graceful fallback to local CSV if credentials not configured
- Credentials loaded from environment variable (never hardcoded)

---

## Sample Reconciliation Output

```
============================================================
RECONCILIATION SUMMARY REPORT
============================================================
Total records compared   : 4,000
Total issues detected    : ~220

BREAKDOWN BY ISSUE TYPE:
  Follow-up gap                      : ~180
  Missing status in CRM              :  ~60
  Revenue discrepancy                :  ~40
  Scheduling conflict                :  ~10
============================================================
```

---

## Google Sheets Setup

```bash
export GOOGLE_CREDENTIALS_PATH=/path/to/service-account-key.json
export GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_ID/edit
python export_to_sheets.py
```

---

## Skills Demonstrated

| Skill | Where |
|-------|-------|
| Python (Pandas, NumPy) | All scripts |
| openpyxl Excel automation | `generate_excel_report.py` |
| Conditional formatting | `generate_excel_report.py` |
| Multi-source reconciliation | `reconcile.py` |
| SQL schema + queries | `sql/` |
| Google Sheets API | `export_to_sheets.py` |
| Data cleaning & transformation | `clean_transform.py` |
| Healthcare operations reporting | Full pipeline |

---

## Contact

**Jomi Jose** | Data & Operations Analyst | Dubai, UAE  
jomilibin10@gmail.com | [linkedin.com/in/jomijose](https://linkedin.com/in/jomijose)
