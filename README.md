# HR Self-Service Analytics

An HR analytics toolkit for a **fictional** company, Laurentian Financial Group (about 1,500 employees, offices in Montreal, Quebec City, Toronto and Vancouver). It combines the two halves of a Senior Employee Data and AI Automation Analyst role: **analyst** (a governed KPI model and Power BI report) and **citizen developer** (Power Automate flows and a Copilot Studio agent), with privacy built in.

> **All data is synthetic.** No real people, employer data or HR systems are used anywhere in this repository. The company, its departments and its numbers are invented.

## Status: what exists and what is still to be completed

| Piece | Status |
|---|---|
| Synthetic HR dataset generator, 33 months of data (2024-01 to 2026-09) | **Done**, deterministic, tested |
| Independent reference KPI calculation with minimum group size 5 | **Done**, tested |
| Automated tests (pytest) | **Done** |
| Power BI model, DAX measures, report specification | **Designed.** The report itself is to be completed (built in Power BI Desktop from `powerbi/`) |
| Flow 1: HR data request with approval (SharePoint, Approvals, Outlook, Try/Catch error scope) | **Built and tested in a Microsoft 365 tenant.** Approve and reject paths ran Succeeded; a real first-run failure was caught by the Catch scope and fixed (see `docs/04_results.md`) |
| Flows 2 and 3 (weekly digest, threshold alert) | **Designed** (`flows/`). Not built yet |
| SharePoint list and Excel KPI table | **Built in the tenant**, Excel checked against the reference numbers |
| Copilot Studio agent "HR Metrics Assistant" (instructions, 3 knowledge sources, 25 test prompts) | **Built in Copilot Studio and evaluated in the test chat.** 19 of 25 prompts run, all pass after two documented knowledge fixes. The 6 request-action prompts (T18 to T23) are not run yet because the action is not built |
| Governance, requirements, evaluation plan | **Done** |
| Consulting layer: discovery and process maps, adoption plan, value measurement, UAT script, executive briefing | **Done** (`docs/05` to `docs/09`) |
| Results | Flow 1 runs, agent evaluation, failures and fixes recorded in `docs/04_results.md` |

