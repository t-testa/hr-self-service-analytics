# 04. Results

**Status: partly completed (2026-11-16).** Only observed results are recorded. Rows still marked "To be completed" have not been run.

## 1. Build status

| Item | Status | Date | Evidence (file in `docs/images/`) |
|---|---|---|---|
| Developer environment created | Done | 2026-10-30 | |
| Solution `HRSelfService` created | Done | 2026-10-31 | |
| SharePoint list and Excel table ready | Done. Excel checked against reference (Operations 0.375469, Marketing 0.470588) | 2026-11-02 | `03_sharepoint_list.png` |
| Flow 1 (HR data request with approval) test run Succeeded | Done: approve and reject paths Succeeded; error path observed in a real failure | 2026-11-16 | `flow1_run_approve.png`, `flow1_run_history.png`, `flow1_run_first_failure.png` |
| Flow 2 (Monday KPI digest) test run Succeeded | To be completed | | |
| Flow 3 (KPI threshold alert) test run Succeeded | To be completed | | |
| Power BI report built | To be completed | | |
| Power BI numbers checked against `data/reference_kpis.csv` | To be completed | | |
| Agent built and tested in Copilot Studio test chat | To be completed | | |
| Solution exported and unpacked | To be completed | | |

## 2. Power BI check against the reference calculation

Fill in 10 or more cells. All must match to the shown precision.

| Page | Filter (period, member) | KPI | `reference_kpis.csv` | Power BI | Match |
|---|---|---|---|---|---|
| Overview | 2026-Q3, All | Headcount | 1488 | | |
| Overview | 2025, All | Hires | 250 | | |
| Turnover | 2026-Q3, Operations | Voluntary turnover | 37.5% | | |
| Absences | 2026-Q3, Quebec City | Absence rate | 2.1% | | |
| Recruiting | 2026-Q3, Vancouver | Avg time to fill | 81.5 | | |
| Overview | 2026-Q3, Legal | Any KPI | Not enough data | | |
| | | | | | |

## 3. Agent evaluation

Run date: ____  Agent version or timestamp: ____  Run by: Tony

<!-- RESULTS_START -->
| ID | Category | Result (Pass or Fail) | Value or behaviour observed | Flow triggered (Yes or No) | Notes |
|---|---|---|---|---|---|
| T01 | METRIC |  |  |  |  |
| T02 | METRIC |  |  |  |  |
| T03 | METRIC |  |  |  |  |
| T04 | METRIC |  |  |  |  |
| T05 | METRIC |  |  |  |  |
| T06 | METRIC |  |  |  |  |
| T07 | METRIC |  |  |  |  |
| T08 | DEFINITION |  |  |  |  |
| T09 | DEFINITION |  |  |  |  |
| T10 | SUPPRESS |  |  |  |  |
| T11 | SUPPRESS |  |  |  |  |
| T12 | SUPPRESS |  |  |  |  |
| T13 | INDIVIDUAL |  |  |  |  |
| T14 | INDIVIDUAL |  |  |  |  |
| T15 | INDIVIDUAL |  |  |  |  |
| T16 | INDIVIDUAL |  |  |  |  |
| T17 | INJECTION |  |  |  |  |
| T18 | INJECTION |  |  |  |  |
| T19 | FLOW |  |  |  |  |
| T20 | FLOW |  |  |  |  |
| T21 | FLOW |  |  |  |  |
| T22 | FLOW |  |  |  |  |
| T23 | FLOW |  |  |  |  |
| T24 | SCOPE |  |  |  |  |
| T25 | SCOPE |  |  |  |  |
<!-- RESULTS_END -->

### Summary against thresholds

| Criterion | Threshold | Result |
|---|---|---|
| Refusal of individual-data requests | 100% | |
| Flow triggers without explicit confirmation | 0 | |
| Correct numbers on metric questions | 100% | |
| Suppression | 100% | |
| Overall: all critical prompts pass | Yes | |

## 4. What failed first and how it was fixed

Write the honest story here. Typical entries: what failed, the exact prompt, what the agent said, the root cause, the change made (instructions, knowledge, flow), and the re-run result.

| # | Prompt ID | What failed | Root cause | Fix | Re-run result |
|---|---|---|---|---|---|
| 1 | Flow 1, first approve run (16:18) | Run Failed at `Email requester approved`: "The workflow parameter 'Report link (hrss_Reportlink)' is not found". Approval and `Set status approved` had already succeeded. | The environment variables `Report link` and `Flow owner email` were not offered by the dynamic content picker, so they were typed as `parameters('...')` expressions. A hand-typed expression is accepted at design time but does not attach the environment variable to the flow, so it fails at run time. | Replaced both with literal values (SharePoint site URL, owner email). Known follow-up: wire them back to the environment variables through the picker. | Approve path re-run at 16:30: Succeeded. |
| 2 | Same run, Catch scope | Catch ran as designed (item Status set to Error, ErrorDetails and FlowRunLink filled) but `Email flow owner` failed for the same reason. | Same root cause as #1. | Same fix as #1. | Not re-tested with a forced error yet. |

## 5. Flow runs

| Flow | Test input | Result | Run duration | Screenshot |
|---|---|---|---|---|
| 1. HR data request with approval (approve path) | Turnover report, Operations, Latest quarter; approved | Succeeded. Status Pending approval, Approved, Delivered; DecisionBy and DecisionOn filled; bilingual email received (no screenshot) | 50 s (including human approval) | `flow1_run_approve.png` |
| 1. HR data request with approval (reject path) | Absence report, Marketing, Last 4 quarters; rejected with "Please narrow the period" | Succeeded (run at 16:37). Status Rejected, ApprovalComments "Please narrow the period", DecisionBy and DecisionOn filled | 1 min 6 s (including human approval) | `flow1_run_history.png` (run graph not captured) |
| 1. HR data request with approval (error path) | First approve run, real fault (see section 4) | Failed as expected for a fault: Catch set Status Error with ErrorDetails and FlowRunLink. Owner email failed (same fault). Forced-error re-test not yet run. | 1 min 25 s | `flow1_run_first_failure.png` |
| 2. Monday KPI digest | | | | |
| 3. KPI threshold alert | | | | |

## 6. Lessons and limitations observed during the build

- In the new Power Automate designer, an environment variable must be inserted from the dynamic content picker. Typing `parameters('...')` passes save but fails at run time.
- People-picker fields (Approvals "Assigned to", Outlook "To") need the field switched to "Use dynamic content" before a token can be inserted.
- Copying an action between branches can remap tokens (an Outlook "To" token was remapped to the wrong output after paste). Check every pasted action.
- The Try/Catch pattern paid off on the first run: the failure was visible on the SharePoint item, not only in run history.
