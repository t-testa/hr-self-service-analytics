# 04. Results

**Status: to be completed.** Nothing in this file has been run yet. Every table below is empty on purpose. Fill it in from the tenant work (`docs/TENANT_GUIDE.md`). Do not fill in a result that was not observed.

## 1. Build status

| Item | Status | Date | Evidence (file in `docs/images/`) |
|---|---|---|---|
| Developer environment created | To be completed | | |
| Solution `HRSelfService` created | To be completed | | |
| SharePoint list and Excel table ready | To be completed | | |
| Flow 1 (HR data request with approval) test run Succeeded | To be completed | | |
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
| 1 | | | | | |

## 5. Flow runs

| Flow | Test input | Result | Run duration | Screenshot |
|---|---|---|---|---|
| 1. HR data request with approval (approve path) | | | | |
| 1. HR data request with approval (reject path) | | | | |
| 1. HR data request with approval (forced error path) | | | | |
| 2. Monday KPI digest | | | | |
| 3. KPI threshold alert | | | | |

## 6. Lessons and limitations observed during the build

To be completed.
