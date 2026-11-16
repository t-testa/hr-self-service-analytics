# 06. Adoption and change plan

Fictional client, synthetic data. The plan assumes the phased rollout in `05_discovery_and_process.md`.

## 1. Change impact by role

| Role | What changes | Size of change | Main concern | Readiness (assumed) |
|---|---|---|---|---|
| HR business partners (about 12) | Stop emailing requests; use the assistant and the request list | Medium | "Will the assistant give me a wrong number I then repeat to a leader?" | Medium |
| Managers (about 120) | Receive a Monday digest; can ask the assistant | Low | "Another email to ignore" | Medium |
| HR analytics team (4) | Approve structured requests; maintain definitions and the KPI table | Medium | "Will this create more work or replace my job?" | High |
| HR analytics lead | Becomes approver and owner of the assistant's knowledge | Medium | Accountability for AI answers | High |

## 2. Role-based adoption strategy

| Audience | Key message | Channel | Enablement | Reinforcement |
|---|---|---|---|---|
| HR business partners | "Common numbers in seconds, same definitions every time, and you can see your request status." | Team meeting demo, pilot invitation | 60 min hands-on workshop, job aid | Weekly office hours for the first 4 weeks; champion in each HRBP pod |
| Managers | "Your team's turnover and absence every Monday, no login." | Email from the sponsor, 5 min demo in leadership meeting | One-page job aid | Digest itself; quarterly reminder |
| HR analytics team | "Fewer one-off emails, more time for real analysis." | Working session with the lead | Walkthrough of flow run history, approval app, knowledge updates | Monthly review of request themes |
| Sponsor | "Faster decisions, consistent numbers, privacy controls we can show." | Executive briefing | None needed | Monthly value report from `07_value_measurement.md` |

## 3. Champions network

- **Who:** 2 HR business partners and 1 HR analytics developer, chosen for credibility with peers, not seniority.
- **What they do:** join the pilot first, run the test prompts on their own questions, answer peer questions in the Teams channel, collect feedback.
- **Support:** early access, 30 min weekly sync with the consultant during the pilot, named in launch communications.

## 4. Workshop outline (60 minutes, HR business partners)

| Time | Segment |
|---|---|
| 0 to 10 | Why we are changing: the current email process, definition drift, the privacy risk |
| 10 to 25 | Live demo: ask three metric questions, see a "Not enough data" refusal, file a request through the assistant with confirmation |
| 25 to 45 | Hands-on: each participant asks two of their real questions and files one test request |
| 45 to 55 | What the assistant will not do (individuals, salary, small groups) and why |
| 55 to 60 | Feedback form, office hours schedule |

## 5. Job aid (one page, bilingual)

1. **Ask:** open the HR Metrics Assistant and ask, for example, "What was voluntary turnover in Operations last quarter?" / « Quel était le roulement volontaire aux Opérations le dernier trimestre? »
2. **Check:** every answer names the period and the definition used.
3. **Small groups:** "Not enough data" means fewer than 5 employees. This is a privacy rule, not an error.
4. **Need more:** ask the assistant to file a request, or add an item to the HR Data Requests list. You will get an email when it is approved or rejected.
5. **Help:** office hours Tuesdays 13:00, or the HR Analytics Teams channel.

## 6. Resistance and mitigations

| Likely resistance | Signal | Mitigation |
|---|---|---|
| "I don't trust AI numbers" | HRBPs keep emailing for confirmation | Show the evaluation results and the reference check; every answer cites the definition; publish accuracy monthly |
| "It refuses too much" | Complaints about "Not enough data" | Explain the privacy rule in the workshop; offer the request route for legitimate needs |
| Analytics team fears loss of role | Low engagement, slow approvals | Position the team as owners of definitions and approvers; track time freed for deeper analysis |
| Managers ignore the digest | Low open rates | Keep it short, bilingual, one table; ask managers in month 2 what they want added |
| Habit: email is easier | Requests still arriving by email | For 4 weeks, reply to emailed requests with a link to the list and a 1 minute guide, then stop answering by email (sponsor decision) |

## 7. Feedback loops and sustainment

- Feedback form after the workshop and at weeks 2 and 6 of the pilot.
- Thumbs up or down and comments reviewed weekly by the HR analytics lead; failed answers become new test prompts (new ID, never editing old ones).
- Monthly: request themes reviewed; recurring requests become new KPIs or report pages.
- Ownership after handoff: HR analytics lead owns knowledge and approvals; M365 admin owns environment and connections; champions own peer support.
