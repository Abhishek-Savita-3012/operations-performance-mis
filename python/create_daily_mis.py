import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = (
    BASE_DIR / "data" / "processed"
)

REPORTS_DIR = (
    BASE_DIR / "reports"
)

REPORTS_DIR.mkdir(
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

SHIFT_FILE = (
    PROCESSED_DATA_DIR /
    "shift_performance.csv"
)

DAILY_FILE = (
    PROCESSED_DATA_DIR /
    "daily_performance.csv"
)

EMPLOYEE_FILE = (
    PROCESSED_DATA_DIR /
    "employee_performance.csv"
)

REPORT_FILE = (
    REPORTS_DIR /
    "Daily_Operations_MIS.xlsx"
)

BACKLOG_FILE = (
    PROCESSED_DATA_DIR /
    "daily_backlog.csv"
)


# ============================================================
# 3. BUSINESS CONSTANTS
# ============================================================

PRODUCTIVITY_BENCHMARK = 15
SLA_TARGET = 95


# ============================================================
# 4. LOAD DATA
# ============================================================

print("\n" + "=" * 60)
print("LOADING MANAGEMENT DATA")
print("=" * 60)

operations = pd.read_csv(
    OPERATIONS_FILE
)

team = pd.read_csv(
    TEAM_FILE
)

shift = pd.read_csv(
    SHIFT_FILE
)

daily = pd.read_csv(
    DAILY_FILE
)

employees = pd.read_csv(
    EMPLOYEE_FILE
)

operations["Date"] = pd.to_datetime(
    operations["Date"]
)

daily["Date"] = pd.to_datetime(
    daily["Date"]
)

print(
    f"\nOperations rows: {len(operations)}"
)

print(
    f"Daily rows: {len(daily)}"
)

print(
    f"Teams: {len(team)}"
)

print(
    f"Shifts: {len(shift)}"
)

print(
    f"Employees: {len(employees)}"
)


# ============================================================
# 5. BUILD CUMULATIVE BACKLOG
# ============================================================

print("\n" + "=" * 60)
print("CALCULATING CUMULATIVE BACKLOG")
print("=" * 60)

daily_backlog = (
    daily[
        [
            "Date",
            "Received",
            "Processed",
            "Pending"
        ]
    ]
    .sort_values("Date")
    .reset_index(drop=True)
)

daily_backlog["Opening Backlog"] = 0

daily_backlog["Closing Backlog"] = 0


opening_backlog = 0


for index in range(
    len(daily_backlog)
):

    received = daily_backlog.loc[
        index,
        "Received"
    ]

    processed = daily_backlog.loc[
        index,
        "Processed"
    ]

    daily_backlog.loc[
        index,
        "Opening Backlog"
    ] = opening_backlog

    closing_backlog = (
        opening_backlog
        + received
        - processed
    )

    daily_backlog.loc[
        index,
        "Closing Backlog"
    ] = closing_backlog

    opening_backlog = closing_backlog


daily_backlog["Backlog Change"] = (
    daily_backlog["Closing Backlog"]
    -
    daily_backlog["Opening Backlog"]
)


# ============================================================
# 6. VALIDATE BACKLOG
# ============================================================

negative_backlog = (
    daily_backlog["Closing Backlog"] < 0
).sum()

print(
    f"Negative closing backlog days: "
    f"{negative_backlog}"
)

print(
    f"Final closing backlog: "
    f"{daily_backlog['Closing Backlog'].iloc[-1]}"
)

daily_backlog.to_csv(
    BACKLOG_FILE,
    index=False
)


# ============================================================
# 7. SELECT LATEST MIS DATE
# ============================================================

latest_date = (
    daily["Date"].max()
)

print(
    f"\nMIS Date: "
    f"{latest_date.strftime('%d-%b-%Y')}"
)


latest_daily = daily[
    daily["Date"] == latest_date
].iloc[0]


latest_backlog = daily_backlog[
    daily_backlog["Date"] == latest_date
].iloc[0]


# ============================================================
# 8. CALCULATE DAILY KPIs
# ============================================================

received = latest_daily["Received"]

processed = latest_daily["Processed"]

pending = latest_daily["Pending"]

errors = latest_daily["Errors"]

rework = latest_daily["Rework"]

working_hours = latest_daily[
    "Working_Hours"
]

sla_achieved = latest_daily[
    "SLA_Achieved"
]


productivity = (
    processed /
    working_hours
    if working_hours > 0
    else 0
)


productivity_pct = (
    productivity /
    PRODUCTIVITY_BENCHMARK
    * 100
)


accuracy = (
    (
        processed - errors
    )
    /
    processed
    * 100
    if processed > 0
    else 0
)


error_rate = (
    errors /
    processed
    * 100
    if processed > 0
    else 0
)


rework_rate = (
    rework /
    processed
    * 100
    if processed > 0
    else 0
)


sla_pct = (
    sla_achieved /
    processed
    * 100
    if processed > 0
    else 0
)


attendance = latest_daily[
    "Attendance"
]


# ============================================================
# 9. FIND TEAM ISSUES
# ============================================================

highest_backlog_team = team.loc[
    team["Backlog"].idxmax()
]

lowest_sla_team = team.loc[
    team["SLA %"].idxmin()
]

highest_error_team = team.loc[
    team["Error Rate %"].idxmax()
]

lowest_productivity_team = team.loc[
    team["Productivity %"].idxmin()
]


# ============================================================
# 10. FIND SHIFT ISSUES
# ============================================================

lowest_sla_shift = shift.loc[
    shift["SLA %"].idxmin()
]


lowest_productivity_shift = shift.loc[
    shift["Productivity %"].idxmin()
]


# ============================================================
# 11. FIND HIGH-ERROR EMPLOYEES
# ============================================================

HIGH_ERROR_THRESHOLD = 5

high_error_employees = employees[
    employees["Error Rate %"]
    > HIGH_ERROR_THRESHOLD
].copy()


# ============================================================
# 12. GENERATE KEY ISSUES
# ============================================================

key_issues = []

if highest_backlog_team["Backlog"] > 0:

    key_issues.append(
        f"Backlog is highest in "
        f"{highest_backlog_team['Team']} "
        f"at {highest_backlog_team['Backlog']:,.0f} records."
    )


if sla_pct < SLA_TARGET:

    key_issues.append(
        f"Overall SLA achievement is "
        f"{sla_pct:.1f}%, below the "
        f"{SLA_TARGET}% target."
    )


key_issues.append(
    f"{lowest_sla_shift['Shift']} shift has the "
    f"lowest SLA at "
    f"{lowest_sla_shift['SLA %']:.1f}%."
)


key_issues.append(
    f"{highest_error_team['Team']} has the "
    f"highest error rate at "
    f"{highest_error_team['Error Rate %']:.1f}%."
)


if len(high_error_employees) > 0:

    key_issues.append(
        f"{len(high_error_employees)} employees "
        f"exceed the {HIGH_ERROR_THRESHOLD}% "
        f"error-rate threshold."
    )


# ============================================================
# 13. GENERATE RECOMMENDED ACTIONS
# ============================================================

recommended_actions = []

recommended_actions.append(
    f"Review and redistribute pending workload "
    f"from {highest_backlog_team['Team']}."
)

recommended_actions.append(
    f"Investigate SLA breaches in the "
    f"{lowest_sla_shift['Shift']} shift."
)

recommended_actions.append(
    f"Conduct quality review for "
    f"{highest_error_team['Team']}."
)

recommended_actions.append(
    f"Review high-error employee cases and "
    f"identify recurring error patterns."
)

recommended_actions.append(
    f"Compare best-performing practices from "
    f"higher-productivity teams with "
    f"{lowest_productivity_team['Team']}."
)


# ============================================================
# 14. CREATE EXCEL WORKBOOK
# ============================================================

print("\n" + "=" * 60)
print("CREATING DAILY MIS REPORT")
print("=" * 60)

workbook = Workbook()


# ============================================================
# 15. DEFINE STYLES
# ============================================================

title_font = Font(
    bold=True,
    size=18
)

section_font = Font(
    bold=True,
    size=13
)

header_font = Font(
    bold=True
)

white_font = Font(
    bold=True,
    color="FFFFFF"
)

header_fill = PatternFill(
    "solid",
    fgColor="1F4E78"
)

section_fill = PatternFill(
    "solid",
    fgColor="D9EAF7"
)

kpi_fill = PatternFill(
    "solid",
    fgColor="EAF2F8"
)

thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)


