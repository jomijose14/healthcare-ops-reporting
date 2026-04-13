"""
reconcile.py
------------
Multi-source reconciliation workflow.

Compares two data sources:
  Source A: crm_exports.csv     (CRM system — may have sync lag / rounding)
  Source B: operational_logs.csv (Ops system — ground truth)

Detects:
  1. Status mismatches   — CRM shows different status than Ops
  2. Revenue discrepancies — CRM revenue differs from Ops by more than AED 1
  3. Missing in CRM      — appointments in Ops but missing/null in CRM
  4. Follow-up gaps      — completed appointments with no follow-up flag
  5. Scheduling conflicts — patient has two appointments on the same day

Outputs:
  reports/reconciliation_report.csv  — full discrepancy log
  reports/reconciliation_summary.txt — plain text summary for management

Author : Jomi Jose
Project: Healthcare Operations Reporting Automation
"""

import pandas as pd
import numpy as np
import os

os.makedirs("reports", exist_ok=True)


def load():
    crm  = pd.read_csv("data/crm_exports.csv")
    ops  = pd.read_csv("data/operational_logs.csv")
    appts= pd.read_csv("data/cleaned/appointments_clean.csv",
                       parse_dates=["appointment_date"])
    print(f"  CRM records : {len(crm):,}")
    print(f"  OPS records : {len(ops):,}")
    return crm, ops, appts


# ── 1. Status mismatches ──────────────────────────────────────────────────────
def check_status_mismatches(crm, ops):
    merged = ops[["appointment_id","status","revenue"]].merge(
        crm[["appointment_id","status","revenue"]].rename(
            columns={"status":"crm_status","revenue":"crm_revenue"}),
        on="appointment_id", how="left"
    )
    # Missing status in CRM (sync lag)
    missing_status = merged[merged["crm_status"].isna()].copy()
    missing_status["issue_type"] = "Missing status in CRM"
    missing_status["detail"]     = "CRM has no status — possible sync lag"

    # Status mismatch
    mismatch = merged[
        merged["crm_status"].notna() &
        (merged["status"] != merged["crm_status"])
    ].copy()
    mismatch["issue_type"] = "Status mismatch"
    mismatch["detail"]     = mismatch.apply(
        lambda r: f"OPS: {r['status']} | CRM: {r['crm_status']}", axis=1)

    return missing_status, mismatch


# ── 2. Revenue discrepancies ──────────────────────────────────────────────────
def check_revenue(crm, ops):
    merged = ops[["appointment_id","revenue"]].merge(
        crm[["appointment_id","revenue"]].rename(columns={"revenue":"crm_revenue"}),
        on="appointment_id", how="left"
    )
    discrepancies = merged[
        merged["crm_revenue"].notna() &
        (abs(merged["revenue"] - merged["crm_revenue"]) > 1)
    ].copy()
    discrepancies["issue_type"] = "Revenue discrepancy"
    discrepancies["detail"]     = discrepancies.apply(
        lambda r: f"OPS: AED {r['revenue']:.0f} | CRM: AED {r['crm_revenue']:.0f} "
                  f"(diff: AED {abs(r['revenue']-r['crm_revenue']):.0f})", axis=1)
    return discrepancies


# ── 3. Scheduling conflicts ───────────────────────────────────────────────────
def check_scheduling_conflicts(appts):
    completed = appts[appts["status"]=="Completed"]
    dupes = completed.groupby(["patient_id","appointment_date"]).filter(
        lambda x: len(x) > 1
    )[["appointment_id","patient_id","appointment_date","specialty"]].copy()
    dupes["issue_type"] = "Scheduling conflict"
    dupes["detail"]     = "Patient has 2+ completed appointments on same day"
    return dupes


# ── 4. Follow-up gaps ─────────────────────────────────────────────────────────
def check_followup_gaps(appts):
    gaps = appts[
        (appts["follow_up_needed"]=="Yes") &
        (appts["status"]=="Completed") &
        (appts["reminder_sent"]=="No")
    ][["appointment_id","patient_id","specialty","appointment_date"]].copy()
    gaps["issue_type"] = "Follow-up gap"
    gaps["detail"]     = "Follow-up required but no reminder sent"
    return gaps


# ── Build reconciliation report ───────────────────────────────────────────────
def build_report(crm, ops, appts):
    print("\n── Running reconciliation checks ────────────────────────────")
    miss_status, status_mm = check_status_mismatches(crm, ops)
    revenue_disc           = check_revenue(crm, ops)
    conflicts              = check_scheduling_conflicts(appts)
    followup_gaps          = check_followup_gaps(appts)

    # Consolidate
    frames = []
    for df, label in [
        (miss_status,  "Missing CRM status"),
        (status_mm,    "Status mismatch"),
        (revenue_disc, "Revenue discrepancy"),
        (conflicts,    "Scheduling conflict"),
        (followup_gaps,"Follow-up gap"),
    ]:
        if len(df) > 0:
            sub = df[["appointment_id","issue_type","detail"]].copy()
            frames.append(sub)
            print(f"  {label:30s}: {len(df):>4} issues")

    report = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    # Save full report
    report.to_csv("reports/reconciliation_report.csv", index=False)

    # Summary text
    summary_lines = [
        "=" * 60,
        "RECONCILIATION SUMMARY REPORT",
        "Healthcare Operations Reporting Automation",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        f"Total records compared   : {len(ops):,}",
        f"Total issues detected    : {len(report):,}",
        "",
        "BREAKDOWN BY ISSUE TYPE:",
    ]
    if len(report):
        for issue, count in report["issue_type"].value_counts().items():
            pct = count / len(report) * 100
            summary_lines.append(f"  {issue:35s}: {count:4d} ({pct:.1f}%)")

    summary_lines += [
        "",
        "RECOMMENDATIONS:",
        "  1. Investigate CRM sync lag for missing status records",
        "  2. Review revenue rounding rules between CRM and OPS systems",
        "  3. Contact patients with scheduling conflicts to reschedule",
        "  4. Assign follow-up calls for all flagged gap appointments",
        "",
        "Full details: reports/reconciliation_report.csv",
        "=" * 60,
    ]
    txt = "\n".join(summary_lines)
    with open("reports/reconciliation_summary.txt", "w") as f:
        f.write(txt)
    print(f"\n  ✓ reports/reconciliation_report.csv ({len(report):,} issues)")
    print(f"  ✓ reports/reconciliation_summary.txt")
    print(f"\n{txt}\n")
    return report


if __name__ == "__main__":
    print("\n── Multi-Source Reconciliation Pipeline ─────────────────────")
    crm, ops, appts = load()
    build_report(crm, ops, appts)
