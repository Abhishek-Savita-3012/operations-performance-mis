import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DATA_DIR = BASE_DIR / "data" / "cleaned"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. INPUT FILE
# ============================================================

OPERATIONS_FILE = (
    CLEANED_DATA_DIR /
    "operations_data_clean.csv"
)


# ============================================================
# 3. LOAD CLEANED DATA
# ============================================================

print("\n" + "=" * 60)
print("LOADING CLEANED OPERATIONS DATA")
print("=" * 60)

operations = pd.read_csv(
    OPERATIONS_FILE
)

operations["Date"] = pd.to_datetime(
    operations["Date"]
)

print(
    f"\nRows loaded: {len(operations)}"
)

print(
    f"Columns loaded: {len(operations.columns)}"
)


# ============================================================
# 4. PRODUCTIVITY
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING PRODUCTIVITY")
print("=" * 60)


operations["Productivity"] = np.where(
    operations["Working Hours"] > 0,
    operations["Records Processed"]
    / operations["Working Hours"],
    0
)


# ============================================================
# 5. PRODUCTIVITY %
# ============================================================

STANDARD_PRODUCTIVITY = 15

operations["Productivity %"] = np.where(
    STANDARD_PRODUCTIVITY > 0,
    (
        operations["Productivity"]
        / STANDARD_PRODUCTIVITY
    ) * 100,
    0
)


# Cap productivity percentage at 100
operations["Productivity %"] = (
    operations["Productivity %"]
    .clip(upper=100)
)


# ============================================================
# 6. ERROR RATE
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING QUALITY METRICS")
print("=" * 60)


operations["Error Rate %"] = np.where(
    operations["Records Processed"] > 0,
    (
        operations["Errors"]
        / operations["Records Processed"]
    ) * 100,
    0
)


# ============================================================
# 7. ACCURACY %
# ============================================================

operations["Accuracy %"] = np.where(
    operations["Records Processed"] > 0,
    (
        (
            operations["Records Processed"]
            - operations["Errors"]
        )
        / operations["Records Processed"]
    ) * 100,
    100
)


operations["Accuracy %"] = (
    operations["Accuracy %"]
    .clip(lower=0, upper=100)
)


# ============================================================
# 8. REWORK RATE
# ============================================================

operations["Rework Rate %"] = np.where(
    operations["Records Processed"] > 0,
    (
        operations["Rework"]
        / operations["Records Processed"]
    ) * 100,
    0
)


# ============================================================
# 9. SLA %
# ============================================================

operations["SLA %"] = np.where(
    operations["Records Processed"] > 0,
    (
        operations["SLA Achieved"]
        / operations["Records Processed"]
    ) * 100,
    0
)


operations["SLA %"] = (
    operations["SLA %"]
    .clip(lower=0, upper=100)
)


# ============================================================
# 10. SLA BREACH
# ============================================================

operations["SLA Breach"] = np.where(
    operations["SLA %"]
    < operations["SLA Target"],
    "Yes",
    "No"
)


# ============================================================
# 11. ATTENDANCE %
# ============================================================

attendance_percentage = {
    "Present": 100,
    "Late": 100,
    "Half Day": 50,
    "Leave": 0,
    "Absent": 0
}


operations["Attendance %"] = (
    operations["Attendance"]
    .map(attendance_percentage)
)


# ============================================================
# 12. ABSENTEEISM
# ============================================================

operations["Absenteeism %"] = np.where(
    operations["Attendance"].isin(
        ["Absent", "Leave"]
    ),
    100,
    0
)


# ============================================================
# 13. WORKLOAD UTILIZATION
# ============================================================

operations["Processing Ratio %"] = np.where(
    operations["Records Received"] > 0,
    (
        operations["Records Processed"]
        / operations["Records Received"]
    ) * 100,
    0
)


operations["Processing Ratio %"] = (
    operations["Processing Ratio %"]
    .clip(lower=0)
)


# ============================================================
# 14. DAILY BACKLOG CALCULATION
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING DAILY BACKLOG")
print("=" * 60)


daily_summary = (
    operations
    .groupby("Date", as_index=False)
    .agg(
        Daily_Received=(
            "Records Received",
            "sum"
        ),
        Daily_Processed=(
            "Records Processed",
            "sum"
        )
    )
)


