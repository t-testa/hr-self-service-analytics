# Tenant guide: the parts only you can do

Click by click, in the order to do them. Every step ends with **Expected** so you know it worked. Written for someone who knows n8n and Make but has not built a Power Automate flow yet. Menus change often at Microsoft. If a name is slightly different, look for the closest one and write the difference in `docs/04_results.md` section 6 (that is useful interview material too).

All commands are PowerShell. All data is synthetic. Account: user@example.com.

## How Power Automate maps to what you know

| n8n or Make | Power Automate |
|---|---|
| Trigger node or module | **Trigger** (first card of the flow) |
| Node or module | **Action** (one card) |
| Credential or connection | **Connection** (and in a solution, a **Connection reference**) |
| IF node or router with filter | **Condition** (Yes and No branches), or **Switch** |
| Loop or iterator | **Apply to each** |
| Set variable, Tools, Compose | **Initialize variable**, **Set variable**, **Compose** |
| Error trigger or error handler route | **Scope** plus **Configure run after** (a "Catch" scope that runs when the "Try" scope failed) |
| Stop and error | **Terminate** (Status Failed) |
| n8n variables or Make data store | **Environment variables** in the solution |
| Execution history | **Run history** (28 days) |
| Expressions `{{ }}` | Expressions `@{ }` with functions like `first()`, `coalesce()`, `formatNumber()` |

Habits that save time: rename every action as you add it (it changes the expression names, so rename **before** you use its outputs), add a comment to every action, and test after each few actions with **Test > Manually**.

---

## Friday minimum: steps 1 to 4 (about 2 hours)

Goal: three flows that ran successfully in a solution, with screenshots. That is enough for the resume line about Power Automate (the resume can say "built" only for flows that actually showed Succeeded).

| Step | Time |
|---|---|
| 1. Developer environment | 15 min |
| 2. Solution | 10 min |
| 3. SharePoint list and Excel table | 25 min |
| 4a. Flow 1 | 35 min |
| 4b. Flow 2 | 20 min |
| 4c. Flow 3 | 15 min |

### Before you start (5 minutes)

1. Create the folder for screenshots if needed: `docs/images/` already exists in the repo.
2. Use a browser profile signed in as user@example.com only (a separate Edge profile avoids mixing accounts).
3. Have `data/kpi_table.csv` and the `flows/` design files open. You will copy values from them.

### Step 1. Power Apps Developer Plan and environment

1. Go to https://aka.ms/PowerAppsDevPlan (it redirects to the developer plan sign-up page).
2. Click **Get started free**, sign in with user@example.com, accept the country and the terms.
3. Wait for the provisioning message. A personal **developer environment** is created for you (name like "Tony's environment").
4. Open https://make.powerautomate.com. Top right, click the **Environment** picker and choose the developer environment.

**Expected:** the environment picker shows the developer environment, and the left menu has **Solutions** and **Approvals**. If the picker only shows "Default", the developer plan sign-up did not finish. Return to step 1 and wait a few minutes. If it still fails, sign in at https://admin.powerplatform.microsoft.com, open Environments, and check for a "Developer" type environment.

Take screenshot `docs/images/01_environment.png` (the environment picker open).

Important to know: a developer environment is for your own building and testing. You cannot share flows with other users for production use, and flows run under your account. That is fine for this demo, and a limitation to state in the README.

### Step 2. Create the solution `HRSelfService`

1. In make.powerautomate.com (developer environment selected), left menu **Solutions**, then **New solution**.
2. Display name: `HRSelfService`. Name: `HRSelfService`.
3. Publisher: click **New publisher**. Display name `Tony Testa`, Name `tonytesta`, **Prefix `hrss`**, Save. Select it.
4. Version `1.0.0.0`. Click **Create**.
5. Open the solution. Click **New > More > Environment variable** and create the six variables in `flows/00_shared_resources.md` (type Text, current value as given, default value the same). The schema names get the `hrss_` prefix automatically, so type only the part after the prefix (for example `HRAnalyticsLeadEmail`).
6. Connection references are created the first time you add an action in a solution flow. If you want them first: **New > More > Connection reference**, one per row of the table in `00_shared_resources.md`. Creating a connection requires you to sign in once for each connector.

