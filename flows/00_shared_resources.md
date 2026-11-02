# Shared resources for the three flows

Fictional company: Laurentian Financial Group. Synthetic data only. Everything here is created inside the solution `HRSelfService` in a Power Apps Developer Plan environment.

Built by you in the tenant (user@example.com). Step by step in `docs/TENANT_GUIDE.md`.

## Naming convention

`HRSS - <Flow name>`, for example `HRSS - 1 HR data request with approval`. Actions get a short verb name ("Set status Pending approval"), not the default connector name. Every action gets a comment (the "..." menu on an action, then Add a comment). The comments are written in each design file below.

## Connection references (create inside the solution)

| Connection reference name | Connector | Used by |
|---|---|---|
| `HRSS SharePoint` | SharePoint | Flows 1 and 1b |
| `HRSS Excel Online (Business)` | Excel Online (Business) | Flows 2 and 3 |
| `HRSS Approvals` | Approvals | Flow 1 |
| `HRSS Outlook` | Office 365 Outlook | Flows 1, 2 and 3 (error emails) |
| `HRSS Teams` | Microsoft Teams | Flows 2 and 3 |

Why connection references: they let the solution move between environments without editing every action. In the demo all use your account.

## Environment variables (create inside the solution)

| Display name | Schema name | Type | Value (demo) | Used for |
|---|---|---|---|---|
| HR analytics lead email | `hrss_HRAnalyticsLeadEmail` | Text | user@example.com (you play the lead) | Flow 1 approver |
| Flow owner email | `hrss_FlowOwnerEmail` | Text | user@example.com | Error notifications |
| Report link | `hrss_ReportLink` | Text | URL of the Power BI report, or a SharePoint page with screenshots | Flow 1 approval email |
| Digest recipients | `hrss_DigestRecipients` | Text | user@example.com (semicolon separated list) | Flow 2 |
| KPI file path | `hrss_KpiFilePath` | Text | Path of `HR_KPI_Table.xlsx` in the document library | Flows 2 and 3 |
| Site URL | `hrss_SiteUrl` | Text | URL of the SharePoint site | Flow 1 |

In a flow, add an environment variable with the dynamic content picker (search for the display name). If you cannot find them in the picker, use the Parameters option in the flow, or hard code the value in the first build and replace it later (log this in `docs/04_results.md` lessons).

## SharePoint list: `HR Data Requests`

Site: a SharePoint team site you create in the tenant, for example "HR Analytics Demo". Create a list (blank list), then add the columns below. `Title` already exists.

| Column (internal name) | Type | Required | Choices or default | Purpose |
|---|---|---|---|---|
| `Title` | Single line of text | Yes | | Short title, for example "Turnover report for Finance" |
| `RequestType` | Choice | Yes | Turnover report, Absence report, Recruiting report, Headcount report, Other | What is asked |
| `Department` | Choice | Yes | Retail Banking, Commercial Banking, Wealth Management, Operations, Technology, Risk and Compliance, Finance, Human Resources, Marketing, Legal, Whole company | Scope |
| `Period` | Choice | Yes | Latest quarter, Last 4 quarters, Calendar year 2025, Calendar year 2026 to date, Other | Time frame |
| `BusinessReason` | Multiple lines of text (plain text) | Yes | | Purpose. Required by privacy rule P5. |
| `Language` | Choice | Yes | EN, FR (default EN) | Language of the answer |
| `Status` | Choice | Yes | New, Pending approval, Approved, Rejected, Delivered, Error (default New) | Shows each step of the flow |
| `RequesterEmail` | Single line of text | No | | Filled by the agent helper flow 1b. If empty, flow 1 uses `Created By`. |
| `Source` | Choice | No | Form, Agent (default Form) | Where the request came from |
| `ApprovalComments` | Multiple lines of text (plain text) | No | | Approver comments, the rejection reason |
| `DecisionBy` | Single line of text | No | | Approver display name |
| `DecisionOn` | Date and time | No | | When the decision was made |
| `ErrorDetails` | Multiple lines of text (plain text) | No | | Written by the error scope |
| `FlowRunLink` | Single line of text | No | | Link to the flow run, written by the flow |

