import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# 1. PROJECT SETUP
# ============================================================

np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. MASTER CONFIGURATION
# ============================================================

teams = {
    "Team A": "Document Verification",
    "Team B": "Data Entry",
    "Team C": "Application Processing",
    "Team D": "Quality Review"
}

shifts = {
    "Morning": "06:00-14:00",
    "General": "09:00-18:00",
    "Afternoon": "14:00-22:00",
    "Night": "22:00-06:00"
}

dates = pd.date_range(
    start="2026-07-01",
    end="2026-08-10",
    freq="D"
)

attendance_options = [
    "Present",
    "Absent",
    "Leave",
    "Late",
    "Half Day"
]

attendance_probabilities = [
    0.90,
    0.01,
    0.03,
    0.04,
    0.02
]


# ============================================================
# 3. PERFORMANCE PARAMETERS
# ============================================================

performance_parameters = {
    "High": {
        "productivity_min": 12,
        "productivity_max": 18,
        "quality_min": 97,
        "quality_max": 100,
        "sla_min": 95,
        "sla_max": 100
    },

    "Average": {
        "productivity_min": 8,
        "productivity_max": 14,
        "quality_min": 93,
        "quality_max": 98,
        "sla_min": 88,
        "sla_max": 97
    },

    "Low": {
        "productivity_min": 5,
        "productivity_max": 10,
        "quality_min": 88,
        "quality_max": 95,
        "sla_min": 75,
        "sla_max": 92
    }
}


# ============================================================
# 4. TEAM WORKLOAD CONFIGURATION
# ============================================================

team_daily_volume = {
    "Team A": 1050,
    "Team B": 1250,
    "Team C": 1150,
    "Team D": 900
}


# ============================================================
# 5. CREATE EMPLOYEE MASTER
# ============================================================

print("\n" + "=" * 60)
print("CREATING EMPLOYEE MASTER")
print("=" * 60)

employees = []

employee_counter = 1

# 10 High, 22 Average, 8 Low performers
performance_bands = (
    ["High"] * 10 +
    ["Average"] * 22 +
    ["Low"] * 8
)

np.random.shuffle(performance_bands)


for team, process in teams.items():

    for _ in range(10):

        employee_id = f"EMP{employee_counter:03d}"
        employee_name = f"Employee {employee_counter:03d}"

        performance_band = performance_bands[
            employee_counter - 1
        ]

        # Skill level based on performance
        if performance_band == "High":

            skill_level = np.random.choice(
                ["Intermediate", "Advanced"],
                p=[0.30, 0.70]
            )

        elif performance_band == "Average":

            skill_level = np.random.choice(
                ["Beginner", "Intermediate", "Advanced"],
                p=[0.20, 0.60, 0.20]
            )

        else:

            skill_level = np.random.choice(
                ["Beginner", "Intermediate"],
                p=[0.70, 0.30]
            )

        shift = np.random.choice(
            list(shifts.keys())
        )

        joining_date = (
            pd.Timestamp("2024-01-01")
            + pd.Timedelta(
                days=np.random.randint(0, 700)
            )
        )

        employees.append({
            "Employee ID": employee_id,
            "Employee Name": employee_name,
            "Team": team,
            "Process": process,
            "Shift": shift,
            "Joining Date": joining_date.date(),
            "Skill Level": skill_level,
            "Performance Band": performance_band,
            "Standard Working Hours": 8,
            "Active": "Yes"
        })

        employee_counter += 1


employee_master = pd.DataFrame(employees)


# ============================================================
# 6. DESIGNATED HIGH-ERROR EMPLOYEES
# ============================================================

# These employees will deliberately have weaker quality
# so that the final MIS can identify quality issues.

high_error_employees = [
    "EMP017",
    "EMP034"
]


# ============================================================
# 7. DISPLAY EMPLOYEE MASTER SUMMARY
# ============================================================

print("\nEmployee Count:")
print(len(employee_master))

print("\nTeam Distribution:")
print(
    employee_master["Team"].value_counts()
)

print("\nPerformance Distribution:")
print(
    employee_master["Performance Band"].value_counts()
)

print("\nShift Distribution:")
print(
    employee_master["Shift"].value_counts()
)


# ============================================================
# 8. SAVE EMPLOYEE MASTER
# ============================================================

employee_master.to_csv(
    RAW_DATA_DIR / "employee_master.csv",
    index=False
)

print("\nEmployee master saved successfully.")


# ============================================================
# 9. HELPER FUNCTION — DAILY TEAM WORKLOAD
# ============================================================

