"""
export_to_sheets.py
-------------------
Exports weekly operational summaries to Google Sheets.
Three tabs: Weekly KPIs · Specialty Summary · Staff Performance

Author : Jomi Jose
Project: Healthcare Operations Reporting Automation
"""

import os
import pandas as pd
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

SCOPES     = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive.file"]
SHEET_NAME = "Healthcare Ops Weekly Report"


def load_summaries():
    weekly    = pd.read_csv("data/cleaned/weekly_summary.csv").tail(12)
    specialty = pd.read_csv("data/cleaned/specialty_summary.csv")
    staff     = pd.read_csv("data/cleaned/staff_summary.csv")
    return weekly, specialty, staff


def export_local(weekly, specialty, staff):
    os.makedirs("reports", exist_ok=True)
    weekly.to_csv("reports/weekly_kpis.csv",       index=False)
    specialty.to_csv("reports/specialty_summary.csv", index=False)
    staff.to_csv("reports/staff_summary.csv",      index=False)
    print("  ✓ Local CSV exports written to reports/")


def write_to_sheets(weekly, specialty, staff):
    if not GSPREAD_AVAILABLE:
        print("  ⚠ gspread not installed. Run: pip install gspread google-auth")
        return

    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    if not creds_path or not os.path.exists(creds_path):
        print("  ⚠ GOOGLE_CREDENTIALS_PATH not set. See README for setup.")
        return

    creds  = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)

    sheet_url = os.environ.get("GOOGLE_SHEET_URL")
    try:
        sh = client.open_by_url(sheet_url) if sheet_url else client.open(SHEET_NAME)
    except Exception:
        sh = client.create(SHEET_NAME)
        print(f"  ✓ Created new sheet: '{SHEET_NAME}'")

    def write_tab(sheet, tab_name, df):
        try:
            ws = sheet.worksheet(tab_name)
            ws.clear()
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(title=tab_name, rows=500, cols=20)
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        ws.update("A1", data)
        print(f"    ✓ Tab '{tab_name}' updated — {len(df)} rows")

    write_tab(sh, "Weekly KPIs",       weekly)
    write_tab(sh, "Specialty Summary", specialty)
    write_tab(sh, "Staff Performance", staff)
    print(f"\n  ✓ Google Sheets updated at {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    print("\n── Google Sheets Export ─────────────────────────────────────")
    weekly, specialty, staff = load_summaries()
    export_local(weekly, specialty, staff)
    write_to_sheets(weekly, specialty, staff)
    print()
