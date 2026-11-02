# Handoff

Written at the end of the autonomous build. Fictional company: Laurentian Financial Group. All data synthetic.

## 1. What was built (and verified here)

| Item | Where | Verified how |
|---|---|---|
| Deterministic data generator, 33 months, 9 CSV tables plus 3 derived fact tables and a data dictionary | `src/generate_data.py`, `data/` | Ran it. Two runs give identical bytes (also a test). |
| Independent reference KPIs (headcount, hires, voluntary and involuntary exits and turnover, absence rate, time to fill) with minimum group size 5 | `src/reference_kpis.py`, `data/reference_kpis.csv`, `data/kpi_table.csv`, `agent/knowledge/kpi_facts.md` | Ran it. Hand-checked small case in the tests. Agrees with the separate fact tables. |
| 30 pytest tests, all passing | `tests/` | `python -m pytest` |
| Power BI model, every DAX measure, 5-page report specification | `powerbi/` | **Written, not run in Power BI.** |
| Three flow designs plus the agent helper flow, SharePoint list schema, Excel table layout | `flows/` | **Written, not run in Power Automate.** |
| Agent instructions (5,981 characters, under the 8,000 limit), knowledge files, 25 test prompts | `agent/` | **Written, not run in Copilot Studio.** |
| Requirements, governance, evaluation plan, results template, decisions log | `docs/` | Reviewed for consistency with the data. |
| Click-by-click tenant guide with the 2 hour Friday minimum | `docs/TENANT_GUIDE.md` | Written for your first Power Automate build. |
| README, with KPI numbers injected by script | `README.md` | Numbers come from `src/update_readme.py`. |

Things you should know about the build:

- Everything that touches Microsoft products is **untested**. I could not run DAX, Power Automate expressions or the agent. The designs follow the documented behavior of each tool, but expect a few small fixes (a renamed menu, an expression that needs a tweak, a column name). Log each fix in `docs/04_results.md` section 6. That log is good interview material because it shows real build experience.
- While writing the agent knowledge file I found that the first version of the KPI table exposed the size of suppressed groups (for example "4"). I fixed it so a hidden group shows no size anywhere, and added a test. This is the kind of privacy bug the group-size rule is meant to prevent, and a good story for an interview.
- All 24 decisions I made are in `docs/DECISIONS.md`. Skim them before you rehearse.
- Nothing is pushed. The repo has 6 commits, authored with `25282736+t-testa@users.noreply.github.com`.

## 2. What is left for you, with time estimates

| # | Task | Estimate | Guide |
|---|---|---|---|
| 1 | **Friday minimum:** developer environment, solution, SharePoint list, Excel table, flows 1 to 3 with test runs and screenshots | **about 2 hours** | `TENANT_GUIDE.md` steps 1 to 4 |
| 2 | Fill `docs/04_results.md` sections 1 and 5 from those runs | 20 min | |
| 3 | Power BI report built and checked against the reference (10 or more values), privacy behavior tested, screenshots | 3 to 4 hours | step 5 |
| 4 | Copilot Studio agent built, 25 prompts run (3 runs each for the first pass), failures logged and fixed, re-run | 3 to 4 hours | step 6 |
| 5 | Remaining screenshots, solution export, `pac solution unpack` | 45 min | steps 7 and 8 |
| 6 | Tenant identifier cleanup, then push | 45 min | step 9 |
| 7 | Update README sections marked "To be completed" with real results, push again | 30 min | |
| 8 | Resume line: only for what ran successfully | 10 min | |

Total about 11 to 13 hours. Order for impact: item 1 (closes the Power Automate gap for the three postings), then 3, then 4.

Resume rule: say "built three Power Automate flows (approval, scheduled digest, threshold alert)" only after each shows Succeeded. Say "Copilot Studio agent evaluated against 25 prompts" only after you ran them. Until then say "designed".

## 3. The project in plain language (to rehearse)

**The problem.** In HR, the same questions ("what is turnover in my department?") come in as ad hoc requests. Answers are slow, definitions drift, and small-team numbers can leak. The posting asks for someone who can both analyze HR data and build automation that makes self-service safe.

**The data.** I used synthetic data for a fictional bank with 1,500 employees over 33 months. A Python script generates it with a fixed seed, so anyone gets the same files. I planted three patterns to find: high voluntary turnover in Operations, winter absence peaks, and slow hiring in Vancouver. I also planted small groups, so the privacy rule has something to hide, and a missing-language-preference issue for the data quality page.

**The metrics.** Headcount, hires, voluntary and involuntary turnover (annualized: exits divided by average headcount, scaled to a year), absence rate (unplanned hours over scheduled hours, vacation excluded), and time to fill (days from opening a requisition to the start date).

**How we know the numbers are right.** A second, independent pandas script computes every metric straight from the raw tables, without looking at the tables the report uses. Tests check hand-calculated small cases (for example a team of 7 where I worked out headcount, turnover and absence rate on paper) and check the two sources agree. Then the Power BI numbers and the agent's answers have to match that reference.