daily_summary = daily_summary.sort_values(
    "Date"
).reset_index(
    drop=True
)


daily_summary["Opening Backlog"] = (
    daily_summary["Daily_Received"].cumsum().shift(
        fill_value=0
    )
    -
    daily_summary["Daily_Processed"].cumsum().shift(
        fill_value=0
    )
)


daily_summary["Closing Backlog"] = (
    daily_summary["Opening Backlog"]
    + daily_summary["Daily_Received"]
    - daily_summary["Daily_Processed"]
)


daily_summary["Closing Backlog"] = (
    daily_summary["Closing Backlog"]
    .clip(lower=0)
)


# ============================================================
# 15. MERGE BACKLOG INTO OPERATIONS DATA
# ============================================================

operations = operations.merge(
    daily_summary[
        [
            "Date",
            "Opening Backlog",
            "Closing Backlog"
        ]
    ],
    on="Date",
    how="left"
)


# ============================================================
# 16. BACKLOG STATUS
# ============================================================

operations["Backlog Status"] = np.where(
    operations["Closing Backlog"] > 0,
    "Backlog Exists",
    "No Backlog"
)


# ============================================================
# 17. PERFORMANCE BAND
# ============================================================

def classify_productivity(value):

    if value >= 90:
        return "High"

    elif value >= 75:
        return "Average"

    else:
        return "Low"


operations["Productivity Band"] = (
    operations["Productivity %"]
    .apply(classify_productivity)
)


# ============================================================
# 18. QUALITY BAND
# ============================================================

def classify_quality(value):

    if value >= 98:
        return "Excellent"

    elif value >= 95:
        return "Good"

    elif value >= 90:
        return "Average"

    else:
        return "Needs Improvement"


operations["Quality Band"] = (
    operations["Quality Score"]
    .apply(classify_quality)
)


# ============================================================
# 19. SLA BAND
# ============================================================

def classify_sla(value):

    if value >= 95:
        return "Met"

    elif value >= 90:
        return "At Risk"

    else:
        return "Breached"


operations["SLA Band"] = (
    operations["SLA %"]
    .apply(classify_sla)
)


# ============================================================
# 20. ROUND CALCULATED VALUES
# ============================================================

calculated_columns = [
    "Productivity",
    "Productivity %",
    "Error Rate %",
    "Accuracy %",
    "Rework Rate %",
    "SLA %",
    "Attendance %",
    "Absenteeism %",
    "Processing Ratio %",
    "Opening Backlog",
    "Closing Backlog"
]


operations[calculated_columns] = (
    operations[calculated_columns]
    .round(2)
)


# ============================================================
# 21. SORT FINAL DATA
# ============================================================

operations = operations.sort_values(
    by=[
        "Date",
        "Team",
        "Employee ID"
    ]
).reset_index(
    drop=True
)


# ============================================================
# 22. KPI VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("KPI VALIDATION")
print("=" * 60)


print(
    "\nAverage Productivity:",
    round(
        operations["Productivity"].mean(),
        2
    )
)


print(
    "Average Productivity %:",
    round(
        operations["Productivity %"].mean(),
        2
    )
)


print(
    "Average Accuracy %:",
    round(
        operations["Accuracy %"].mean(),
        2
    )
)


print(
    "Average Error Rate %:",
    round(
        operations["Error Rate %"].mean(),
        2
    )
)


print(
    "Average Rework Rate %:",
    round(
        operations["Rework Rate %"].mean(),
        2
    )
)


print(
    "Average SLA %:",
    round(
        operations["SLA %"].mean(),
        2
    )
)


print(
    "Average Attendance %:",
    round(
        operations["Attendance %"].mean(),
        2
    )
)


print(
    "Total Errors:",
    operations["Errors"].sum()
)


print(
    "Total Rework:",
    operations["Rework"].sum()
)


# ============================================================
# 23. SAVE PROCESSED DATA
# ============================================================

OUTPUT_FILE = (
    PROCESSED_DATA_DIR /
    "operations_processed.csv"
)


operations.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 24. COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("KPI ENGINEERING COMPLETED SUCCESSFULLY")
print("=" * 60)


print(
    "\nProcessed file created:"
)

print(OUTPUT_FILE)

print(
    "\nFinal rows:",
    len(operations)
)

print(
    "Final columns:",
    len(operations.columns)
)