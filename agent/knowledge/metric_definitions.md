# Metric definitions

Fictional company: Laurentian Financial Group. All data is synthetic. Version 1.0. Owner: HR analytics lead.
Source of the numbers: the KPI facts file, produced by the reference calculation (`src/reference_kpis.py`) and matched to the Power BI report.

These definitions are the only source for "how is it calculated" answers. Periods are quarters (for example 2026-Q3) and years (2024, 2025, and 2026 YTD, January to September 2026). Data ends on 2026-09-30.

## General rules

**Minimum group size.** A metric is reported only for groups of at least 5 employees. A group is the set of employees in a department, a location, a job level, or a department and location together. Group size is the smaller of the average month-end headcount in the period and the headcount at the end of the period. Below 5, the value is not reported ("Not enough data" / "Données insuffisantes"). Time to fill uses a similar rule: fewer than 5 filled requisitions means not reported.

**Annualized.** Turnover rates are converted to a yearly equivalent so quarters and years can be compared. A quarter has 3 months, a full year 12, and 2026 YTD 9.

**Aggregates only.** Metrics describe groups, never individuals.

## Headcount (Effectif)

Number of employees employed after the last day of the period. An employee who leaves on the last day of the period is not counted. Full-time, part-time and contract employees each count as one.

## Hires (Embauches)

Number of employees whose first day of work falls in the period.

## Voluntary exits and involuntary exits (Départs volontaires, départs involontaires)

Number of employees whose last day of work falls in the period. Voluntary: the employee chose to leave (resignation, retirement). Involuntary: the employer ended employment.

## Average headcount (Effectif moyen)

Average of the month-end headcounts of the months in the period. A quarter averages 3 month-ends.

## Voluntary turnover rate, annualized (Taux de roulement volontaire, annualisé)

Voluntary exits in the period, divided by the average headcount in the period, multiplied by 12 and divided by the number of months in the period.
Example: 10 voluntary exits in a quarter with an average headcount of 200 gives 10 / 200 x 12 / 3 = 20.0%.

## Involuntary turnover rate, annualized (Taux de roulement involontaire, annualisé)

Same calculation, with involuntary exits.

## Absence rate (Taux d'absentéisme)

Unplanned absence hours divided by scheduled hours, for the group and the period. Unplanned absences are Sick (maladie), Family (responsabilités familiales) and Personal (personnel). **Vacation (vacances) is planned leave and is not counted.** Scheduled hours are the weekdays an employee was employed in the period times the daily hours of the employment type (full-time 7.5, part-time 4.5, contract 7.5). Statutory holidays are not removed.

## Average time to fill (Délai moyen de dotation)

Average number of calendar days from the day a requisition was opened to the start date of the person hired, for requisitions that were filled in the period. Requisitions that are still open or were cancelled are not included. Recent periods can look shorter than they will end up, because slow requisitions are still open.

## What is not covered

Monthly values, salary and pay, performance, engagement, health or leave reasons, diversity, individual employees or managers, job changes and internal mobility, and anything outside the data period.

## Glossary of names (English and French)

| English | Français |
|---|---|
| Headcount | Effectif |
| Hires | Embauches |
| Voluntary turnover | Roulement volontaire |
| Involuntary turnover | Roulement involontaire |
| Absence rate | Taux d'absentéisme |
| Time to fill | Délai de dotation |
| Not enough data | Données insuffisantes |
| Quarter (Q3) | Trimestre (T3) |
| Department | Département |
| Location | Emplacement |
| Quebec City | Québec |
| Montreal | Montréal |