# ============================================================
# 16. EXECUTIVE MIS SHEET
# ============================================================

ws = workbook.active

ws.title = "Daily MIS"

ws.merge_cells(
    "A1:H1"
)

ws["A1"] = "OPERATIONS DAILY MIS"

ws["A1"].font = title_font

ws["A1"].alignment = Alignment(
    horizontal="center"
)


ws.merge_cells(
    "A2:H2"
)

ws["A2"] = (
    f"Date: "
    f"{latest_date.strftime('%d-%b-%Y')}"
)

ws["A2"].alignment = Alignment(
    horizontal="center"
)


# ============================================================
# 17. KPI SECTION
# ============================================================

ws["A4"] = "KEY PERFORMANCE INDICATORS"

ws["A4"].font = section_font

ws["A4"].fill = section_fill


kpis = [

    ("Total Received", received, "#,##0"),

    ("Total Processed", processed, "#,##0"),

    ("Pending", pending, "#,##0"),

    ("Closing Backlog",
     latest_backlog["Closing Backlog"],
     "#,##0"),

    ("SLA Achievement",
     sla_pct / 100,
     "0.0%"),

    ("Quality",
     accuracy / 100,
     "0.0%"),

    ("Productivity",
     productivity_pct / 100,
     "0.0%"),

    ("Error Rate",
     error_rate / 100,
     "0.0%"),

    ("Attendance",
     attendance / 100,
     "0.0%")
]


