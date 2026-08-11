# Operations Dataset Schema

## Dataset Purpose

The Operations dataset contains fictional daily operational records used to monitor employee productivity, quality, SLA, attendance, workload, and backlog.

## Columns

| Column | Data Type | Description |
|---|---|---|
| Record ID | String | Unique operational record identifier |
| Employee ID | String | Employee identifier |
| Employee Name | String | Employee name |
| Team | String | Employee's assigned team |
| Process | String | Process handled |
| Date | Date | Operational date |
| Shift | String | Employee shift |
| Records Received | Integer | Number of records received |
| Records Processed | Integer | Number of records processed |
| Records Pending | Integer | Number of records remaining |
| Errors | Integer | Number of incorrect records |
| Rework | Integer | Number of records requiring rework |
| SLA Target | Integer | Target number of records to be completed within SLA |
| SLA Achieved | Integer | Number of records completed within SLA |
| Processing Time | Decimal | Average processing time in minutes |
| Working Hours | Decimal | Actual hours worked |
| Quality Score | Decimal | Quality percentage |
| Attendance | String | Present / Absent / Leave / Late / Half Day |
| Status | String | Completed / Pending / Partial |

## Derived Metrics

### Productivity

Records Processed / Working Hours

### Accuracy

Correct Records / Total Records × 100

### Error Rate

Errors / Total Records × 100

### Rework Rate

Rework / Total Records × 100

### SLA Achievement %

SLA Achieved / Records Processed × 100

### Attendance %

Present Days / Scheduled Days × 100

### Absenteeism %

Absent Days / Scheduled Days × 100

### Backlog

Records Received - Records Processed