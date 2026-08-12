import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEANED_DATA_DIR = BASE_DIR / "data" / "cleaned"

CLEANED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FILE PATHS
# ============================================================

EMPLOYEE_FILE = (
    RAW_DATA_DIR / "employee_master.csv"
)

OPERATIONS_FILE = (
    RAW_DATA_DIR / "operations_data.csv"
)


# ============================================================
# 3. LOAD RAW DATA
# ============================================================

print("\n" + "=" * 60)
print("LOADING RAW DATA")
print("=" * 60)

employees = pd.read_csv(
    EMPLOYEE_FILE
)

operations = pd.read_csv(
    OPERATIONS_FILE
)

print(
    f"\nEmployee Master: {employees.shape[0]} rows, "
    f"{employees.shape[1]} columns"
)

print(
    f"Operations Data: {operations.shape[0]} rows, "
    f"{operations.shape[1]} columns"
)


# ============================================================
# 4. STANDARDIZE COLUMN NAMES
# ============================================================

employees.columns = (
    employees.columns
    .str.strip()
)

operations.columns = (
    operations.columns
    .str.strip()
)


# ============================================================
# 5. CONVERT DATA TYPES
# ============================================================

print("\n" + "=" * 60)
print("CONVERTING DATA TYPES")
print("=" * 60)


# Employee master
employees["Joining Date"] = pd.to_datetime(
    employees["Joining Date"],
    errors="coerce"
)


# Operations data
operations["Date"] = pd.to_datetime(
    operations["Date"],
    errors="coerce"
)


# Numeric columns
numeric_columns = [
    "Records Received",
    "Records Processed",
    "Records Pending",
    "Errors",
    "Rework",
    "SLA Target",
    "SLA Achieved",
    "Processing Time",
    "Working Hours",
    "Quality Score"
]

for column in numeric_columns:

    operations[column] = pd.to_numeric(
        operations[column],
        errors="coerce"
    )


# ============================================================
# 6. REMOVE DUPLICATES
# ============================================================

print("\n" + "=" * 60)
print("DUPLICATE CHECK")
print("=" * 60)


employee_duplicates = employees.duplicated().sum()

operations_duplicates = operations.duplicated().sum()

record_id_duplicates = (
    operations["Record ID"]
    .duplicated()
    .sum()
)


print(
    "Employee duplicate rows:",
    employee_duplicates
)

print(
    "Operations duplicate rows:",
    operations_duplicates
)

print(
    "Duplicate Record IDs:",
    record_id_duplicates
)


# Remove duplicate rows if any
employees = employees.drop_duplicates()

operations = operations.drop_duplicates(
    subset=["Record ID"]
)


# ============================================================
# 7. MISSING VALUE CHECK
# ============================================================

print("\n" + "=" * 60)
print("MISSING VALUE CHECK")
print("=" * 60)


employee_missing = (
    employees.isnull().sum()
)

operations_missing = (
    operations.isnull().sum()
)


print("\nEmployee Master:")
print(
    employee_missing[
        employee_missing > 0
    ]
)


print("\nOperations Data:")
print(
    operations_missing[
        operations_missing > 0
    ]
)


# ============================================================
# 8. VALIDATE NUMERIC RANGES
# ============================================================

print("\n" + "=" * 60)
print("NUMERIC RANGE VALIDATION")
print("=" * 60)


checks = {

    "Negative Records Received":
        (
            operations["Records Received"] < 0
        ).sum(),

    "Negative Records Processed":
        (
            operations["Records Processed"] < 0
        ).sum(),

    "Negative Records Pending":
        (
            operations["Records Pending"] < 0
        ).sum(),

    "Negative Errors":
        (
            operations["Errors"] < 0
        ).sum(),

    "Negative Rework":
        (
            operations["Rework"] < 0
        ).sum(),

    "Invalid Quality Score":
        (
            (operations["Quality Score"] < 0)
            |
            (operations["Quality Score"] > 100)
        ).sum(),

    "Invalid SLA Target":
        (
            (operations["SLA Target"] < 0)
            |
            (operations["SLA Target"] > 100)
        ).sum(),

    "Negative Working Hours":
        (
            operations["Working Hours"] < 0
        ).sum()

}


