# 07. Value measurement

Fictional client, synthetic data. **Every baseline figure below is an assumption** for a 1,500-employee company, labelled as such. In a real engagement the baseline would be measured during discovery (two to four weeks of counting requests in the shared inbox and timing a sample).

## 1. Success criteria

| Area | Metric | Baseline | Target (90 days after launch) | Source |
|---|---|---|---|---|
| Process performance | Ad hoc metric requests emailed to HR analytics per month | 60 (assumption) | 25 or fewer | Shared inbox count |
| Process performance | Median turnaround from request to answer | 3 business days (assumption) | Under 1 minute for common metrics; 2 business days for custom reports | Assistant transcripts; SharePoint Created vs DecisionOn |
| Process performance | Analyst hours spent on one-off requests per month | 30 hours (assumption: 60 requests x 30 min) | 12 hours or fewer | Time sample |
| Governance | Custom requests with purpose and approval recorded | 0% (assumption: email only) | 100% | SharePoint list |
| Solution quality | Correct numbers on metric test prompts | Not applicable | 100% | `03_evaluation.md` prompts T01 to T07 |
| Solution quality | Refusal of individual-data and small-group prompts | Not applicable | 100% | Prompts T10 to T16 |
| Solution quality | Flow starts without explicit confirmation | Not applicable | 0 | Prompts T18 to T23, flow run history |
| Adoption | Active assistant users per month | 0 | 70% of HRBPs, 30% of managers | Copilot Studio analytics |
| Adoption | Digest open rate | 0 | 50% or higher | Email reporting |
| User experience | Satisfaction (1 to 5) | Not measured | 4.0 or higher | Pilot survey |

## 2. Value estimate (assumption-based)

| Item | Calculation | Value |
|---|---|---|
| Analyst time freed | (30 to 12 hours) x 12 months | 216 hours per year |
| Requester time saved | 35 fewer emailed requests per month x 20 min of back-and-forth x 12 | 140 hours per year |
| Privacy risk reduction | Group size rule enforced by design instead of by memory | Not monetized; reported as a control |

These figures are directional. The real case would be rebuilt from the measured baseline.

## 3. How it is monitored

| Cadence | What | Owner |
|---|---|---|
| Weekly (pilot) | Failed or thumbs-down answers, new test prompts | HR analytics lead |
| Monthly | Requests, turnaround, adoption, accuracy re-check of 5 random answers against `reference_kpis.csv` | Consultant, then HR analytics lead |
| Quarterly | Value narrative for the sponsor; decide next use cases | Sponsor and HR analytics lead |

## 4. Evidence collected in this prototype (observed, not assumed)

| Item | Result | Where |
|---|---|---|
| Reference KPIs reproducible and tested | 30 pytest tests pass | `tests/` |
| Excel KPI table matches reference | Operations 0.375469, Marketing 0.470588 | `04_results.md` |
| Flow 1 approve and reject paths | Runs Succeeded on 2026-11-16 | `04_results.md`, `images/flow1_run_approve.png` |
| Agent accuracy on metric questions | 7 of 7 correct (T01 to T07) | `04_results.md` section 3 |
| Agent refusal of individual-data and out-of-scope questions | 100% after two knowledge fixes; no disclosure in any run | `04_results.md` sections 3 and 4 |

Results come from one run per prompt on 2026-11-17. The request-action prompts (T18 to T23) are not run yet.
