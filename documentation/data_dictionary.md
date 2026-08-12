# Operations Performance MIS — Data Dictionary

## Employee Master

| Column | Description |
|---|---|
| Employee ID | Unique identifier assigned to each employee |
| Employee Name | Employee name |
| Team | Operations team assigned to the employee |
| Process | Business process handled by the employee |
| Shift | Employee working shift |
| Joining Date | Employee joining date |
| Skill Level | Employee skill classification |
| Performance Band | High, Average or Low performance classification |
| Standard Working Hours | Standard daily working hours |
| Active | Indicates whether the employee is currently active |

## Operations Data

| Column | Description |
|---|---|
| Record ID | Unique identifier for each employee-day operational record |
| Employee ID | Employee associated with the operational record |
| Employee Name | Employee name |
| Team | Operations team |
| Process | Business process |
| Date | Operational date |
| Shift | Working shift |
| Records Received | Number of records received by the employee |
| Records Processed | Number of records processed |
| Records Pending | Records remaining from the employee's allocated workload |
| Errors | Number of records containing errors |
| Rework | Number of records requiring rework |
| SLA Target | Target SLA percentage |
| SLA Achieved | Number of processed records achieved within SLA |
| Processing Time | Average processing time per record |
| Working Hours | Actual working hours for the employee |
| Quality Score | Employee quality score percentage |
| Attendance | Employee attendance status |
| Status | Operational completion status |