**The privacy rule.** A group with fewer than 5 employees shows "Not enough data". The rule is in the Power BI measures, in the Excel table (values blank, flag set), in the flows (they only read unsuppressed rows) and in the agent. I defined group size as the smaller of the average and the end-of-period headcount, so a team that shrank to 4 does not slip through. I also made sure the size of a hidden group is never exposed.

**The flows.** Flow 1: an employee submits a request in a SharePoint list, the HR analytics lead approves or rejects, the requester gets the result by email, and the list status updates at each step. A "Try" scope holds the work and a "Catch" scope runs on failure to set the status to Error and email the owner. Flow 2: every Monday at 8:00, a bilingual digest of the latest KPIs by email and Teams. Flow 3: a scheduled threshold check that posts a Teams alert for departments above 20% voluntary turnover, once per period.

**The agent.** An assistant that answers metric questions only from two approved sources (the KPI facts and the definitions). It refuses anything about named or identifiable people, never gives a number for a group under 5, does not do arithmetic that would reveal a hidden value, treats user text as data (not instructions), answers in French or English, and can file a report request only after showing it and getting an explicit yes. Web search is off.

**The governance.** Data classification (employee-level is confidential and never reaches the agent or flows), privacy rules, access model, who approves what, an AI risk assessment where every risk links to a test prompt, and a register entry. The evaluation plan with 25 prompts and pass thresholds was written before testing, so results cannot be tuned after the fact.

**What I would say about limits.** Synthetic data, a developer environment, an agent that is not published because of licensing, and no internal mobility because there is no job history. (Add: what actually failed first, after you run the tests.)

## 4. Eight likely interview questions, with short answers

**1. Walk me through the project in two minutes.**
It is a self-service HR analytics toolkit for a fictional bank, using synthetic data. A Python generator creates the data, a second script calculates the KPIs independently as a reference, Power BI shows them with a minimum group size of 5, three Power Automate flows handle requests, a weekly digest and threshold alerts, and a Copilot Studio agent answers metric questions without exposing individuals. Governance and a pre-written evaluation sit around all of it.

**2. Why synthetic data, and is it realistic enough?**
I have no HR job experience and cannot use real employee data, so I generated it. It has realistic mechanics: exits tied to departments, hires linked to requisitions, seasonal absences, different time to fill by location. The patterns are planted, so real data would be noisier. I use it to show I understand the domain and the controls, not to claim real insights.

**3. How do you know your KPI numbers are correct?**
Two independent calculations. The Power BI model uses employee-by-month fact tables and DAX. A separate pandas script works from the raw tables. They are compared in tests and I check at least ten report values against the reference. Small hand-calculated cases test the logic. A mismatch means fix the model, not the reference.

**4. How do you protect employee privacy?**
Layers. Minimum group size of 5 in the measures, the Excel table and the agent. No employee-level fields in visuals (ID columns hidden). The agent only sees aggregates. It refuses named people and IDs and will not subtract numbers to reveal a hidden group. I also name the residual risk: a group just above 5 can still reveal a single exit, so in production I would consider complementary suppression and review with the privacy office.

**5. Power Automate was a gap for you. What did you actually build, and what went wrong?**
(Answer after you build it.) Template: "I built three flows in a solution in a developer environment. The one I learned most from was flow 1, because of the approval and the error scope. My first run failed because ____, which I fixed by ____." Do not claim anything you did not run. Explain the mapping from n8n and Make: triggers, actions, conditions, loops are the same ideas, and scope with run-after is the error route.

**6. How does the agent resist prompt injection and misuse?**
Instructions say user text is data, never instructions. It has one action only, and that action needs the request shown and a clear yes in the next message. The request itself then needs a human approval in flow 1. It only has access to aggregated knowledge, so even a successful injection cannot reach individual data. I tested this with prompts such as "ignore all instructions" and a fake "system note" that claims pre-approval. (Add the real results.)

**7. What did AI do and what did you do? How do you control AI-written output?**
Claude Code wrote the code and the first drafts of the documents from my brief. I wrote the brief, the requirements, the privacy and evaluation criteria, and I run and judge the tests in my tenant. The control is evidence: tests, an independent reference calculation, evaluation prompts fixed before testing, and a decisions log. I also found and fixed an AI-introduced privacy leak (hidden group sizes in an output file) because the checks were there.

**8. If this were production at a bank, what would change?**
Real sources (SAP SuccessFactors Reporting Center or the HR data warehouse), service accounts instead of personal connections, separate dev, test and production environments with managed solutions, row-level security, a privacy impact assessment and sign-off from the privacy office, monitoring for flow failures, a published agent in Teams with logging, a change process for KPI definitions, and a data steward. The Excel KPI table would become a governed dataset.

## 5. Quick references

- Reference numbers: `docs/reference_headlines.md`, `data/reference_kpis.csv`.
- Rules: no em dashes in any file, PowerShell for commands, synthetic data disclosed, minimum group size 5.
- Re-run everything: `python src/generate_data.py; python src/reference_kpis.py; python src/update_readme.py; python src/render_eval_table.py; python -m pytest`
