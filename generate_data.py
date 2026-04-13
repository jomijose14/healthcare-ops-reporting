"""
generate_data.py
----------------
Generates synthetic clinic operational data:
  - patient_records.csv      : patient demographics and registration
  - appointment_logs.csv     : appointment history with status
  - staff_performance.csv    : staff KPIs (SLA, escalations, throughput)
  - crm_exports.csv          : simulated CRM system export (separate source)
  - operational_logs.csv     : simulated ops system export (separate source)

The crm_exports and operational_logs are intentionally slightly different
to create reconciliation scenarios (the multi-source reconciliation task).

Author : Jomi Jose
Project: Healthcare Operations Reporting Automation
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(99)
np.random.seed(99)

N_PATIENTS     = 800
N_APPOINTMENTS = 4000
N_STAFF        = 20
OUTPUT_DIR     = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SPECIALTIES  = ["General Practice", "Cardiology", "Dermatology",
                 "Orthopedics", "Pediatrics", "Gynecology", "ENT"]
STATUSES     = ["Completed", "No-Show", "Cancelled", "Rescheduled"]
STATUS_WT    = [0.63, 0.17, 0.13, 0.07]
STAFF_ROLES  = ["Receptionist", "Nurse", "Patient Coordinator", "Admin Officer"]
CHANNELS     = ["SMS", "Email", "WhatsApp", "Phone"]
START        = datetime(2023, 6, 1)
END          = datetime(2024, 12, 31)


def rdate(s=START, e=END):
    return s + timedelta(days=random.randint(0, (e - s).days))


# ── 1. Patients ───────────────────────────────────────────────────────────────
def gen_patients():
    first = ["Ahmed","Sara","Ali","Fatima","John","Maria","Raj","Priya",
             "Omar","Aisha","James","Laila","David","Nour","Sanjay","Meera"]
    last  = ["Al Rashid","Khan","Sharma","Santos","Smith","Al Zaabi",
             "Nair","Hassan","Patel","Al Mansoori","Johnson","Pillai","Singh"]
    rows  = []
    for pid in range(1, N_PATIENTS + 1):
        dob = rdate(datetime(1950,1,1), datetime(2010,12,31))
        rows.append({
            "patient_id":        f"P{pid:04d}",
            "first_name":        random.choice(first),
            "last_name":         random.choice(last),
            "dob":               dob.strftime("%Y-%m-%d"),
            "age":               (datetime(2024,12,31)-dob).days//365,
            "gender":            random.choice(["Male","Female"]),
            "insurance":         random.choice(["Yes","Yes","No"]),
            "preferred_channel": random.choice(CHANNELS),
            "registration_date": rdate(datetime(2022,1,1),datetime(2024,1,1)).strftime("%Y-%m-%d"),
            "active":            random.choice(["Yes","Yes","Yes","No"]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT_DIR}/patient_records.csv", index=False)
    print(f"  patient_records.csv      — {len(df):,} rows")
    return df


# ── 2. Appointment logs ───────────────────────────────────────────────────────
def gen_appointments(patients):
    pids = patients["patient_id"].tolist()
    rows = []
    for aid in range(1, N_APPOINTMENTS + 1):
        pid       = random.choice(pids)
        spec      = random.choice(SPECIALTIES)
        appt_dt   = rdate()
        book_dt   = appt_dt - timedelta(days=random.randint(1, 30))
        lead_days = (appt_dt - book_dt).days
        status    = random.choices(STATUSES, weights=STATUS_WT)[0]
        ins       = patients.loc[patients["patient_id"]==pid,"insurance"].values[0]
        if lead_days > 18 and ins == "No" and random.random() < 0.22:
            status = "No-Show"
        fee = {"General Practice":150,"Cardiology":400,"Dermatology":250,
               "Orthopedics":350,"Pediatrics":200,"Gynecology":300,"ENT":220}[spec]
        rows.append({
            "appointment_id":   f"A{aid:05d}",
            "patient_id":       pid,
            "specialty":        spec,
            "appointment_date": appt_dt.strftime("%Y-%m-%d"),
            "booking_date":     book_dt.strftime("%Y-%m-%d"),
            "lead_days":        lead_days,
            "status":           status,
            "consultation_fee": fee,
            "revenue":          fee if status=="Completed" else 0,
            "follow_up_needed": random.choice(["Yes","No"]),
            "channel_used":     random.choice(CHANNELS),
            "reminder_sent":    random.choice(["Yes","Yes","No"]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT_DIR}/appointment_logs.csv", index=False)
    print(f"  appointment_logs.csv     — {len(df):,} rows")
    return df


# ── 3. Staff performance ──────────────────────────────────────────────────────
def gen_staff(appts):
    appts["appointment_date"] = pd.to_datetime(appts["appointment_date"])
    weeks = pd.date_range(START, END, freq="W-MON")
    rows  = []
    for sid in range(1, N_STAFF + 1):
        role = random.choice(STAFF_ROLES)
        name = f"Staff_{sid:02d}"
        for wk in weeks:
            appts_handled = random.randint(40, 120)
            sla_met       = random.uniform(0.78, 0.99)
            escalations   = random.randint(0, 5)
            followups_due = random.randint(5, 25)
            followups_done= int(followups_due * random.uniform(0.6, 1.0))
            rows.append({
                "staff_id":           f"S{sid:03d}",
                "staff_name":         name,
                "role":               role,
                "week_start":         wk.strftime("%Y-%m-%d"),
                "appointments_handled": appts_handled,
                "sla_met_rate":       round(sla_met, 4),
                "escalations":        escalations,
                "followups_due":      followups_due,
                "followups_completed": followups_done,
                "followup_rate":      round(followups_done/followups_due, 4),
                "avg_handle_time_min": round(random.uniform(8, 20), 1),
            })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT_DIR}/staff_performance.csv", index=False)
    print(f"  staff_performance.csv    — {len(df):,} rows")
    return df


# ── 4. CRM export (source A) ──────────────────────────────────────────────────
def gen_crm_export(appts):
    """Simulates a CRM system export — slightly different from ops log."""
    df = appts[["appointment_id","patient_id","specialty",
                "appointment_date","status","revenue"]].copy()
    df["source"] = "CRM"
    # Introduce 3% missing statuses (CRM sync lag)
    mask = np.random.random(len(df)) < 0.03
    df.loc[mask, "status"] = np.nan
    # Introduce 2% revenue discrepancies (rounding differences)
    mask2 = np.random.random(len(df)) < 0.02
    df.loc[mask2, "revenue"] = df.loc[mask2, "revenue"] + random.choice([5, -5, 10])
    df.to_csv(f"{OUTPUT_DIR}/crm_exports.csv", index=False)
    print(f"  crm_exports.csv          — {len(df):,} rows  (with intentional discrepancies)")
    return df


# ── 5. Operational log (source B) ─────────────────────────────────────────────
def gen_ops_log(appts):
    """Simulates an operational system log — ground truth."""
    df = appts[["appointment_id","patient_id","specialty",
                "appointment_date","status","revenue","follow_up_needed"]].copy()
    df["source"] = "OPS"
    df.to_csv(f"{OUTPUT_DIR}/operational_logs.csv", index=False)
    print(f"  operational_logs.csv     — {len(df):,} rows  (ground truth)")
    return df


if __name__ == "__main__":
    print("\n── Generating healthcare operational data ──")
    p  = gen_patients()
    a  = gen_appointments(p)
    gen_staff(a)
    gen_crm_export(a)
    gen_ops_log(a)
    print(f"\nAll files written to /{OUTPUT_DIR}/\n")