def generate_team_received(date, team):

    base_volume = team_daily_volume[team]

    weekday = date.weekday()

    # Monday workload spike
    if weekday == 0:
        weekday_multiplier = 1.15

    # Thursday slightly higher
    elif weekday == 3:
        weekday_multiplier = 1.10

    # Weekend lower workload
    elif weekday in [5, 6]:
        weekday_multiplier = 0.75

    else:
        weekday_multiplier = 1.00

    # Random daily variation
    random_factor = np.random.uniform(
        0.90,
        1.10
    )

    received = (
        base_volume
        * weekday_multiplier
        * random_factor
    )

    # Team B workload spike from August 1
    if (
        team == "Team B"
        and date >= pd.Timestamp("2026-08-01")
    ):
        received *= 1.20

    return max(
        100,
        int(received)
    )


# ============================================================
# 10. GENERATE OPERATIONS DATA
# ============================================================

print("\n" + "=" * 60)
print("GENERATING OPERATIONS DATA")
print("=" * 60)

records = []

record_counter = 1


# ------------------------------------------------------------
# Opening backlog for each team
# ------------------------------------------------------------

opening_backlog = {
    "Team A": 0,
    "Team B": 0,
    "Team C": 0,
    "Team D": 0
}


# ============================================================
# 11. DATE → TEAM → EMPLOYEE PROCESSING
# ============================================================

