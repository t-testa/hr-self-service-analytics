# 01. Requirements

Fictional company: Laurentian Financial Group (about 1,500 employees, Montreal, Quebec City, Toronto, Vancouver). All data is synthetic.

## Problem

HR questions ("What is turnover in my department?", "How long do we take to hire in Vancouver?") reach the HR analytics team as ad hoc emails. Answers take days, definitions drift between answers, and small-group numbers sometimes go out without any privacy check. The goal is self-service: trusted dashboards, a governed way to ask for what is missing, and an assistant that answers common metric questions safely.

## Personas

| Persona | Who | Needs | Worries |
|---|---|---|---|
| **Isabelle, HR business partner** | Supports 3 departments, prepares workforce reviews. | Fast, consistent numbers by department and location. A way to ask for a deeper report. | Quoting a number that is wrong or that exposes a small team. |
| **Marc, manager** | Runs a 40 person team in Operations. | A quick view of his department's turnover and absence. A weekly summary without logging in anywhere. | Not knowing if a number is "bad". Wasting time on definitions. |
| **Sophie, HR analytics lead** | Owns the KPI definitions and the report catalogue. Approves custom report requests. | One source of truth. Requests that arrive structured, with a purpose. An audit trail. Early warning when a KPI crosses a threshold. | Privacy incidents. Shadow reports. Manual rework. |

## Scope

In scope: KPI model and report, three automated flows, a metric assistant, governance and evaluation.
Out of scope: real HR systems (SAP SuccessFactors), salary and performance data, individual-level reporting, production deployment, publishing the agent to channels.

## User stories and acceptance criteria

### Reporting (Power BI)

**US-01 Overview.** As Isabelle, I want company and department headcount, hires, turnover, absence and time to fill on one page so that I can prepare a review quickly.
- Given the Overview page, when I filter by department and period, then every KPI recalculates and matches `data/reference_kpis.csv` to the shown precision.
- Headcount, hires, turnover, absence and time to fill are all visible without scrolling at 1080p.

**US-02 Turnover.** As Isabelle, I want voluntary and involuntary turnover by department, location and job level, with a monthly trend.
- Voluntary turnover is annualized using the definition in `agent/knowledge/metric_definitions.md`.
- Operations is visibly higher than other departments in 2025 and 2026.

**US-03 Absences.** As Marc, I want the absence rate by month and location so that I can see seasonal patterns.
- Vacation is not counted. Winter months show higher rates than summer months.

**US-04 Recruiting.** As Isabelle, I want average time to fill by location and job level.
- Vancouver is clearly longer than other locations.
- A visual with fewer than 5 filled requisitions shows "Not enough data".

**US-05 Data quality.** As Sophie, I want checks on missing and inconsistent data.
- The page lists missing language preference (planted, expected above zero), terminations before hire (expected zero), unknown department or location keys (expected zero), and the number of suppressed groups.

**US-06 Minimum group size.** As Sophie, I want any group under 5 employees to show "Not enough data" instead of a number.
- Given a filter that leaves fewer than 5 employees, every KPI card and chart label shows "Not enough data".
- Given a table or matrix, the suppressed cells show the same text, not blank and not 0.
- No visual or tooltip exposes `employee_id`.

### Automation (Power Automate)

**US-07 Report request.** As Isabelle, I want to submit a request for a report in a SharePoint list so that my ask is recorded and routed.
- A new list item starts flow 1. Status moves New, Pending approval, then Approved or Rejected. A failure sets status Error and notifies the flow owner.
- On approval the requester receives an email with the report link. On rejection the requester receives the approver's reason.
- Each step writes the status back to the list item.

**US-08 Weekly digest.** As Marc, I want a short bilingual KPI summary every Monday at 8:00 so that I do not need to open a dashboard.
- Flow 2 runs on schedule, reads the latest quarter from the KPI table, and posts or emails the digest. Suppressed values are never shown.
- A manual test run of flow 2 succeeds.

**US-09 Threshold alert.** As Sophie, I want a Teams alert when annualized voluntary turnover in a department crosses a threshold.
- Flow 3 checks the latest quarter. For each department above the threshold with `suppressed = No`, it posts the department name and value.
- The threshold lives in a configuration table, not inside the flow.

### Assistant (Copilot Studio)

**US-10 Metric questions.** As Marc, I want to ask "What was voluntary turnover in Operations in Q3 2026?" in English or French and get the right number with its definition.
- Numbers match `data/kpi_table.csv`. The answer names the metric definition used and the period.

**US-11 Privacy by design.** As Sophie, I want the assistant to refuse anything about an identifiable person and to show "Not enough data" under 5 employees.
- 100 percent refusal of individual-data prompts in `agent/test_prompts.csv`.

**US-12 Request a report.** As Isabelle, I want to ask the assistant to file a report request so that I do not fill a form.
- The assistant shows the request, asks for explicit confirmation, and starts flow 1 only after a clear yes. Zero flow starts without confirmation.

**US-13 Honest scope.** As Sophie, I want the assistant to say when its sources do not cover a question.
- Salary, performance, named people and web questions get a clear "not covered" answer.

### Governance

**US-14 Documented governance.** As Sophie, I want a register entry, data classification, access model and AI risk assessment so that the solution can be reviewed.
- `docs/02_governance.md` contains all four, plus who approves what.

**US-15 Repeatable evaluation.** As Sophie, I want written test prompts with thresholds defined before testing.
- `docs/03_evaluation.md` and `agent/test_prompts.csv` exist and were committed before any result was recorded.

## Non-functional requirements

- Bilingual (English and French) labels in the report and agent answers.
- All data synthetic and disclosed as such everywhere.
- No individual-level data reachable by the agent or by the flows.
- Numbers reproducible: one command regenerates the data and the reference KPIs.
- Built with free or developer-plan tooling.
