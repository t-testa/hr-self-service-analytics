# Decisions log

Decisions made autonomously while building, with the reason. Change any of them, but change the matching files too (the data, the reference KPIs, the DAX and the agent definitions all depend on each other).

| # | Decision | Why |
|---|---|---|
| 1 | The repo was built in a folder the app made for the session. Move or copy the `hr-self-service-analytics/` folder to where you want it, then push. | No project folder existed. |
| 2 | Data covers 2024-01-01 to **2026-09-30** (33 months, as-of date 2026-09-30). | Q3 2026 is the last complete quarter at build time (2026-10-30), and the brief's example question is about Q3 2026. |
| 3 | The company starts with 1,500 employees on 2024-01-01 and stays between about 1,490 and 1,510 (backfills plus small growth). | Matches "about 1,500 employees". |
| 4 | Department, location and job level are static per employee (no transfers, no promotions). | Keeps the star schema simple. Consequence: **internal mobility is not included** (no job change history exists). Listed as a future extension. |
| 5 | **Absence rate** = unplanned hours (Sick, Family, Personal) divided by scheduled hours. Vacation is stored but excluded. | Vacation is planned leave. Including it would make the metric meaningless. |
| 6 | Scheduled hours = weekdays employed in the month times daily hours (Full-time 7.5, Part-time 4.5, Contract 7.5). Statutory holidays are not modelled. | Simple, documented, reproducible in DAX and pandas. |
| 7 | **Turnover rate (annualized)** = exits in period / average month-end headcount in period x 12 / months in period. | One formula for month, quarter and year. Easy to write in DAX. |
| 8 | **Time to fill** = days from open date to the start date of the hire (not offer acceptance). Cancelled and still-open requisitions are excluded. | The dataset has one date for the hire. Recent periods are biased low because slow requisitions are still open (stated as a limitation). |
| 9 | **Minimum group size** = MIN(average month-end headcount in the period, headcount at period end) below 5 suppresses every employee-based KPI. Time to fill is suppressed when fewer than 5 requisitions were filled. | One simple rule that works in DAX, pandas, Excel and the agent. |
| 10 | The rule applies to the population of the group, not to the event count. A group of 8 with 1 exit still shows "1 exit". Residual risk is documented in `docs/02_governance.md`. | The brief says "below 5 employees". Stricter rules would hide most monthly views. |
| 11 | The facts (`fact_headcount_snapshot`, `fact_terminations`, `fact_absences`) are employee-level rows with a hidden `employee_id`. `reference_kpis.py` does **not** read them. | The snapshot needs employee grain to give correct headcount and scheduled hours. Independence of the check matters more than a smaller file. A test confirms the two agree. |
| 12 | `requisitions.csv` is used directly as `fact_requisitions`. Open date and filled date both relate to the date table. Filled date is the active relationship. | Avoids a duplicate file. |
| 13 | The KPI table for the flows and the agent is `data/kpi_table.csv` (wide, one row per period, dimension and member). Suppressed values are blank, with a `suppressed` flag. | Flows and the agent can filter on `suppressed = No` and never see a number below the group size. |
| 14 | No `.xlsx` is produced. The tenant guide shows how to open the CSV in Excel Online and format it as a table named `KPI_Table`. | The `openpyxl` library was not available and adding a dependency for one file was not worth it. |
| 15 | Flow 3 uses a scheduled check against the Excel table (not a Power BI data alert). | Data alerts need a published report and a Power BI connector setup. The Excel route is reproducible, testable and works with the free developer plan. A Power BI alert is noted as an optional extra. |
| 16 | Flow 2 reads the Excel table, not a Power BI dataset query. | Same reason as 15, and the numbers can be checked against `reference_kpis.csv`. The guide mentions the dataset query as an upgrade. |
| 17 | The Operations planted turnover is about 27 percent per year in the generator settings, and comes out higher (30 to 38 percent) because new hires leave faster and backfills keep refilling the churn. | Realistic churn dynamic. The pattern is still clear. |
| 18 | Small departments produce noisy quarters (for example Marketing, about 49 people, shows 47 percent in 2026-Q3 on 5 exits). This is left in. | It is a good, honest example of why small groups need care, and it is a useful alert test case. |
| 19 | CSV files are UTF-8 with a byte order mark and LF line endings. | Excel and Power BI show French accents correctly. Git keeps the files byte-stable (`.gitattributes`). |
| 20 | `pytest.ini` sets `--basetemp=.pytest_tmp` inside the repo. | Windows temp folders sometimes deny access. The folder is git-ignored. |
| 21 | Commit author is `25282736+t-testa@users.noreply.github.com`, trailer `Co-Authored-By: Claude <noreply@anthropic.com>`, nothing pushed. | As instructed. |
| 22 | The fictional personas use first names only (Isabelle, Marc, Sophie). | Personas need names to read well. They are fictional, like the company. |
| 23 | French labels use accents in the data and the agent files. Docs avoid em dashes everywhere. | Rule from the brief. |
| 24 | Test prompts are written before any agent testing and are not to be edited after the first run, except to add new ones. | Keeps the evaluation honest. New failures become new prompts. |