A machine readable copy of the schema is in `flows/sharepoint_list_schema.csv`.

List permissions (item level): in List settings > Advanced settings, set "Read access: Read items that were created by the user" and "Create and Edit access: Create items and edit items that were created by the user". The HR analytics lead keeps full control through site permissions. This implements the access model in `docs/02_governance.md`. For a quick demo, leaving the defaults is acceptable if you note it in the results.

Sample test item (used for the first test of flow 1):

| Field | Value |
|---|---|
| Title | Turnover report for Operations |
| RequestType | Turnover report |
| Department | Operations |
| Period | Latest quarter |
| BusinessReason | Preparing the Q4 workforce plan (test) |
| Language | EN |

## Excel workbook: `HR_KPI_Table.xlsx`

Stored in the SharePoint document library of the same site (Excel Online (Business) works with files in SharePoint or OneDrive, and only reads data inside **tables**). The workbook has three tables.

### Table `KPI_Table` (worksheet `KPI_Table`)

Source: `data/kpi_table.csv`, produced by `src/reference_kpis.py`. 2,867 rows. Open the CSV in Excel, keep the header row, then Insert > Table and name it `KPI_Table` (Table Design > Table Name). Do not add formulas or extra columns. Numeric columns must be numeric (not text). Blank cells are intentional: they are values hidden by the minimum group size, and `suppressed` is then `Yes`.

| Column | Type | Meaning |
|---|---|---|
| `period_type` | text | Month, Quarter or Year |
| `period` | text | 2026-09, 2026-Q3, 2025 or 2026 YTD |
| `period_start` | text | First day, ISO date |
| `period_end` | text | Last day, ISO date |
| `months_in_period` | number | 1, 3, 12 or 9 (year to date) |
| `is_latest` | text | Yes for the latest month, latest quarter and latest year to date |
| `dimension` | text | All, Department, Location, Job level, Department x Location |
| `member` | text | Value within the dimension, for example Operations, or `Legal | Quebec City` |
| `group_size` | number | MIN(average headcount, period-end headcount). The privacy basis. |
| `suppressed` | text | Yes when group_size is below 5. All employee-based KPI cells are then blank. |
| `headcount` | number | Headcount at the end of the period |
| `hires` | number | Hires in the period |
| `voluntary_terminations` | number | Voluntary exits |
| `involuntary_terminations` | number | Involuntary exits |
| `voluntary_turnover_rate` | number | Annualized, a fraction (0.375 means 37.5%) |
| `involuntary_turnover_rate` | number | Annualized, a fraction |
| `absence_rate` | number | A fraction (0.021 means 2.1%) |
| `filled_requisitions` | number | Requisitions filled in the period |
| `ttf_suppressed` | text | Yes when fewer than 5 requisitions were filled |
| `avg_time_to_fill_days` | number | Blank when `ttf_suppressed` is Yes |

Formatting tip: after creating the table, format the rate columns as Percentage with 1 decimal for readability. Do not change the stored values.

### Table `Config` (worksheet `Config`)

| key | value | description |
|---|---|---|
| `voluntary_turnover_threshold` | 0.20 | Alert when annualized voluntary turnover is above this fraction (flow 3) |
| `digest_top_n` | 3 | Number of departments with the highest turnover shown in the digest (flow 2) |
| `min_group_size` | 5 | Documentation only. The rule is already applied in `KPI_Table`. |

### Table `Alert_Log` (worksheet `Alert_Log`)

Header row only at the start. Flow 3 appends rows.

| Column | Meaning |
|---|---|
| `logged_on` | Timestamp (text, ISO) |
| `period` | For example 2026-Q3 |
| `member` | Department name |
| `kpi` | `voluntary_turnover_rate` |
| `value` | Value that triggered the alert |
| `threshold` | Threshold at the time |

Purpose: stops flow 3 from posting the same alert every day. An alert is posted once per period and department.

## Expected values to check after upload

After the upload, these rows in `KPI_Table` (period `2026-Q3`, `period_type` Quarter) must hold: Operations voluntary_turnover_rate 0.375469, Marketing 0.470588, Technology 0.161074, Legal | Quebec City suppressed = Yes with blank rates. They are the same numbers as `data/reference_kpis.csv`.