**Expected:** the solution lists the six environment variables. Screenshot `docs/images/02_solution.png`.

### Step 3. SharePoint list and Excel KPI table

**3a. SharePoint site and list**

1. Go to https://www.office.com, open **SharePoint**, **Create site**, **Team site**, name it `HR Analytics Demo`, finish. (If the tenant has no SharePoint licence, stop and write it in the results. Without SharePoint, flow 1 can be built with a Dataverse table instead. Tell Claude Code so the design file can be adapted.)
2. In the site, **New > List > Blank list**, name `HR Data Requests`, Create.
3. Add the columns from `flows/00_shared_resources.md` (table "SharePoint list"). For each: **Add column**, choose the type, enter the name **without spaces** (the internal name is fixed at creation, for example `RequestType`), then optionally rename the display name afterwards. Choice columns: paste the choices one per line. Set the defaults (`Status` = New, `Language` = EN, `Source` = Form).
4. Copy the site URL into the environment variable `hrss_SiteUrl` (in the solution).

**Expected:** the list shows all columns. Add one test item with the sample values from the design file, then delete it (the flow does not exist yet).

**3b. Excel KPI table**

1. On your computer, open `data/kpi_table.csv` in Excel. (If accents look wrong in the other CSV files, use Data > From Text/CSV and choose 65001 UTF-8.)
2. Select the data, **Insert > Table**, tick "My table has headers", OK. In **Table Design**, set **Table Name** to `KPI_Table`. Rename the worksheet to `KPI_Table`.
3. Check: Excel shows 2,867 data rows. Rate columns (`voluntary_turnover_rate` and so on) hold numbers like 0.375469.
4. Add a worksheet `Config`, type the header row `key`, `value`, `description` and the three rows from `00_shared_resources.md`. Insert > Table, name it `Config`.
5. Add a worksheet `Alert_Log` with the header row `logged_on`, `period`, `member`, `kpi`, `value`, `threshold` and one empty row, Insert > Table, name `Alert_Log`. (Excel needs a table of at least one row; leave the row empty. Delete the empty row after the first alert lands if you like.)
6. Save as `HR_KPI_Table.xlsx` and upload it to the **Documents** library of the SharePoint site (site > Documents > Upload).
7. Put the path in the environment variable `hrss_KpiFilePath` (for example `/Shared Documents/HR_KPI_Table.xlsx`).

**Expected:** open the file in Excel for the web. In `KPI_Table` filter `period` = `2026-Q3`, `dimension` = `Department`: Operations shows 0.375469, Marketing 0.470588. Filter `member` = `Legal | Quebec City`: `suppressed` = Yes and the rates are blank. Screenshot `docs/images/03_sharepoint_list.png` and `docs/images/03_excel_table.png`.

### Step 4a. Build flow 1 (HR data request with approval)

Follow `flows/01_hr_data_request_with_approval.md` exactly. Short version:

1. Solution `HRSelfService` > **New > Automation > Cloud flow > Automated**. Name `HRSS - 1 HR data request with approval`. Trigger: **When an item is created** (SharePoint). Create.
2. Set the trigger site and list. Add a comment on it.
3. Add two **Scope** actions, `Try` and `Catch`. Build the Try path (set status, compose requester email, start and wait for approval, condition, the two branches). Build the Catch path.
4. On `Catch`: **... > Configure run after**, tick **has failed** and **has timed out**, untick **is successful**. (This is the Power Automate version of an error handler route.)
5. Rename actions as you add them. Add comments (**... > Add a comment**).
6. Save. Fix any red markers (they list missing fields).
7. **Test > Manually > Test**. Go to the SharePoint list and add the sample item. Wait for the run to start (can take up to a minute). Open the **Approvals** page in make.powerautomate.com (left menu **Approvals**, tab **Received**), open the request and click **Approve** with a comment.

**Expected (approve path):** the run page shows every step green and **Succeeded**. List item Status went New, Pending approval, Approved, Delivered. The email arrived in your inbox with both languages and the link. Screenshot `docs/images/flow1_run_approve.png`.

Then repeat for **Reject** (comment "Please narrow the period"): Expected Status Rejected, an email with that reason. Screenshot `docs/images/flow1_run_reject.png`.

