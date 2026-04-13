-- =============================================================================
-- queries.sql — Healthcare Operations Reporting Automation
-- Author: Jomi Jose
-- =============================================================================

USE healthcare_ops;

-- Q1. Weekly KPI summary (last 12 weeks)
SELECT
    YEARWEEK(appointment_date, 1)          AS year_week,
    MIN(appointment_date)                  AS week_start,
    COUNT(*)                               AS total_appts,
    SUM(status = 'Completed')              AS completed,
    SUM(status = 'No-Show')                AS no_shows,
    ROUND(AVG(status = 'No-Show') * 100,1) AS no_show_rate_pct,
    ROUND(SUM(revenue), 0)                 AS revenue_aed
FROM appointment_logs
GROUP BY YEARWEEK(appointment_date, 1)
ORDER BY year_week DESC
LIMIT 12;


-- Q2. Specialty performance
SELECT
    specialty,
    COUNT(*)                               AS total_appts,
    SUM(status = 'Completed')              AS completed,
    SUM(status = 'No-Show')                AS no_shows,
    ROUND(AVG(status = 'No-Show') * 100,1) AS no_show_rate_pct,
    ROUND(SUM(revenue), 0)                 AS total_revenue_aed,
    ROUND(AVG(consultation_fee), 0)        AS avg_fee_aed
FROM appointment_logs
GROUP BY specialty
ORDER BY total_revenue_aed DESC;


-- Q3. Staff SLA league table (top 10)
SELECT
    staff_id,
    staff_name,
    role,
    SUM(appointments_handled)              AS total_handled,
    ROUND(AVG(sla_met_rate) * 100, 1)     AS avg_sla_pct,
    SUM(escalations)                       AS total_escalations,
    ROUND(AVG(followup_rate) * 100, 1)    AS avg_followup_pct
FROM staff_performance
GROUP BY staff_id, staff_name, role
ORDER BY avg_sla_pct DESC
LIMIT 10;


-- Q4. Follow-up gaps — completed appointments with no reminder
SELECT
    a.appointment_id,
    a.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.preferred_channel,
    a.specialty,
    a.appointment_date,
    DATEDIFF(CURDATE(), a.appointment_date) AS days_since
FROM appointment_logs a
JOIN patient_records p ON a.patient_id = p.patient_id
WHERE a.follow_up_needed = 'Yes'
  AND a.status           = 'Completed'
  AND a.reminder_sent    = 'No'
ORDER BY days_since DESC
LIMIT 50;


-- Q5. No-show rate by lead-time bucket
SELECT
    CASE
        WHEN lead_days <= 3  THEN 'Same-week'
        WHEN lead_days <= 7  THEN '1 week'
        WHEN lead_days <= 14 THEN '2 weeks'
        WHEN lead_days <= 30 THEN '1 month'
        ELSE '30+ days'
    END                                     AS lead_bucket,
    COUNT(*)                                AS total_appts,
    SUM(status = 'No-Show')                 AS no_shows,
    ROUND(AVG(status = 'No-Show') * 100, 1) AS no_show_rate_pct
FROM appointment_logs
GROUP BY lead_bucket
ORDER BY no_show_rate_pct DESC;


-- Q6. Monthly revenue trend
SELECT
    YEAR(appointment_date)                  AS year,
    MONTH(appointment_date)                 AS month,
    DATE_FORMAT(appointment_date, '%b %Y')  AS period,
    COUNT(*)                                AS total_appts,
    ROUND(SUM(revenue), 0)                  AS revenue_aed
FROM appointment_logs
GROUP BY year, month, period
ORDER BY year, month;


-- Q7. Patients with multiple no-shows (retention risk)
SELECT
    patient_id,
    COUNT(*)                                AS total_noshows,
    MAX(appointment_date)                   AS last_noshow_date
FROM appointment_logs
WHERE status = 'No-Show'
GROUP BY patient_id
HAVING total_noshows >= 2
ORDER BY total_noshows DESC;