row = 5

for metric, value, number_format in kpis:

    ws.cell(
        row=row,
        column=1,
        value=metric
    )

    ws.cell(
        row=row,
        column=1
    ).font = header_font

    ws.cell(
        row=row,
        column=2,
        value=value
    )

    ws.cell(
        row=row,
        column=2
    ).number_format = number_format

    ws.cell(
        row=row,
        column=2
    ).fill = kpi_fill

    row += 1


# ============================================================
# 18. BACKLOG INFORMATION
# ============================================================

ws["D4"] = "BACKLOG STATUS"

ws["D4"].font = section_font

ws["D4"].fill = section_fill


backlog_info = [

    ("Opening Backlog",
     latest_backlog["Opening Backlog"]),

    ("Received",
     latest_backlog["Received"]),

    ("Processed",
     latest_backlog["Processed"]),

    ("Closing Backlog",
     latest_backlog["Closing Backlog"]),

    ("Backlog Change",
     latest_backlog["Backlog Change"])
]


row = 5

for metric, value in backlog_info:

    ws.cell(
        row=row,
        column=4,
        value=metric
    )

    ws.cell(
        row=row,
        column=4
    ).font = header_font

    ws.cell(
        row=row,
        column=5,
        value=value
    )

    ws.cell(
        row=row,
        column=5
    ).number_format = "#,##0"

    row += 1


# ============================================================
# 19. KEY ISSUES
# ============================================================

ws["A16"] = "KEY ISSUES"

ws["A16"].font = section_font

ws["A16"].fill = section_fill


row = 17

for issue in key_issues:

    ws.cell(
        row=row,
        column=1,
        value="• " + issue
    )

    ws.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=8
    )

    row += 1


# ============================================================
# 20. RECOMMENDED ACTIONS
# ============================================================

action_start = row + 1