Then the **error test** (see the design file, test plan item 3). Expected: Catch runs, Status Error, owner email, run shows **Failed** (that is the correct result for this test). Screenshot `docs/images/flow1_run_error.png`. Restore the setting you changed.

Then the helper flow `HRSS - 1b Submit report request (agent)` from the design file. Test it with a manual trigger run later, when the agent exists.

**Common problems:** the approval email does not arrive (check Approvals page, the Outlook junk folder, and that the approver variable holds a valid email), the trigger does not fire (check the site and list names, wait one minute), "Invalid column" errors (an internal name differs from the design file, fix the action field).

### Step 4b. Build flow 2 (Monday KPI digest)

Follow `flows/02_monday_kpi_digest.md`. Short version: Scheduled cloud flow with Recurrence (weekly, Monday, 8:00, time zone Eastern), initialize variable `topN`, the Try scope with the Excel actions (**List rows present in a table**), Select actions, Compose, Send email, Post message in Teams, and the Catch scope. For Teams, first create a team and channel `HR digest` in Microsoft Teams.

**Expected:** **Test > Manually**: Succeeded. The email and the Teams post show: company headcount 1488, voluntary turnover 15.8%, absence rate 1.9%, average time to fill 48.3 days, and top 3 departments Marketing 47.1%, Operations 37.5%, Risk and Compliance 16.2%. Screenshots `docs/images/flow2_run.png`, `flow2_email.png`.

### Step 4c. Build flow 3 (KPI threshold alert)

Follow `flows/03_kpi_threshold_alert.md`. Create a Teams channel `HR alerts` first.

**Expected:** **Test > Manually**: Succeeded, two Teams posts (Marketing 47.1%, Operations 37.5%) and two rows in `Alert_Log`. Run it again: no new posts. Screenshots `docs/images/flow3_run.png`, `flow3_teams_alert.png`.

**Friday minimum done.** Fill the table in `docs/04_results.md` sections 1 and 5 now, while it is fresh, then commit.

---

## Step 5. Power BI report (about 3 to 4 hours)

1. Install Power BI Desktop (Microsoft Store, free) if needed.
2. Open it, **Get data > Text/CSV**, choose each file from the `data/` folder listed in `powerbi/model.md`. In the preview dialog set **File Origin** to **65001: Unicode (UTF-8)**. Click **Transform Data** for each, set the data types (dates as Date, hours as Decimal Number, flags as Whole Number), rename the query to the Power BI table name, **Close & Apply**.
3. Model view: create the relationships in `powerbi/model.md` (drag column to column, or Manage relationships). Make sure each is Many to One, Single direction. For `fact_requisitions`, make `filled_date` active and `open_date` inactive. Mark `dim_date` as a date table.
4. Create the `Language` table: Home > Enter data, or Modeling > New table with the DATATABLE line in `measures.dax`. Create the `_Measures` table (Enter data, one blank column, then hide it), then add each measure: Modeling > New measure, paste, one measure at a time (the file has comments and blank lines between measures; paste each measure only).
5. Hide the columns listed in `model.md`. Set sort-by columns.
6. Build the pages from `powerbi/report_spec.md`: Overview, Turnover, Absences, Recruiting, Data quality. Add the slicers, sync them across pages (View > Sync slicers).
7. **Check the numbers.** Use the table in `powerbi/report_spec.md` ("Acceptance check") and the table in `docs/04_results.md` section 2. Filter the report to the stated period and member and compare with `data/reference_kpis.csv` (open it in Excel and filter, or open `data/kpi_table.csv`).
8. **Check the privacy rule.** Select Department Legal, Location Quebec City, Quarter 2026-Q3. Every card must show "Not enough data". Then select Legal and Vancouver: values show.
9. Save as `HR_Self_Service_Analytics.pbix`. Put it in `powerbi/` if smaller than 50 MB (GitHub warns above 50 MB and blocks above 100 MB). Otherwise use File > Save as > Power BI Project (.pbip) and commit that folder instead.
10. **Publish** (Home > Publish) to a workspace in your tenant if the licence allows. If it will not publish (no Pro or trial licence), skip it. The README already says this honestly.

