import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = (
    BASE_DIR / "data" / "processed"
)

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. INPUT FILE
# ============================================================

OPERATIONS_FILE = (
    PROCESSED_DATA_DIR /
    "operations_processed.csv"
)


# ============================================================
# 3. LOAD PROCESSED DATA
# ============================================================

print("\n" + "=" * 60)
print("LOADING PROCESSED OPERATIONS DATA")
print("=" * 60)

operations = pd.read_csv(
    OPERATIONS_FILE
)

print(
    f"\nRows loaded: {operations.shape[0]}"
)

print(
    f"Columns loaded: {operations.shape[1]}"
)


# ============================================================
# 4. OVERALL WEIGHTED KPI SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING OVERALL KPI SUMMARY")
print("=" * 60)

total_received = operations[
    "Records Received"
].sum()

total_processed = operations[
    "Records Processed"
].sum()

total_errors = operations[
    "Errors"
].sum()

total_rework = operations[
    "Rework"
].sum()

total_sla_achieved = operations[
    "SLA Achieved"
].sum()

total_working_hours = operations[
    "Working Hours"
].sum()

total_absenteeism = operations[
    "Absenteeism %"
].sum()


overall_productivity = (
    total_processed /
    total_working_hours
    if total_working_hours > 0
    else 0
)

overall_accuracy = (
    (
        total_processed - total_errors
    )
    / total_processed
    * 100
    if total_processed > 0
    else 0
)

overall_error_rate = (
    total_errors /
    total_processed
    * 100
    if total_processed > 0
    else 0
)

overall_rework_rate = (
    total_rework /
    total_processed
    * 100
    if total_processed > 0
    else 0
)

overall_sla = (
    total_sla_achieved /
    total_processed
    * 100
    if total_processed > 0
    else 0
)

overall_attendance = (
    operations["Attendance %"].mean()
)

overall_absenteeism = (
    operations["Absenteeism %"].mean()
)

overall_productivity_pct = (
    overall_productivity /
    15
    * 100
)

overall_pending = operations[
    "Records Pending"
].sum()


overall_summary = pd.DataFrame({
    "Metric": [
        "Total Received",
        "Total Processed",
        "Total Pending",
        "Total Errors",
        "Total Rework",
        "Productivity",
        "Productivity %",
        "Accuracy %",
        "Error Rate %",
        "Rework Rate %",
        "SLA %",
        "Attendance %",
        "Absenteeism %"
    ],

    "Value": [
        total_received,
        total_processed,
        overall_pending,
        total_errors,
        total_rework,
        overall_productivity,
        overall_productivity_pct,
        overall_accuracy,
        overall_error_rate,
        overall_rework_rate,
        overall_sla,
        overall_attendance,
        overall_absenteeism
    ]
})

overall_summary["Value"] = (
    overall_summary["Value"]
    .round(2)
)


# ============================================================
# 5. TEAM PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING TEAM PERFORMANCE")
print("=" * 60)

team_performance = (
    operations
    .groupby("Team")
    .agg(
        Received=(
            "Records Received",
            "sum"
        ),

        Processed=(
            "Records Processed",
            "sum"
        ),

        Pending=(
            "Records Pending",
            "sum"
        ),

        Errors=(
            "Errors",
            "sum"
        ),

        Rework=(
            "Rework",
            "sum"
        ),

        SLA_Achieved=(
            "SLA Achieved",
            "sum"
        ),

        Working_Hours=(
            "Working Hours",
            "sum"
        ),

        Attendance=(
            "Attendance %",
            "mean"
        )
    )
    .reset_index()
)


team_performance["Productivity"] = (
    team_performance["Processed"]
    / team_performance["Working_Hours"]
)

team_performance["Productivity %"] = (
    team_performance["Productivity"]
    / 15
    * 100
)

team_performance["Accuracy %"] = (
    (
        team_performance["Processed"]
        -
        team_performance["Errors"]
    )
    /
    team_performance["Processed"]
    * 100
)

team_performance["Error Rate %"] = (
    team_performance["Errors"]
    /
    team_performance["Processed"]
    * 100
)

team_performance["Rework Rate %"] = (
    team_performance["Rework"]
    /
    team_performance["Processed"]
    * 100
)

team_performance["SLA %"] = (
    team_performance["SLA_Achieved"]
    /
    team_performance["Processed"]
    * 100
)

team_performance["Backlog"] = (
    team_performance["Received"]
    -
    team_performance["Processed"]
)

