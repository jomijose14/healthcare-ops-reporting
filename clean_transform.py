"""
clean_transform.py
------------------
Cleans and transforms all raw operational datasets.
Produces a clean master dataset and weekly summary tables
ready for Excel reporting and Google Sheets export.

Author : Jomi Jose
Project: Healthcare Operations Reporting Automation
"""

import pandas as pd
import numpy as np
import os

RAW   = "data"
CLEAN = "data/cleaned"
os.makedirs(CLEAN, exist_ok=True)


def load():
    patients = pd.read_csv(f"{RAW}/patient_records.csv")
    appts    = pd.read_csv(f"{RAW}/appointment_logs.csv")
    staff    = pd.read_csv(f"{RAW}/staff_performance.csv")
    crm      = pd.read_csv(f"{RAW}/crm_exports.csv")
    ops      = pd.read_csv(f"{RAW}/operational_logs.csv")
    print(f"  Loaded: patients={len(patients):,}  appts={len(appts):,}  "
          f"staff={len(staff):,}  crm={len(crm):,}  ops={len(ops):,}")
    return patients, appts, staff, crm, ops


# ── Clean patients ────────────────────────────────────────────────────────────
def clean_patients(df):
    df["registration_date"] = pd.to_datetime(df["registration_date"])
    df["dob"]               = pd.to_datetime(df["dob"])
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.title()
    df = df.drop_duplicates("patient_id")
    df["age"] = df["age"].clip(0, 110)
    print(f"  patients cleaned: {len(df):,} records")
    return df


# ── Clean appointments ────────────────────────────────────────────────────────
def clean_appointments(df):
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    df["booking_date"]     = pd.to_datetime(df["booking_date"])
    df = df.drop_duplicates("appointment_id")
    df["lead_days"]  = df["lead_days"].clip(lower=0)
    df["revenue"]    = np.where(df["status"]=="Completed", df["consultation_fee"], 0)
    df["month"]      = df["appointment_date"].dt.month
    df["month_name"] = df["appointment_date"].dt.strftime("%b")
    df["year"]       = df["appointment_date"].dt.year
    df["week"]       = df["appointment_date"].dt.to_period("W").astype(str)
    df["quarter"]    = df["appointment_date"].dt.quarter
    df["day_of_week"]= df["appointment_date"].dt.day_name()
    df["is_no_show"] = (df["status"]=="No-Show").astype(int)
    df["is_completed"]=(df["status"]=="Completed").astype(int)
    df["lead_bucket"]= pd.cut(df["lead_days"],
                              bins=[0,3,7,14,30,999],
                              labels=["Same-week","1 week","2 weeks","1 month","30+ days"])
    print(f"  appointments cleaned: {len(df):,} records, {df.shape[1]} columns")
    return df


# ── Clean staff ───────────────────────────────────────────────────────────────
def clean_staff(df):
    df["week_start"] = pd.to_datetime(df["week_start"])
    df["month"]      = df["week_start"].dt.month
    df["month_name"] = df["week_start"].dt.strftime("%b")
    df["year"]       = df["week_start"].dt.year
    df["sla_met_pct"]= (df["sla_met_rate"] * 100).round(1)
    df["followup_pct"]=(df["followup_rate"] * 100).round(1)
    print(f"  staff cleaned: {len(df):,} records")
    return df


# ── Weekly summaries ──────────────────────────────────────────────────────────
def build_weekly_summary(appts):
    weekly = (
        appts.groupby(["year","week"])
        .agg(
            total_appts    =("appointment_id","count"),
            completed      =("is_completed","sum"),
            no_shows       =("is_no_show","sum"),
            revenue_aed    =("revenue","sum"),
            avg_lead_days  =("lead_days","mean"),
        )
        .reset_index()
    )
    weekly["no_show_rate"] = (weekly["no_shows"]/weekly["total_appts"]*100).round(1)
    weekly["completion_rate"]=(weekly["completed"]/weekly["total_appts"]*100).round(1)
    weekly["revenue_aed"]  = weekly["revenue_aed"].round(0).astype(int)
    weekly["avg_lead_days"]= weekly["avg_lead_days"].round(1)
    print(f"  weekly summary: {len(weekly):,} weeks")
    return weekly


def build_specialty_summary(appts):
    spec = (
        appts.groupby("specialty")
        .agg(
            total_appts   =("appointment_id","count"),
            completed     =("is_completed","sum"),
            no_shows      =("is_no_show","sum"),
            total_revenue =("revenue","sum"),
            avg_fee       =("consultation_fee","mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )
    spec["no_show_rate"]   =(spec["no_shows"]/spec["total_appts"]*100).round(1)
    spec["total_revenue"]  = spec["total_revenue"].round(0).astype(int)
    spec["avg_fee"]        = spec["avg_fee"].round(0).astype(int)
    return spec


def build_staff_summary(staff):
    summary = (
        staff.groupby(["staff_id","staff_name","role"])
        .agg(
            total_appts_handled=("appointments_handled","sum"),
            avg_sla_pct        =("sla_met_pct","mean"),
            total_escalations  =("escalations","sum"),
            avg_followup_pct   =("followup_pct","mean"),
            avg_handle_min     =("avg_handle_time_min","mean"),
        )
        .reset_index()
    )
    summary["avg_sla_pct"]     = summary["avg_sla_pct"].round(1)
    summary["avg_followup_pct"]= summary["avg_followup_pct"].round(1)
    summary["avg_handle_min"]  = summary["avg_handle_min"].round(1)
    return summary.sort_values("avg_sla_pct", ascending=False)


# ── Export ────────────────────────────────────────────────────────────────────
def export(patients, appts, staff, weekly, specialty, staff_sum):
    patients.to_csv(f"{CLEAN}/patients_clean.csv",   index=False)
    appts.to_csv(f"{CLEAN}/appointments_clean.csv",  index=False)
    staff.to_csv(f"{CLEAN}/staff_clean.csv",         index=False)
    weekly.to_csv(f"{CLEAN}/weekly_summary.csv",     index=False)
    specialty.to_csv(f"{CLEAN}/specialty_summary.csv",index=False)
    staff_sum.to_csv(f"{CLEAN}/staff_summary.csv",   index=False)
    print(f"  All clean files written to {CLEAN}/")


if __name__ == "__main__":
    print("\n── Step 1: Load ─────────────────────────────────────────────")
    patients, appts, staff, crm, ops = load()

    print("\n── Step 2: Clean ────────────────────────────────────────────")
    patients = clean_patients(patients)
    appts    = clean_appointments(appts)
    staff    = clean_staff(staff)

    print("\n── Step 3: Build summaries ──────────────────────────────────")
    weekly    = build_weekly_summary(appts)
    specialty = build_specialty_summary(appts)
    staff_sum = build_staff_summary(staff)

    print("\n── Step 4: Export ───────────────────────────────────────────")
    export(patients, appts, staff, weekly, specialty, staff_sum)

    print(f"\n── Quality snapshot ─────────────────────────────────────────")
    print(f"  Total appointments : {len(appts):,}")
    print(f"  No-show rate       : {appts['is_no_show'].mean():.1%}")
    print(f"  Total revenue      : AED {appts['revenue'].sum():,.0f}")
    print(f"  Date range         : {appts['appointment_date'].min().date()} "
          f"→ {appts['appointment_date'].max().date()}")
    print()
