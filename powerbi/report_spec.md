# Power BI report specification

Report name: **HR Self-Service Analytics** (Laurentian Financial Group, synthetic data). Build it in Power BI Desktop after loading the model described in `model.md` and adding the measures from `measures.dax`.

## Global settings

- Page size 16:9. Theme: simple, high contrast, one accent color for "Operations" style highlights. Use colorblind-safe colors.
- Footer text box on every page: `[Privacy Footnote]` measure (card) plus "Synthetic data, fictional company".
- **Slicer panel (synced across pages):** Language (EN or FR, from `Language[Name]`, single select, default English), Year, Quarter (`quarter_label`), Department, Location, Job level. Use the `dim_date` Year > Quarter > Month fields only.
- Default selection: Quarter = latest (2026-Q3). Reset button bookmark "Latest quarter".
- No visual may contain `employee_id`. Turn off "Drill through" to row level and "Show data" and "Export data" for viewers (Report settings and Tenant settings if you publish).
- Every page title is a text box or card using the `Title ...` measures so French works. Chart titles use fx to point at the matching `Title ...` measure.
- Alt text on every visual (accessibility).
- Tooltips: only measures from sections 6 and 7 of `measures.dax`. Never `(raw)` measures.

## Privacy behavior to test on every page

1. Select Department = Legal and Location = Quebec City and Quarter = 2026-Q3. Every card must show "Not enough data" and every chart must be empty or show the notice from `[Privacy Notice]`.
2. Select Department = Legal and Location = Vancouver (6 employees). Values show.
3. Clear filters: company numbers show.

## Page 1: Overview

Purpose: one look at the state of the workforce. Maps to US-01.

| Visual | Type | Fields | Notes |
|---|---|---|---|
| Headcount | Card | `[Headcount Text]`, label `[Title Headcount]` | |
| Hires | Card | `[Hires Text]` | |
| Voluntary turnover (annualized) | Card | `[Voluntary Turnover Rate Text]` | |
| Involuntary turnover (annualized) | Card | `[Involuntary Turnover Rate Text]` | |
| Absence rate | Card | `[Absence Rate Text]` | |
| Average time to fill | Card | `[Average Time To Fill Text]` | |
| Headcount trend | Line chart | Axis `dim_date[year_month]`, values `[Headcount]` | Ignore the Quarter slicer on this visual (Edit interactions off for Quarter) so the trend always shows 33 months. Optional. |
| Headcount by department | Bar chart | Axis `dim_department[department_name_en]`, values `[Headcount]` | Sorted descending |
| Headcount by location | Donut or bar | Axis `dim_location[city_en]`, values `[Headcount]` | |
| Privacy notice | Card | `[Privacy Notice]` | Visible only when text is not blank |

## Page 2: Turnover

Maps to US-02.

| Visual | Type | Fields |
|---|---|---|
| Voluntary and involuntary turnover | Two cards | `[Voluntary Turnover Rate Text]`, `[Involuntary Turnover Rate Text]` |
| Voluntary turnover by department | Bar chart | Axis department, values `[Voluntary Turnover Rate]`. Data labels on. Sort descending. Highlight Operations through conditional color on a rule (value above 20%), not by hard coding the name. |
| Monthly trend | Line chart | Axis `dim_date[year_month]`, values `[Voluntary Turnover Rate]`, `[Involuntary Turnover Rate]`. Monthly values are annualized (x12), so they are noisy for small groups. Note this in the subtitle. |
| By location | Bar chart | Axis location, values `[Voluntary Turnover Rate]` |
| By job level | Bar chart | Axis `dim_job_level[level_name_en]`, values `[Voluntary Turnover Rate]` |
| Detail table | Matrix | Rows department, columns none, values `[Headcount Text]`, `[Voluntary Terminations]` (numeric), `[Voluntary Turnover Rate Text]`, `[Involuntary Turnover Rate Text]` | Suppressed rows show "Not enough data". |

## Page 3: Absences

Maps to US-03.