team_performance = (
    team_performance
    .round(2)
)


# ============================================================
# 6. PROCESS PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING PROCESS PERFORMANCE")
print("=" * 60)

process_performance = (
    operations
    .groupby("Process")
    .agg(
        Received=(
            "Records Received",
            "sum"
        ),

        Processed=(
            "Records Processed",
            "sum"
        ),

        Pending=(
            "Records Pending",
            "sum"
        ),

        Errors=(
            "Errors",
            "sum"
        ),

        Rework=(
            "Rework",
            "sum"
        ),

        SLA_Achieved=(
            "SLA Achieved",
            "sum"
        ),

        Working_Hours=(
            "Working Hours",
            "sum"
        )
    )
    .reset_index()
)


process_performance["Productivity"] = (
    process_performance["Processed"]
    /
    process_performance["Working_Hours"]
)

process_performance["Productivity %"] = (
    process_performance["Productivity"]
    / 15
    * 100
)

process_performance["Accuracy %"] = (
    (
        process_performance["Processed"]
        -
        process_performance["Errors"]
    )
    /
    process_performance["Processed"]
    * 100
)

process_performance["Error Rate %"] = (
    process_performance["Errors"]
    /
    process_performance["Processed"]
    * 100
)

process_performance["Rework Rate %"] = (
    process_performance["Rework"]
    /
    process_performance["Processed"]
    * 100
)

process_performance["SLA %"] = (
    process_performance["SLA_Achieved"]
    /
    process_performance["Processed"]
    * 100
)

process_performance["Backlog"] = (
    process_performance["Received"]
    -
    process_performance["Processed"]
)

process_performance = (
    process_performance
    .round(2)
)


# ============================================================
# 7. SHIFT PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING SHIFT PERFORMANCE")
print("=" * 60)

shift_performance = (
    operations
    .groupby("Shift")
    .agg(
        Received=(
            "Records Received",
            "sum"
        ),

        Processed=(
            "Records Processed",
            "sum"
        ),

        Errors=(
            "Errors",
            "sum"
        ),

        Rework=(
            "Rework",
            "sum"
        ),

        SLA_Achieved=(
            "SLA Achieved",
            "sum"
        ),

        Working_Hours=(
            "Working Hours",
            "sum"
        ),

        Attendance=(
            "Attendance %",
            "mean"
        )
    )
    .reset_index()
)


shift_performance["Productivity"] = (
    shift_performance["Processed"]
    /
    shift_performance["Working_Hours"]
)

shift_performance["Productivity %"] = (
    shift_performance["Productivity"]
    / 15
    * 100
)

shift_performance["Accuracy %"] = (
    (
        shift_performance["Processed"]
        -
        shift_performance["Errors"]
    )
    /
    shift_performance["Processed"]
    * 100
)

shift_performance["Error Rate %"] = (
    shift_performance["Errors"]
    /
    shift_performance["Processed"]
    * 100
)

shift_performance["Rework Rate %"] = (
    shift_performance["Rework"]
    /
    shift_performance["Processed"]
    * 100
)

shift_performance["SLA %"] = (
    shift_performance["SLA_Achieved"]
    /
    shift_performance["Processed"]
    * 100
)

shift_performance = (
    shift_performance
    .round(2)
)


# ============================================================
# 8. EMPLOYEE PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING EMPLOYEE PERFORMANCE")
print("=" * 60)

employee_performance = (
    operations
    .groupby(
        [
            "Employee ID",
            "Employee Name",
            "Team"
        ]
    )
    .agg(
        Received=(
            "Records Received",
            "sum"
        ),

        Processed=(
            "Records Processed",
            "sum"
        ),

        Pending=(
            "Records Pending",
            "sum"
        ),

        Errors=(
            "Errors",
            "sum"
        ),

        Rework=(
            "Rework",
            "sum"
        ),

        SLA_Achieved=(
            "SLA Achieved",
            "sum"
        ),

        Working_Hours=(
            "Working Hours",
            "sum"
        ),

        Attendance=(
            "Attendance %",
            "mean"
        )
    )
    .reset_index()
)


employee_performance["Productivity"] = (
    employee_performance["Processed"]
    /
    employee_performance["Working_Hours"]
)

employee_performance["Productivity %"] = (
    employee_performance["Productivity"]
    / 15
    * 100
)

employee_performance["Accuracy %"] = (
    (
        employee_performance["Processed"]
        -
        employee_performance["Errors"]
    )
    /
    employee_performance["Processed"]
    * 100
)