for date in dates:

    for team, process in teams.items():

        # ----------------------------------------------------
        # STEP 1: Generate total team workload
        # ----------------------------------------------------

        team_received = generate_team_received(
            date,
            team
        )

        team_opening_backlog = opening_backlog[team]

        total_available_work = (
            team_opening_backlog
            + team_received
        )

        # ----------------------------------------------------
        # STEP 2: Get employees belonging to the team
        # ----------------------------------------------------

        team_employees = employee_master[
            employee_master["Team"] == team
        ].copy()

        employee_results = []

        total_team_capacity = 0


        # ----------------------------------------------------
        # STEP 3: Determine employee attendance + capacity
        # ----------------------------------------------------

        for _, employee in team_employees.iterrows():

            attendance = np.random.choice(
                attendance_options,
                p=attendance_probabilities
            )

            # Working hours based on attendance
            if attendance == "Present":
                working_hours = 8.0

            elif attendance == "Late":
                working_hours = 7.5

            elif attendance == "Half Day":
                working_hours = 4.0

            else:
                working_hours = 0.0


            performance_band = employee[
                "Performance Band"
            ]

            params = performance_parameters[
                performance_band
            ]


            # Base productivity rate
            productivity_rate = np.random.uniform(
                params["productivity_min"],
                params["productivity_max"]
            )


            # Slight shift-level capacity variation
            if employee["Shift"] == "Night":

                productivity_rate *= np.random.uniform(
                    0.90,
                    0.98
                )

            elif employee["Shift"] == "Morning":

                productivity_rate *= np.random.uniform(
                    1.00,
                    1.05
                )


            employee_capacity = (
                productivity_rate
                * working_hours
            )

            total_team_capacity += employee_capacity


            employee_results.append({
                "employee": employee,
                "attendance": attendance,
                "working_hours": working_hours,
                "productivity_rate": productivity_rate,
                "capacity": employee_capacity
            })


        # ----------------------------------------------------
        # STEP 4: Determine team-level processed volume
        # ----------------------------------------------------

        # Team capacity has some natural variation
        team_processed = int(
            min(
                total_available_work,
                max(
                    0,
                    np.random.normal(
                        total_team_capacity,
                        total_team_capacity * 0.05
                    )
                )
            )
        )


        # ----------------------------------------------------
        # STEP 5: Calculate team closing backlog
        # ----------------------------------------------------

        team_closing_backlog = max(
            0,
            total_available_work - team_processed
        )

        opening_backlog[team] = team_closing_backlog


        # ----------------------------------------------------
        # STEP 6: Distribute processed work among employees
        # ----------------------------------------------------

        capacity_sum = sum(
            item["capacity"]
            for item in employee_results
        )


        processed_allocations = []

        remaining_processed = team_processed


        for index, item in enumerate(employee_results):

            if capacity_sum == 0:

                allocated_processed = 0

            elif index == len(employee_results) - 1:

                # Give the final employee whatever remains
                allocated_processed = remaining_processed

            else:

                share = (
                    item["capacity"]
                    / capacity_sum
                )

                allocated_processed = int(
                    team_processed * share
                )

                allocated_processed = min(
                    allocated_processed,
                    remaining_processed
                )

            processed_allocations.append(
                allocated_processed
            )

            remaining_processed -= allocated_processed


        # ----------------------------------------------------
        # STEP 7: Distribute received workload
        # ----------------------------------------------------

        # Employee received workload is proportional to
        # their available capacity.

        received_allocations = []

        remaining_received = team_received


        for index, item in enumerate(employee_results):

            if capacity_sum == 0:

                allocated_received = 0

            elif index == len(employee_results) - 1:

                allocated_received = remaining_received

            else:

                share = (
                    item["capacity"]
                    / capacity_sum
                )

                allocated_received = int(
                    team_received * share
                )

                allocated_received = min(
                    allocated_received,
                    remaining_received
                )

            received_allocations.append(
                allocated_received
            )

            remaining_received -= allocated_received


        # ----------------------------------------------------
        # STEP 8: Create employee-level records
        # ----------------------------------------------------

        for index, item in enumerate(employee_results):

            employee = item["employee"]

            attendance = item["attendance"]

            working_hours = item["working_hours"]

            performance_band = employee[
                "Performance Band"
            ]

            received = received_allocations[index]

            processed = processed_allocations[index]


            # ------------------------------------------------
            # Employee pending workload
            # ------------------------------------------------

            # This represents the employee-level portion
            # of today's workload that was not completed.

            pending = max(
                0,
                received - processed
            )


            # ------------------------------------------------
            # Quality
            # ------------------------------------------------

            params = performance_parameters[
                performance_band
            ]

            quality_score = np.random.uniform(
                params["quality_min"],
                params["quality_max"]
            )


            # Designated high-error employees
            if employee["Employee ID"] in high_error_employees:

                quality_score -= np.random.uniform(
                    4,
                    7
                )


            quality_score = max(
                80,
                min(
                    100,
                    quality_score
                )
            )


            # ------------------------------------------------
            # Errors
            # ------------------------------------------------

            errors = int(
                round(
                    processed
                    * (100 - quality_score)
                    / 100
                )
            )

            errors = max(
                0,
                errors
            )


            # ------------------------------------------------
            # Rework
            # ------------------------------------------------

            base_rework_rate = np.random.uniform(
                0.01,
                0.04
            )

            if employee["Employee ID"] in high_error_employees:

                base_rework_rate += np.random.uniform(
                    0.02,
                    0.04
                )

            rework = int(
                processed
                * base_rework_rate
            )


            # ------------------------------------------------
            # SLA
            # ------------------------------------------------

            sla_percentage = np.random.uniform(
                params["sla_min"],
                params["sla_max"]
            )


            # Afternoon shift penalty
            if employee["Shift"] == "Afternoon":

                sla_percentage -= np.random.uniform(
                    2,
                    5
                )


            # High-error employees also have slight SLA impact
            if employee["Employee ID"] in high_error_employees:

                sla_percentage -= np.random.uniform(
                    1,
                    3
                )


            sla_percentage = max(
                0,
                min(
                    100,
                    sla_percentage
                )
            )


            # ------------------------------------------------
            # SLA target / achievement
            # ------------------------------------------------

            sla_target_percentage = 95

            sla_achieved = int(
                processed
                * sla_percentage
                / 100
            )


            # ------------------------------------------------
            # Processing Time
            # ------------------------------------------------

            processing_time = np.random.uniform(
                3.0,
                7.0
            )


            if performance_band == "Low":

                processing_time += np.random.uniform(
                    0.5,
                    1.5
                )

            elif performance_band == "High":

                processing_time -= np.random.uniform(
                    0.2,
                    0.6
                )


            processing_time = max(
                2.0,
                round(
                    processing_time,
                    2
                )
            )


            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            if processed == 0:

                status = "Pending"

            elif pending == 0:

                status = "Completed"

            else:

                status = "Partial"


            # ------------------------------------------------
            # Record
            # ------------------------------------------------

            records.append({

                "Record ID":
                    f"REC{record_counter:06d}",

                "Employee ID":
                    employee["Employee ID"],

                "Employee Name":
                    employee["Employee Name"],

                "Team":
                    team,

                "Process":
                    employee["Process"],

                "Date":
                    date.date(),

                "Shift":
                    employee["Shift"],

                "Records Received":
                    received,

                "Records Processed":
                    processed,

                "Records Pending":
                    pending,

                "Errors":
                    errors,

                "Rework":
                    rework,

                "SLA Target":
                    sla_target_percentage,

                "SLA Achieved":
                    sla_achieved,

                "Processing Time":
                    processing_time,

                "Working Hours":
                    working_hours,

                "Quality Score":
                    round(
                        quality_score,
                        2
                    ),

                "Attendance":
                    attendance,

                "Status":
                    status
            })


            record_counter += 1