ws.cell(
    row=action_start,
    column=1,
    value="RECOMMENDED ACTIONS"
)

ws.cell(
    row=action_start,
    column=1
).font = section_font

ws.cell(
    row=action_start,
    column=1
).fill = section_fill


row = action_start + 1

for action in recommended_actions:

    ws.cell(
        row=row,
        column=1,
        value="• " + action
    )

    ws.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=8
    )

    row += 1


# ============================================================
# 21. TEAM PERFORMANCE SHEET
# ============================================================

team_ws = workbook.create_sheet(
    "Team Performance"
)

team_ws.append(
    list(team.columns)
)

for cell in team_ws[1]:

    cell.font = white_font
    cell.fill = header_fill
    cell.alignment = Alignment(
        horizontal="center"
    )


for record in team.itertuples(
    index=False,
    name=None
):

    team_ws.append(
        list(record)
    )


# ============================================================
# 22. SHIFT PERFORMANCE SHEET
# ============================================================

shift_ws = workbook.create_sheet(
    "Shift Performance"
)

shift_ws.append(
    list(shift.columns)
)

for cell in shift_ws[1]:

    cell.font = white_font
    cell.fill = header_fill
    cell.alignment = Alignment(
        horizontal="center"
    )


for record in shift.itertuples(
    index=False,
    name=None
):

    shift_ws.append(
        list(record)
    )


# ============================================================
# 23. DAILY BACKLOG SHEET
# ============================================================

backlog_ws = workbook.create_sheet(
    "Daily Backlog"
)

backlog_ws.append(
    list(daily_backlog.columns)
)

for cell in backlog_ws[1]:

    cell.font = white_font
    cell.fill = header_fill
    cell.alignment = Alignment(
        horizontal="center"
    )


for record in daily_backlog.itertuples(
    index=False,
    name=None
):

    backlog_ws.append(
        list(record)
    )


# ============================================================
# 24. EMPLOYEE PERFORMANCE SHEET
# ============================================================

employee_ws = workbook.create_sheet(
    "Employee Performance"
)

employee_ws.append(
    list(employees.columns)
)

for cell in employee_ws[1]:

    cell.font = white_font
    cell.fill = header_fill
    cell.alignment = Alignment(
        horizontal="center"
    )


for record in employees.itertuples(
    index=False,
    name=None
):

    employee_ws.append(
        list(record)
    )


# ============================================================
# 25. FORMAT ALL SHEETS
# ============================================================

for worksheet in workbook.worksheets:

    worksheet.freeze_panes = "A2"

    for row_cells in worksheet.iter_rows():

        for cell in row_cells:

            cell.border = thin_border

            cell.alignment = Alignment(
                vertical="center"
            )

    for column_cells in worksheet.columns:

        max_length = 0

        column_letter = (
            get_column_letter(
                column_cells[0].column
            )
        )

        for cell in column_cells:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            35
        )


# ============================================================
# 26. SPECIAL FORMATTING
# ============================================================

ws.freeze_panes = "A5"

ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 18
ws.column_dimensions["D"].width = 25
ws.column_dimensions["E"].width = 18


# ============================================================
# 27. SAVE WORKBOOK
# ============================================================

workbook.save(
    REPORT_FILE
)


# ============================================================
# 28. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("DAILY MIS REPORT CREATED SUCCESSFULLY")
print("=" * 60)

print(
    f"\nReport created:"
)

print(
    REPORT_FILE
)

print(
    f"\nMIS Date: "
    f"{latest_date.strftime('%d-%b-%Y')}"
)

print(
    f"Closing Backlog: "
    f"{latest_backlog['Closing Backlog']:,.0f}"
)

print(
    f"SLA: "
    f"{sla_pct:.2f}%"
)

print(
    f"Quality: "
    f"{accuracy:.2f}%"
)

print(
    f"Productivity: "
    f"{productivity_pct:.2f}%"
)

print(
    f"Attendance: "
    f"{attendance:.2f}%"
)