**Expected:** at least 10 values match the reference exactly at the shown precision. If a value differs, see "usual causes" in `report_spec.md`. Screenshots in section 7.

**DAX troubleshooting:** if a measure shows an error, check that the table and column names match `model.md` exactly (for example `dim_date[is_month_end]`). Power BI is case insensitive but spaces and underscores matter. Paste measures one at a time so errors are easy to locate.

---

## Step 6. Copilot Studio agent (about 2 hours plus testing)

1. Go to https://copilotstudio.microsoft.com, sign in with user@example.com, choose the developer environment (top right).
2. **Create > New agent**. Name `HR Metrics Assistant`. (Choose the option to configure manually or skip the guided setup, whichever is offered.) Better: create it from inside the `HRSelfService` solution so it is exported with it.
3. Follow `agent/agent_setup.md`: paste the instructions from `agent/instructions.md`, switch **web search off** and **general knowledge off**, add the two knowledge files, wait until they are **Ready**.
4. Add the action from the flow `HRSS - 1b Submit report request (agent)` as described in `agent_setup.md`.
5. Open **Test your agent**. Ask: "What was voluntary turnover in Operations in Q3 2026?" Expected: 37.5%, with the definition and the source.
6. Run every prompt in `agent/test_prompts.csv` following `docs/03_evaluation.md` (new chat for each, except T21 after T20 and T23 after T22). Three runs per prompt for the first full pass. Record Pass or Fail for each in `docs/04_results.md` section 3, and whether flow 1b ran (check the flow run history).
7. When something fails: write the failure in section 4 of the results **first**, then change the instructions or knowledge, then re-run the whole set.

**Expected:** all critical prompts pass, or you have an honest list of failures and fixes. The agent cannot be published without a premium licence. The test chat is enough.

---

## Step 7. Screenshots to take (save in `docs/images/`)

| File name | What it shows |
|---|---|
| `01_environment.png` | Developer environment selected |
| `02_solution.png` | Solution `HRSelfService` with flows, variables, agent |
| `03_sharepoint_list.png` | `HR Data Requests` list with a few items and statuses |
| `03_excel_table.png` | `KPI_Table` with the Operations row |
| `flow1_run_approve.png` | Succeeded run, approve path |
| `flow1_run_reject.png` | Succeeded run, reject path |
| `flow1_run_error.png` | Failed run with the Catch scope executed |
| `flow1_designer.png` | The flow design (Try and Catch scopes visible) |
| `flow2_run.png`, `flow2_email.png` | Digest run and the email |
| `flow3_run.png`, `flow3_teams_alert.png` | Alert run and the Teams post |
| `pbi_overview.png`, `pbi_turnover.png`, `pbi_absences.png`, `pbi_recruiting.png`, `pbi_data_quality.png` | The five pages, default filter (2026-Q3) |
| `pbi_privacy_not_enough_data.png` | Legal and Quebec City selected, "Not enough data" visible |
| `pbi_model.png` | Model view showing the star schema |
| `agent_settings.png`, `agent_knowledge.png` | Web search off, two knowledge sources |
| `agent_test_individual_refusal.png` | A refusal (T13 or T14) |
| `agent_test_confirmation.png` | The request shown and the confirmation question (T20) |
| `agent_test_metric.png` | A correct metric answer (T01) |

Crop out personal information. Everything must show the fictional company and synthetic data. Check the tenant identifier checklist below before committing images (browser address bars show tenant and environment IDs: crop them).

---

## Step 8. Export the solution and unpack it

**8a. Export**

1. make.powerautomate.com > **Solutions** > select `HRSelfService` > **Export solution**.
2. If asked, click **Publish** first, then **Next**. Version `1.0.0.1`. Export type **Unmanaged** (source readable). Export. Wait for the download.
3. Save the downloaded `.zip` as `solution\HRSelfService.zip` inside the repo. The zip from Power Platform already has its files at the top level (no nested folder). If you ever repack it yourself, use `pac solution pack` (below) rather than zipping the folder, so the files stay at the top level.

**8b. Install the Power Platform CLI (PowerShell)**

Check whether you have the .NET SDK:

```powershell
dotnet --version
```

If that fails, install it:

