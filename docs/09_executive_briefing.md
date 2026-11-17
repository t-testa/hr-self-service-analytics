# 09. Executive briefing: HR self-service with guardrails

Fictional client (Laurentian Financial Group), synthetic data. One page for the sponsor.

**The problem.** HR metric questions arrive as one-off emails. Answers take days, the same metric comes back with different numbers, and small-team figures can expose individuals. There is no record of who asked for what, or why.

**The recommendation.** Self-service with guardrails, built on the Microsoft 365 tools the company already has:

1. **Governed request process** (Power Automate, SharePoint, Approvals): every custom request records its purpose, goes to the HR analytics lead for approval, and updates its status automatically. Failures are flagged, not lost.
2. **Weekly bilingual KPI digest** to managers (Power Automate, Outlook, Teams).
3. **HR Metrics Assistant** (Copilot Studio): answers common metric questions from approved data only, refuses individual data and groups under 5 employees, and files a request only after the user confirms.

**Why this approach.** It covers ad hoc, routine and proactive needs, keeps a human approver in the loop, and enforces the privacy rule in the data, the flows and the assistant rather than relying on memory.

**Expected value (assumptions to be confirmed with a measured baseline).** About 60% fewer emailed requests, answers to common questions in under a minute instead of about 3 days, roughly 200 analyst hours a year returned to real analysis, and a full audit trail for custom requests.

**Risks and controls.**

| Risk | Control |
|---|---|
| Wrong AI answer | Approved sources only; definition and period cited; 25 written test prompts with 100% accuracy target before release |
| Privacy breach | Minimum group size 5 built into the data; individual questions refused; no row-level data reachable |
| Action without consent | Assistant has one action, gated by explicit confirmation and a human approval |
| Low adoption | Champions, workshop, job aid, office hours, sponsor message |

**Status of the prototype.** Request flow with approval, status tracking and error handling built and tested (approve path run Succeeded). KPI model and privacy rule built and tested. Assistant built in Copilot Studio and evaluated: 19 of 25 test prompts run, all passing after two documented fixes, no individual data disclosed. Request action and weekly digest designed, not yet built.

**Decisions needed.** (1) Approve a 10-week phased rollout. (2) Name the HR analytics lead as process owner. (3) Confirm Copilot Studio licensing for the pilot group. (4) Privacy officer sign-off on the group size rule.
