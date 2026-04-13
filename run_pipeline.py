"""
run_pipeline.py
---------------
Runs the full Healthcare Operations Reporting pipeline in order:
  1. generate_data.py         — synthetic raw data
  2. clean_transform.py       — clean, build summaries
  3. reconcile.py             — multi-source reconciliation
  4. generate_excel_report.py — formatted Excel report
  5. export_to_sheets.py      — Google Sheets + local CSV

Author : Jomi Jose
"""

import subprocess, sys, time

STEPS = [
    ("generate_data.py",         "Step 1: Generate synthetic data"),
    ("clean_transform.py",       "Step 2: Clean & transform"),
    ("reconcile.py",             "Step 3: Multi-source reconciliation"),
    ("generate_excel_report.py", "Step 4: Generate Excel report"),
    ("export_to_sheets.py",      "Step 5: Export to Google Sheets"),
]

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Healthcare Operations Reporting — Full Pipeline")
    print("  Author: Jomi Jose")
    print("="*60)

    t0 = time.time()
    for script, label in STEPS:
        print(f"\n── {label} {'─'*(48-len(label))}")
        res = subprocess.run([sys.executable, script])
        if res.returncode != 0:
            print(f"\n  ✗ {script} failed. Stopping.")
            sys.exit(res.returncode)

    print(f"\n{'='*60}")
    print(f"  ✓ Pipeline complete in {time.time()-t0:.1f}s")
    print(f"  Excel report  : excel_reports/Healthcare_Ops_Weekly_Report.xlsx")
    print(f"  Recon report  : reports/reconciliation_report.csv")
    print(f"  CSV summaries : reports/")
    print("="*60 + "\n")