```powershell
winget install Microsoft.DotNet.SDK.8
```

Close and reopen PowerShell, then install the CLI as a .NET tool:

```powershell
dotnet tool install --global Microsoft.PowerApps.CLI.Tool
```

Check it:

```powershell
pac --version
```

Expected: a version number is printed. If `pac` is not found, close and reopen PowerShell (the tools folder `%USERPROFILE%\.dotnet\tools` must be on the path). To update later: `dotnet tool update --global Microsoft.PowerApps.CLI.Tool`.

**8c. Unpack (from the repo root)**

```powershell
cd path\to\hr-self-service-analytics
pac solution unpack --zipfile .\solution\HRSelfService.zip --folder .\solution\unpacked --packagetype Unmanaged --allowDelete true --allowWrite true
```

Expected: the folder `solution\unpacked` contains `Other\Solution.xml`, a `Workflows` folder with a `.json` file per flow, and `environmentvariabledefinitions` (and bot or agent folders if the agent is in the solution). Re-running after a new export updates it, so `git diff` shows exactly what changed in the flows. That is the point of unpacking: flows become reviewable text.

To repack (only if you need to):

```powershell
pac solution pack --zipfile .\solution\HRSelfService_repacked.zip --folder .\solution\unpacked --packagetype Unmanaged
```

---

## Step 9. Remove tenant identifiers before pushing (checklist)

The data is synthetic but the exports contain real identifiers of your tenant. Remove or replace them. Run these checks from the repo root.

1. **Search for your identifiers:**

```powershell
Get-ChildItem -Recurse -File -Exclude *.png,*.zip,*.pbix | Select-String -Pattern 'aitaskworks','sharepoint\.com','dynamics\.com','crm\d*\.','onmicrosoft','tony@' | Select-Object Path,LineNumber,Line
```

2. **Search for GUIDs that identify the tenant or environment** (tenant ID, environment ID, user object IDs, connection IDs). Component GUIDs of your own flows are fine to keep, the others should go:

```powershell
Get-ChildItem .\solution\unpacked -Recurse -File | Select-String -Pattern '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}' | Select-Object Path,LineNumber,Line | Out-GridView
```

3. **Replace** the matches in `solution\unpacked` with placeholders (for example `00000000-0000-0000-0000-000000000000` for tenant and environment IDs, `user@example.com` for emails, `https://example.sharepoint.com/sites/HRAnalyticsDemo` for site URLs). Example for one file:

```powershell
(Get-Content .\solution\unpacked\Workflows\SomeFlow.json -Raw) -replace 'tony@aitaskworks\.com','user@example.com' | Set-Content .\solution\unpacked\Workflows\SomeFlow.json -Encoding utf8
```

4. **Do not** edit `solution\HRSelfService.zip` in place. Either keep the zip as exported (it contains your identifiers, so do **not** push it) or repack from the cleaned folder with `pac solution pack`. The brief lists the zip in the repo structure: push only the repacked, cleaned zip. Files must sit at the zip's top level.
5. **Screenshots:** crop browser address bars, tenant names, email addresses of real people, environment names. Check the Teams and Outlook screenshots for other contacts.
6. **Power BI file:** File > Options > Current file > Privacy, and check the `.pbix` does not carry a workspace name or personal data. If in doubt, push only screenshots and `measures.dax`.
7. **Environment variable current values** in the unpacked solution (`environmentvariablevalues`) contain your email and site URL: replace them.
8. **Final scan** after replacing: rerun the two searches above. They must return nothing for your real values.
9. **Read the git diff** before pushing:

```powershell
git status
git diff --stat
git log --format='%h %an <%ae> %s'
```

Expected: author email `25282736+t-testa@users.noreply.github.com`, no tenant identifiers in the diff.

10. **Push** (from PowerShell, after creating an empty public repo `hr-self-service-analytics` on github.com/t-testa without README):

```powershell
git remote add origin https://github.com/t-testa/hr-self-service-analytics.git
git push -u origin main
```

If you use GitHub CLI instead: `gh repo create t-testa/hr-self-service-analytics --public --source . --push`.

11. **After pushing**, update the README sections marked "To be completed" with real results, add the repo link on the resume only for what actually ran, and push again.