employee_performance["Error Rate %"] = (
    employee_performance["Errors"]
    /
    employee_performance["Processed"]
    * 100
)

employee_performance["Rework Rate %"] = (
    employee_performance["Rework"]
    /
    employee_performance["Processed"]
    * 100
)

employee_performance["SLA %"] = (
    employee_performance["SLA_Achieved"]
    /
    employee_performance["Processed"]
    * 100
)

employee_performance = (
    employee_performance
    .round(2)
)


# ============================================================
# 9. EMPLOYEE RANKING
# ============================================================

employee_performance = (
    employee_performance
    .sort_values(
        by="Productivity %",
        ascending=False
    )
    .reset_index(drop=True)
)

employee_performance["Productivity Rank"] = (
    employee_performance.index + 1
)


# ============================================================
# 10. DAILY PERFORMANCE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING DAILY PERFORMANCE")
print("=" * 60)

daily_performance = (
    operations
    .groupby("Date")
    .agg(
        Received=(
            "Records Received",
            "sum"
        ),

        Processed=(
            "Records Processed",
            "sum"
        ),

        Pending=(
            "Records Pending",
            "sum"
        ),

        Errors=(
            "Errors",
            "sum"
        ),

        Rework=(
            "Rework",
            "sum"
        ),

        SLA_Achieved=(
            "SLA Achieved",
            "sum"
        ),

        Working_Hours=(
            "Working Hours",
            "sum"
        ),

        Attendance=(
            "Attendance %",
            "mean"
        )
    )
    .reset_index()
)


daily_performance["Productivity"] = (
    daily_performance["Processed"]
    /
    daily_performance["Working_Hours"]
)

daily_performance["Productivity %"] = (
    daily_performance["Productivity"]
    / 15
    * 100
)

daily_performance["Accuracy %"] = (
    (
        daily_performance["Processed"]
        -
        daily_performance["Errors"]
    )
    /
    daily_performance["Processed"]
    * 100
)

daily_performance["Error Rate %"] = (
    daily_performance["Errors"]
    /
    daily_performance["Processed"]
    * 100
)

daily_performance["Rework Rate %"] = (
    daily_performance["Rework"]
    /
    daily_performance["Processed"]
    * 100
)

daily_performance["SLA %"] = (
    daily_performance["SLA_Achieved"]
    /
    daily_performance["Processed"]
    * 100
)

daily_performance["Backlog"] = (
    daily_performance["Received"]
    -
    daily_performance["Processed"]
)

daily_performance = (
    daily_performance
    .round(2)
)


# ============================================================
# 11. SAVE OUTPUT FILES
# ============================================================

print("\n" + "=" * 60)
print("SAVING MANAGEMENT DATASETS")
print("=" * 60)


overall_summary.to_csv(
    PROCESSED_DATA_DIR /
    "overall_kpi_summary.csv",
    index=False
)

team_performance.to_csv(
    PROCESSED_DATA_DIR /
    "team_performance.csv",
    index=False
)

process_performance.to_csv(
    PROCESSED_DATA_DIR /
    "process_performance.csv",
    index=False
)

shift_performance.to_csv(
    PROCESSED_DATA_DIR /
    "shift_performance.csv",
    index=False
)

employee_performance.to_csv(
    PROCESSED_DATA_DIR /
    "employee_performance.csv",
    index=False
)

daily_performance.to_csv(
    PROCESSED_DATA_DIR /
    "daily_performance.csv",
    index=False
)


# ============================================================
# 12. DISPLAY KEY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("KEY MANAGEMENT RESULTS")
print("=" * 60)

print("\nOverall KPIs:")
print(overall_summary)

print("\nTeam Performance:")
print(
    team_performance[
        [
            "Team",
            "Processed",
            "Productivity %",
            "Accuracy %",
            "Error Rate %",
            "SLA %",
            "Backlog"
        ]
    ]
)

print("\nTop 5 Employees by Productivity:")
print(
    employee_performance[
        [
            "Employee ID",
            "Employee Name",
            "Team",
            "Productivity %",
            "Accuracy %",
            "SLA %",
            "Productivity Rank"
        ]
    ].head(5)
)


# ============================================================
# 13. COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("MANAGEMENT KPI ANALYSIS COMPLETED")
print("=" * 60)

print(
    "\nFiles created inside:"
)

print(PROCESSED_DATA_DIR)