# ============================================================
# 12. CREATE DATAFRAME
# ============================================================

operations_data = pd.DataFrame(
    records
)


# ============================================================
# 13. SORT DATA
# ============================================================

operations_data = operations_data.sort_values(
    by=[
        "Date",
        "Team",
        "Employee ID"
    ]
).reset_index(
    drop=True
)


# ============================================================
# 14. SAVE OPERATIONS DATA
# ============================================================

operations_data.to_csv(
    RAW_DATA_DIR / "operations_data.csv",
    index=False
)


# ============================================================
# 15. DATA VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("DATA VALIDATION")
print("=" * 60)


# Record count
print(
    "\nTotal Records:",
    len(operations_data)
)


# Duplicate IDs
duplicate_ids = (
    operations_data["Record ID"]
    .duplicated()
    .sum()
)

print(
    "Duplicate Record IDs:",
    duplicate_ids
)


# Missing values
missing_values = (
    operations_data
    .isnull()
    .sum()
    .sum()
)

print(
    "Missing Values:",
    missing_values
)


# Negative values
negative_received = (
    operations_data["Records Received"] < 0
).sum()

negative_processed = (
    operations_data["Records Processed"] < 0
).sum()

negative_pending = (
    operations_data["Records Pending"] < 0
).sum()

negative_hours = (
    operations_data["Working Hours"] < 0
).sum()


print(
    "Negative Received:",
    negative_received
)

print(
    "Negative Processed:",
    negative_processed
)

print(
    "Negative Pending:",
    negative_pending
)

print(
    "Negative Working Hours:",
    negative_hours
)


# Quality validation
invalid_quality = (
    (operations_data["Quality Score"] < 0)
    |
    (operations_data["Quality Score"] > 100)
).sum()

print(
    "Quality outside 0-100:",
    invalid_quality
)


# SLA validation
invalid_sla = (
    (operations_data["SLA Achieved"] < 0)
    |
    (
        operations_data["SLA Achieved"]
        >
        operations_data["Records Processed"]
    )
).sum()

print(
    "Invalid SLA Achieved values:",
    invalid_sla
)


# Attendance / working hours validation
invalid_attendance_hours = (
    (
        operations_data["Attendance"]
        == "Absent"
    )
    &
    (
        operations_data["Working Hours"] != 0
    )
).sum()

print(
    "Absent employees with working hours:",
    invalid_attendance_hours
)


# ============================================================
# 16. TEAM-LEVEL VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("TEAM-LEVEL VALIDATION")
print("=" * 60)


team_summary = operations_data.groupby(
    "Team"
).agg(

    Total_Received=(
        "Records Received",
        "sum"
    ),

    Total_Processed=(
        "Records Processed",
        "sum"
    ),

    Total_Pending=(
        "Records Pending",
        "sum"
    ),

    Total_Errors=(
        "Errors",
        "sum"
    ),

    Total_Rework=(
        "Rework",
        "sum"
    )

).reset_index()


print(
    team_summary.to_string(
        index=False
    )
)


# ============================================================
# 17. ATTENDANCE SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("ATTENDANCE SUMMARY")
print("=" * 60)

print(
    operations_data[
        "Attendance"
    ].value_counts()
)


# ============================================================
# 18. PERFORMANCE SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)


performance_summary = operations_data.groupby(
    "Team"
).agg(

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

    Avg_Quality=(
        "Quality Score",
        "mean"
    ),

    Avg_Processing_Time=(
        "Processing Time",
        "mean"
    )

).round(2)


print(
    performance_summary
)


# ============================================================
# 19. FINAL OUTPUT INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("DATA GENERATION COMPLETED")
print("=" * 60)

print(
    "\nEmployee Master:"
)

print(
    RAW_DATA_DIR / "employee_master.csv"
)

print(
    "\nOperations Data:"
)

print(
    RAW_DATA_DIR / "operations_data.csv"
)

print(
    "\nTotal Operations Records:",
    len(operations_data)
)

print(
    "\nColumns:",
    len(operations_data.columns)
)

print("\nDataset columns:")

for column in operations_data.columns:
    print(
        f"- {column}"
    )

print(
    "\nReady for Lesson 4: Data Cleaning & Validation."
)