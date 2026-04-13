-- =============================================================================
-- schema.sql — Healthcare Operations Reporting Automation
-- Author: Jomi Jose
-- =============================================================================

CREATE DATABASE IF NOT EXISTS healthcare_ops;
USE healthcare_ops;

CREATE TABLE IF NOT EXISTS patient_records (
    patient_id        VARCHAR(10) PRIMARY KEY,
    first_name        VARCHAR(50),
    last_name         VARCHAR(50),
    dob               DATE,
    age               INT,
    gender            VARCHAR(10),
    insurance         VARCHAR(5),
    preferred_channel VARCHAR(20),
    registration_date DATE,
    active            VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS appointment_logs (
    appointment_id    VARCHAR(10) PRIMARY KEY,
    patient_id        VARCHAR(10),
    specialty         VARCHAR(50),
    appointment_date  DATE,
    booking_date      DATE,
    lead_days         INT,
    status            VARCHAR(20),
    consultation_fee  DECIMAL(8,2),
    revenue           DECIMAL(8,2),
    follow_up_needed  VARCHAR(5),
    channel_used      VARCHAR(20),
    reminder_sent     VARCHAR(5),
    FOREIGN KEY (patient_id) REFERENCES patient_records(patient_id)
);

CREATE TABLE IF NOT EXISTS staff_performance (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    staff_id             VARCHAR(10),
    staff_name           VARCHAR(50),
    role                 VARCHAR(50),
    week_start           DATE,
    appointments_handled INT,
    sla_met_rate         DECIMAL(5,4),
    escalations          INT,
    followups_due        INT,
    followups_completed  INT,
    followup_rate        DECIMAL(5,4),
    avg_handle_time_min  DECIMAL(5,1)
);
