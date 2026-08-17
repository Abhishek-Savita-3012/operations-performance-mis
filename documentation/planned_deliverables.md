# Planned Deliverables

This file tracks deliverables for **Operations Performance MIS** beyond the initial release — items either partially in place or not yet started. For what's already built and shipped, see the [Results Snapshot](../README.md#results-snapshot) and [Deliverables](../README.md#overview) sections of the main README.

## Status Legend

- ✅ Completed
- 🚧 In Progress
- 📋 Planned

## Completed (v1.0)

| Deliverable | Status |
|---|---|
| Synthetic Operations & Employee dataset | ✅ |
| Data cleaning & validation pipeline | ✅ |
| KPI engineering (productivity, quality, SLA, backlog, bands) | ✅ |
| Team / Process / Shift / Employee / Daily aggregation | ✅ |
| Automated Excel Daily MIS report | ✅ |
| Power BI star schema export | ✅ |
| 6-page interactive Power BI dashboard | ✅ |
| Project documentation (scope, schema, data dictionary) | ✅ |

## Planned

### Repository & Engineering

- 📋 Add `LICENSE` file (MIT)
- 📋 Add automated tests for KPI calculation logic (`calculate_kpis.py`)
- 📋 Centralize business thresholds (SLA target, productivity benchmark, error-rate threshold) into a single shared config used by both the Excel and Power BI layers, instead of duplicated constants
- 📋 Resolve duplicate backlog computation — `create_daily_mis.py` currently recalculates daily backlog independently of `analyze_performance.py` instead of reading its output
- 📋 Add a `Makefile` or single entry-point script to run the full pipeline in one command

### Data Model

- 📋 Refactor Power BI `dim_team` / `dim_process` / `dim_shift` / `dim_employee` tables into attribute-only dimensions, with all percentage/rate metrics rebuilt as DAX measures against the fact tables (avoids double-counting when slicers are applied)
- 📋 Add a proper `DateTable` mark-as-date-table configuration with fiscal calendar support

### Reporting & Analysis

- 📋 Add week-over-week and month-over-month trend comparisons to the Management Summary page
- 📋 Add a drill-through page from Team/Employee visuals to record-level detail
- 📋 Add email/PDF export automation for the Daily MIS report
- 📋 Extend the dataset beyond a single reporting period to validate seasonality handling in the backlog and productivity trends

### Documentation

- 📋 Add a short project write-up / case study (problem → approach → outcome) for portfolio presentation
- 📋 Record a short walkthrough video or GIF of the Power BI dashboard for the README