for check, count in checks.items():

    print(
        f"{check}: {count}"
    )


# ============================================================
# 9. ATTENDANCE VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("ATTENDANCE VALIDATION")
print("=" * 60)


valid_attendance = [
    "Present",
    "Absent",
    "Leave",
    "Late",
    "Half Day"
]


invalid_attendance = operations[
    ~operations["Attendance"].isin(
        valid_attendance
    )
]


print(
    "Invalid attendance records:",
    len(invalid_attendance)
)


# ============================================================
# 10. STATUS VALIDATION
# ============================================================

valid_status = [
    "Completed",
    "Partial",
    "Pending"
]


invalid_status = operations[
    ~operations["Status"].isin(
        valid_status
    )
]


print(
    "Invalid status records:",
    len(invalid_status)
)


# ============================================================
# 11. EMPLOYEE MASTER RELATIONSHIP CHECK
# ============================================================

print("\n" + "=" * 60)
print("EMPLOYEE RELATIONSHIP VALIDATION")
print("=" * 60)


employee_ids = set(
    employees["Employee ID"]
)

operations_employee_ids = set(
    operations["Employee ID"]
)


orphan_employee_ids = (
    operations_employee_ids
    - employee_ids
)


print(
    "Orphan Employee IDs:",
    len(orphan_employee_ids)
)


# ============================================================
# 12. CHECK EMPLOYEE / TEAM CONSISTENCY
# ============================================================

employee_team_lookup = (
    employees
    .set_index("Employee ID")["Team"]
    .to_dict()
)


operations["Master Team"] = (
    operations["Employee ID"]
    .map(employee_team_lookup)
)


team_mismatches = (
    operations["Team"]
    != operations["Master Team"]
).sum()


print(
    "Employee-Team mismatches:",
    team_mismatches
)


# ============================================================
# 13. CHECK EMPLOYEE / PROCESS CONSISTENCY
# ============================================================

employee_process_lookup = (
    employees
    .set_index("Employee ID")["Process"]
    .to_dict()
)


operations["Master Process"] = (
    operations["Employee ID"]
    .map(employee_process_lookup)
)


process_mismatches = (
    operations["Process"]
    != operations["Master Process"]
).sum()


print(
    "Employee-Process mismatches:",
    process_mismatches
)


# ============================================================
# 14. REMOVE VALIDATION HELPER COLUMNS
# ============================================================

operations = operations.drop(
    columns=[
        "Master Team",
        "Master Process"
    ]
)


# ============================================================
# 15. SORT DATA
# ============================================================

employees = employees.sort_values(
    by=["Team", "Employee ID"]
).reset_index(
    drop=True
)


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
# 16. FINAL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("FINAL VALIDATION")
print("=" * 60)


print(
    "\nEmployee Master:",
    employees.shape
)

print(
    "Operations Data:",
    operations.shape
)

print(
    "Employee Master Missing Values:",
    employees.isnull().sum().sum()
)

print(
    "Operations Missing Values:",
    operations.isnull().sum().sum()
)

print(
    "Operations Duplicate IDs:",
    operations["Record ID"].duplicated().sum()
)


# ============================================================
# 17. SAVE CLEANED DATA
# ============================================================

employees.to_csv(
    CLEANED_DATA_DIR /
    "employee_master_clean.csv",
    index=False
)


operations.to_csv(
    CLEANED_DATA_DIR /
    "operations_data_clean.csv",
    index=False
)


# ============================================================
# 18. COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 60)


print(
    "\nCleaned files created:"
)

print(
    CLEANED_DATA_DIR /
    "employee_master_clean.csv"
)

print(
    CLEANED_DATA_DIR /
    "operations_data_clean.csv"
)