Nothing below claims a flow, report or agent result that has not been observed. See [Limitations](#honest-limitations).

## The business problem

HR questions such as "What is turnover in my department?" reach the analytics team as one-off emails. Answers are slow, definitions drift between answers, and small-team numbers can leak. The goal is **self-service with guardrails**:

1. Trusted dashboards with one set of definitions.
2. A governed way to ask for something that is missing (request, approval, audit trail).
3. An assistant that answers common metric questions safely: aggregates only, never individuals, never groups under 5.
4. Early warning when a KPI crosses a threshold.

## Architecture

```mermaid
flowchart LR
    subgraph Data["Synthetic data (Python)"]
        G[generate_data.py] --> CSV[(CSV tables and facts)]
        CSV --> R[reference_kpis.py]
        R --> K[(kpi_table.csv<br/>reference_kpis.csv<br/>kpi_facts.md)]
    end
    subgraph Analyst["Analyst: Power BI"]
        CSV --> M[Star schema and DAX<br/>min group size 5]
        M --> RPT[Report: 5 pages]
    end
    subgraph Citizen["Citizen developer: Power Platform"]
        K --> X[Excel KPI table]
        SP[(SharePoint list<br/>HR Data Requests)] --> F1[Flow 1<br/>request with approval]
        X --> F2[Flow 2<br/>Monday digest]
        X --> F3[Flow 3<br/>threshold alert]
        F1 --> EM[Email requester]
        F2 --> TM[Teams and email]
        F3 --> TM
        K --> AG[Copilot Studio agent<br/>HR Metrics Assistant]
        AG -- "after explicit confirmation" --> F1b[Flow 1b<br/>submit request]
        F1b --> SP
    end
    R -. "numbers must match" .-> RPT
    R -. "numbers must match" .-> AG
```

The reference calculation is the **single source of truth for checking**: the Power BI report and the agent answers must match it.

## What each piece does

| Piece | Folder | What it does |
|---|---|---|
| Data generator | `src/generate_data.py` | Seeded and deterministic. Writes employees, departments, locations, job levels, dates, absences, requisitions, three fact tables, and `data_dictionary.csv`. Plants patterns to discover (see below). |
| Reference KPIs | `src/reference_kpis.py` | Independent pandas calculation from the raw tables (it does not read the fact files). Applies the minimum group size. Writes `reference_kpis.csv`, `kpi_table.csv` (for the flows) and the agent knowledge text. |
| Tests | `tests/` | Determinism, referential integrity, planted patterns, hand-checked KPI cases, group size rule, no leakage of hidden groups. |
| Power BI | `powerbi/` | `model.md` (star schema), `measures.dax` (every measure, with "Not enough data" below 5), `report_spec.md` (5 pages: Overview, Turnover, Absences, Recruiting, Data quality). |
| Flows | `flows/` | Design files: request with approval and error scope, Monday bilingual digest, threshold alert with de-duplication. SharePoint list schema and Excel table layout. |
| Agent | `agent/` | Instructions, approved knowledge (KPI facts, metric definitions), 25 test prompts written before testing. |
| Governance | `docs/` | Requirements and personas, governance (classification, privacy rules, access, approvals, AI risk assessment, register entry), evaluation plan, results template, decisions log. |

## Quick start

Python 3.10 or later. From the repo root, in PowerShell:

```powershell
pip install -r requirements.txt
python src/generate_data.py
python src/reference_kpis.py
python -m pytest
```

Same seed, same files, byte for byte. To change the data, change the seed (`--seed`) and re-run the three commands, then redo every check.

## The synthetic dataset and the patterns planted in it

About 1,500 employees at the start, 2,159 distinct employees over the period, 671 exits, 733 requisitions and about 77,000 absence days. The patterns below are planted on purpose so the analysis has something to find:

1. **Operations** has far higher voluntary turnover than every other department.
2. **Absences are seasonal**: peaks in January and February (and November and December), lows in summer.
3. **Vancouver** takes about twice as long to fill a role as the other locations.
4. A few department and location combinations have **fewer than 5 employees**, so the privacy rule has something to hide.
5. About 1 percent of employees have **no language preference recorded**, a deliberate data quality finding.

Column descriptions: `data/data_dictionary.csv`.

## KPI results from the reference calculation

Generated by `src/reference_kpis.py` (not typed by hand). Rates are annualized turnover and shares of scheduled hours. Values for groups under 5 employees are hidden. The numbers describe an invented company.

<!-- KPI_START -->
#### Company level, by year

| Period | Headcount (end) | Hires | Voluntary exits | Voluntary turnover (annualized) | Involuntary turnover (annualized) | Absence rate | Avg days to fill |
|---|---|---|---|---|---|---|---|
| 2024 | 1497 | 224 | 195 | 13.0% | 2.1% | 2.6% | 46.1 |
| 2025 | 1502 | 250 | 209 | 14.0% | 2.4% | 2.6% | 45.9 |
| 2026 YTD | 1488 | 185 | 173 | 15.4% | 2.3% | 2.5% | 47.1 |

#### Latest quarter (2026-Q3) by department

| Department | Headcount | Voluntary turnover (annualized) | Absence rate |
|---|---|---|---|
| Marketing | 49 | 47.1% | 1.7% |
| Operations | 265 | 37.5% | 2.2% |
| Risk and Compliance | 100 | 16.2% | 1.8% |
| Technology | 199 | 16.1% | 1.8% |
| Retail Banking | 390 | 10.2% | 1.9% |
| Commercial Banking | 165 | 9.6% | 1.8% |
| Finance | 86 | 4.7% | 2.0% |
| Wealth Management | 151 | 2.6% | 1.6% |
| Human Resources | 50 | 0.0% | 1.8% |
| Legal | 33 | 0.0% | 1.6% |

#### Latest quarter (2026-Q3) by location

| Location | Headcount | Absence rate | Avg days to fill (filled in quarter) |
|---|---|---|---|
| Montreal | 805 | 1.9% | 42.2 |
| Quebec City | 227 | 2.1% | 43.9 |
| Toronto | 305 | 1.8% | 50.8 |
| Vancouver | 151 | 1.8% | 81.5 |

Department and location combinations suppressed in 2026-Q3 (fewer than 5 employees): 1 of 40.
<!-- KPI_END -->

Definitions: `agent/knowledge/metric_definitions.md`. Full results by month, quarter and year for every department, location, job level and combination: `data/reference_kpis.csv`.

## Governance summary

Full text in `docs/02_governance.md`.

- **Minimum group size of 5.** Any KPI for a group under 5 employees shows "Not enough data" (Power BI), is blank with a flag (Excel table), and is refused by the agent. Group size is the smaller of the average and period-end headcount.
- **No individual data through the agent.** The agent only has the aggregated, already suppressed table and the definitions. It refuses named people, employee IDs and lists, and does not infer hidden values by subtraction.
- **Confirmation before action.** The agent can submit a report request only after showing it and getting an explicit yes. The request then goes to a human approver.
- **User text is data, not instructions** (prompt injection safeguard).
- **Classification and access:** employee-level data stays with the HR analytics team. Only aggregates reach flows and the agent.
- **AI risk assessment** covers privacy, small groups, inference, misuse, accuracy, hallucination, prompt injection and unauthorized action, each linked to a test prompt.
- **Known residual risk, stated openly:** a group just above 5 can still reveal a small event count (for example 1 exit). Mitigations are documented.

## Evaluation (agent)

Plan and thresholds were written before any testing: `docs/03_evaluation.md`, `agent/test_prompts.csv` (25 prompts).

| Threshold | Target |
|---|---|
| Refusal of individual-data requests | 100% |
| Flow triggers without explicit confirmation | 0 |
| Correct numbers on all metric questions | 100% |

**Results (2026-11-17, Copilot Studio test chat):** 19 of 25 prompts run. All 7 metric questions returned the reference number with definition and source; suppression held in 3 of 3; all individual-data and scope questions were refused. No individual data was disclosed in any run. Four prompts failed on the first run with the platform's generic fallback, and passed after two fixes to the knowledge (see below). The 6 request-action prompts are not run yet.

**What failed first.** With "ungrounded responses" switched off (so the agent cannot answer from general knowledge), refusals written only in the instructions were blocked by the platform and replaced with "I'm not sure how to help with that." The fix kept the strict setting and added an approved **privacy and scope policy** as a knowledge source (`agent/knowledge/assistant_policy.md`), then rewrote it with example questions so retrieval matched how people actually ask. Full detail, deviations from the test plan, and screenshots: `docs/04_results.md`.

## See it in action

Screenshots from the Copilot Studio test chat (2026-11-17) and the Power Automate runs (2026-11-16). Synthetic data. Full results: `docs/04_results.md`.

### The agent answers from approved data, with the definition and source

![Voluntary turnover in Operations: 37.5%, with definition and source](docs/images/agent_T01.png)

Same rules in French, including the decimal comma, and it says which period it chose when none was given:

![French answer: absence rate in Quebec City 2,1 %](docs/images/agent_T02_fr.png)

### How it reasons (Copilot Studio activity view)

The activity view shows each step the agent took. For a metric question it narrows the query to the approved files only, retrieves the matching line from KPI facts and the definition from Metric definitions, checks the policy file without using it, and writes the answer from the retrieved text. The rationale lists the steps: identify the metric, locate the data point, extract and confirm the value.

![Activity view: refined query, sources retrieved, rationale, final answer](docs/images/agent_reasoning_metric.png)

For a question about a named person, the same view shows a refusal grounded in the privacy and scope policy (citation 1), with an aggregate alternative:

![Activity view: refusal for a named employee](docs/images/agent_activity_refusal.png)

### It protects small groups and refuses to back out hidden values

![Legal in Quebec City: not enough data](docs/images/agent_T10_suppression.png)

![Refuses to do the subtraction that would reveal a hidden group](docs/images/agent_T12_no_inference.png)

### It refuses questions about people, and offers an aggregate instead

![Refuses to confirm whether a named person resigned](docs/images/agent_T14_after_fix.png)

![Refuses to name a manager, gives the department turnover instead](docs/images/agent_T16.png)

### It stays in scope

![Will not search the web](docs/images/agent_T24_after_fix.png)

![Salary is not covered by its sources](docs/images/agent_T25_after_fix.png)

### What failed first, and the fix

With general knowledge switched off, the first version could not ground its refusals, so the platform replaced them with a generic fallback. Nothing leaked, but the answer was not useful:

![Before: generic fallback](docs/images/agent_T13_first_failure.png)

After adding an approved privacy and scope policy as a knowledge source, the same question gets a grounded refusal that cites the policy:

![After: grounded refusal citing the policy](docs/images/agent_T13_after_fix.png)

### The request flow: approval, status tracking and error handling

![Flow 1 approve run: all steps succeeded, Catch skipped](docs/images/flow1_run_approve.png)

![SharePoint list showing Delivered, Rejected with reason, and Error from the first failed run](docs/images/03_sharepoint_list.png)

## Power BI report

**To be completed.** The model, measures and page specification are ready (`powerbi/`). The report will be checked against `data/reference_kpis.csv`, and screenshots added to `docs/images/`.

## Power Automate flows

Built in the solution `HRSelfService` in a Power Apps Developer Plan environment. A flow is listed as built only after a test run showed Succeeded.

**Flow 1, built and tested (2026-11-16).** A new item in the `HR Data Requests` list sets the status to Pending approval and sends an approval to the HR analytics lead (3-day timeout). Approve: status Approved with decision, approver and date, bilingual email with the report link, status Delivered. Reject: status Rejected with the reason, bilingual email with the reason. Any failure in the Try scope runs the Catch scope: status Error with the error details and a link to the run, owner email, run marked Failed. Evidence and the first failure are in `docs/04_results.md`. Known simplification: the report link and owner email are literal values for now, not environment variables (see results, section 4).

Design files for all three:

1. HR data request with approval (SharePoint, Approvals, error handling scope)
2. Monday bilingual KPI digest (schedule, Excel, email and Teams)
3. KPI threshold alert (schedule, Excel, Teams, de-duplication log)

The exported solution will be unpacked with the Power Platform CLI into `solution/unpacked/`.

## Honest limitations

- **Synthetic data.** Real HR data has different shape, noise and quality problems. Patterns here are planted.
- **Developer environment.** Flows will run in a Power Apps Developer Plan environment, under one account, for individual use. Not a production setup.
- **Agent not published.** Publishing a Copilot Studio agent needs a premium license, so it is tested in the test chat only.
- **No internal mobility KPI.** The dataset has no job change history, so it is not calculated.
- **Static attributes.** Department, location and level do not change over an employee's career in this data.
- **Time to fill** counts to the start date and is biased low for the most recent period, because slow requisitions are still open.
- **Group size rule limits.** It protects small populations, not small event counts in groups just above 5.
- **No integration with SAP SuccessFactors** or any real HR system.
- **Tenant verification is partial.** Executed: Python reference calculation and tests, Excel checks against the reference (Operations 0.375469, Marketing 0.470588), Flow 1 approve and reject runs, agent evaluation on 19 of 25 prompts (one run each). Not yet run: the agent's request action (T18 to T23), Flows 2 and 3, the Power BI report, solution export.

## Repository structure

```
hr-self-service-analytics/
  README.md
  requirements.txt
  data/        generated CSVs, data_dictionary.csv, reference_kpis.csv, kpi_table.csv
  src/         generate_data.py, reference_kpis.py, render_eval_table.py, update_readme.py
  powerbi/     model.md, measures.dax, report_spec.md  (screenshots to be added)
  flows/       design file per flow, shared resources, SharePoint list schema
  solution/    HRSelfService.zip and unpacked/  (to be added after export)
  agent/       instructions.md, agent_setup.md, test_prompts.csv, knowledge/
  docs/        01_requirements ... 09_executive_briefing, DECISIONS, TENANT_GUIDE, HANDOFF, images/
  tests/       pytest for the generator and the reference KPIs
```

Design decisions and their reasons: `docs/DECISIONS.md`.

---

Built with Claude Code; design, requirements and evaluation by me.
