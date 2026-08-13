import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = (
    BASE_DIR / "data" / "processed"
)

POWERBI_DATA_DIR = (
    BASE_DIR / "data" / "powerbi"
)

POWERBI_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FILE PATHS
# ============================================================

OPERATIONS_FILE = (
    PROCESSED_DATA_DIR /
    "operations_processed.csv"
)

TEAM_FILE = (
    PROCESSED_DATA_DIR /
    "team_performance.csv"
)

PROCESS_FILE = (
    PROCESSED_DATA_DIR /
    "process_performance.csv"
)

SHIFT_FILE = (
    PROCESSED_DATA_DIR /
    "shift_performance.csv"
)

EMPLOYEE_FILE = (
    PROCESSED_DATA_DIR /
    "employee_performance.csv"
)

DAILY_FILE = (
    PROCESSED_DATA_DIR /
    "daily_performance.csv"
)

BACKLOG_FILE = (
    PROCESSED_DATA_DIR /
    "daily_backlog.csv"
)


# ============================================================
# 3. LOAD DATA
# ============================================================

print("\n" + "=" * 60)
print("LOADING PROCESSED DATA")
print("=" * 60)

operations = pd.read_csv(
    OPERATIONS_FILE
)

team = pd.read_csv(
    TEAM_FILE
)

process = pd.read_csv(
    PROCESS_FILE
)

shift = pd.read_csv(
    SHIFT_FILE
)

employee = pd.read_csv(
    EMPLOYEE_FILE
)

daily = pd.read_csv(
    DAILY_FILE
)

backlog = pd.read_csv(
    BACKLOG_FILE
)


print(
    f"\nOperations: {operations.shape}"
)

print(
    f"Team: {team.shape}"
)

print(
    f"Process: {process.shape}"
)

print(
    f"Shift: {shift.shape}"
)

print(
    f"Employee: {employee.shape}"
)

print(
    f"Daily: {daily.shape}"
)

print(
    f"Backlog: {backlog.shape}"
)


# ============================================================
# 4. CONVERT DATE COLUMNS
# ============================================================

operations["Date"] = pd.to_datetime(
    operations["Date"]
)

daily["Date"] = pd.to_datetime(
    daily["Date"]
)

backlog["Date"] = pd.to_datetime(
    backlog["Date"]
)


# ============================================================
# 5. CREATE POWER BI DATASETS
# ============================================================

print("\n" + "=" * 60)
print("PREPARING POWER BI DATASETS")
print("=" * 60)


datasets = {

    "fact_operations.csv":
        operations,

    "dim_team.csv":
        team,

    "dim_process.csv":
        process,

    "dim_shift.csv":
        shift,

    "dim_employee.csv":
        employee,

    "fact_daily_performance.csv":
        daily,

    "fact_daily_backlog.csv":
        backlog
}


# ============================================================
# 6. SAVE DATASETS
# ============================================================

for filename, dataframe in datasets.items():

    output_file = (
        POWERBI_DATA_DIR /
        filename
    )

    dataframe.to_csv(
        output_file,
        index=False
    )

    print(
        f"Created: {filename} "
        f"({len(dataframe)} rows, "
        f"{len(dataframe.columns)} columns)"
    )


# ============================================================
# 7. VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("POWER BI DATA VALIDATION")
print("=" * 60)


for filename, dataframe in datasets.items():

    missing_values = (
        dataframe.isnull().sum().sum()
    )

    duplicate_rows = (
        dataframe.duplicated().sum()
    )

    print(
        f"\n{filename}"
    )

    print(
        f"Rows: {len(dataframe)}"
    )

    print(
        f"Columns: {len(dataframe.columns)}"
    )

    print(
        f"Missing Values: {missing_values}"
    )

    print(
        f"Duplicate Rows: {duplicate_rows}"
    )


# ============================================================
# 8. COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("POWER BI DATA PREPARATION COMPLETED")
print("=" * 60)

print(
    f"\nPower BI files created in:"
)

print(
    POWERBI_DATA_DIR
)