| Visual | Type | Fields |
|---|---|---|
| Absence rate | Card | `[Absence Rate Text]` |
| Absence rate by month | Column chart | Axis `dim_date[year_month]`, values `[Absence Rate]`. Winter peaks (January, February) should be visible. Ignore the Quarter slicer here. |
| Absence rate by month name, all years | Line chart | Axis `dim_date[month_name_en]` (sorted by month number), legend `dim_date[year]`, values `[Absence Rate]`. Shows the seasonal pattern by year. |
| By location | Bar chart | Axis location, values `[Absence Rate]` |
| By department | Bar chart | Axis department, values `[Absence Rate]` |
| Absence by type | Stacked column | Axis `year_month`, legend `fact_absences[type]`, values `[Absence Hours By Type]` (defined below). Hours, not employee counts. Vacation is visible here and labelled "not in the rate". |
| Definition note | Text box | "Absence rate = Sick, Family and Personal hours / scheduled hours. Vacation excluded." |

For the "Absence by type" visual add a measure:

```
Absence Hours By Type = IF ( [Group Is Visible], SUM ( fact_absences[hours] ) )
```

## Page 4: Recruiting

Maps to US-04.

| Visual | Type | Fields |
|---|---|---|
| Average time to fill | Card | `[Average Time To Fill Text]` |
| Filled requisitions | Card | `[Filled Requisitions (raw)]` shown through `[Time To Fill Is Visible]` rule, or a text measure |
| Open requisitions | Card | `[Open Requisitions (raw)]` |
| Time to fill by location | Bar chart | Axis location, values `[Average Time To Fill]`. Vancouver should be the longest. |
| Time to fill by job level | Bar chart | Axis job level, values `[Average Time To Fill]` |
| Time to fill by department | Bar chart | Axis department, values `[Average Time To Fill]` |
| Trend | Line chart | Axis quarter label, values `[Average Time To Fill]` |
| Note | Text box | "Time to fill = days from opening to start date, filled requisitions only. Recent periods can look shorter because slow requisitions are still open." |

## Page 5: Data quality

Maps to US-05.

| Visual | Type | Fields |
|---|---|---|
| Status | Card | `[DQ Status]` |
| Checks table | Table or multi-row card | One row per check: name (typed in a small disconnected table `dq_check_names`, or as separate cards) and the matching `DQ ...` measure. Show: Missing language preference (expected above 0), Terminated before hire (0), Terminated without type (0), Active with termination type (0), Missing manager below VP (0), Manager not in employees (0), Snapshot rows without department (0), Reconciliation difference (0). |
| Missing language preference | Card | `[DQ Missing Language Preference]` and `[DQ Missing Language Share]` |
| Suppressed groups | Card | `[DQ Suppressed Department x Location]` with subtitle "Department and location combinations hidden by the minimum group size in the selected period" |
| Row counts | Table | Table names and row counts (typed: use cards of `COUNTROWS` for each fact) to compare with `model.md` |

This page must never show a table of `dq_employee` rows.

## Visual interactions and filters

- Page level filters: none (the slicers drive everything), except where noted.
- Turn off cross-filtering from the monthly trend charts to the cards so clicking a month does not accidentally change the privacy evaluation without the user seeing it.
- Add a bookmark for each page with "Latest quarter" applied.

## Acceptance check (before publishing)

1. Fill the table in `docs/04_results.md` section 2 with at least 10 values. Each must match `data/reference_kpis.csv` (or `data/kpi_table.csv`) at the shown precision. Suggested cells:

| Filter | KPI | Expected (from reference) |
|---|---|---|
| 2026-Q3, All | Headcount | 1,488 |
| 2026-Q3, All | Voluntary turnover | 15.8% |
| 2026-Q3, All | Absence rate | 1.9% |
| 2026-Q3, All | Average time to fill | 48.3 |
| 2025, All | Hires | 250 |
| 2025, All | Voluntary turnover | 14.0% |
| 2026-Q3, Operations | Voluntary turnover | 37.5% |
| 2026-Q3, Montreal | Headcount | 805 |
| 2026-Q3, Quebec City | Absence rate | 2.1% |
| 2026-Q3, Vancouver | Average time to fill | 81.5 |
| 2026-Q3, Legal and Quebec City | any KPI | Not enough data |

2. If a value differs, the usual causes are: a day-range slicer, the file origin (encoding), the relationship on `fact_requisitions` (filled date must be the active one), or a measure copied with a different name. Fix the model, not the reference.
3. Run the privacy behavior tests above and take the screenshots listed in `docs/TENANT_GUIDE.md` section 7.

## Publishing

Publish to the Power BI Service in the tenant if the license allows (a Power BI Pro or a trial is needed to publish to a workspace). If not, keep the `.pbix` (or save as a `.pbip` project folder under `powerbi/`) and the screenshots, and say so in the README.
