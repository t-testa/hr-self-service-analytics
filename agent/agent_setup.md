# Agent setup in Copilot Studio

Agent name: **HR Metrics Assistant**. Fictional company: Laurentian Financial Group. Synthetic data only. Built in your demo tenant (user@example.com), in the `HRSelfService` solution if the option is offered when you create it (create the agent from inside the solution).

Copilot Studio changes its menus often. Names below follow the current layout. If a name differs, look for the equivalent and note the difference in `docs/04_results.md` section 6.

## Settings

| Setting | Value |
|---|---|
| Name | HR Metrics Assistant |
| Description | See `agent/instructions.md` |
| Instructions | The block in `agent/instructions.md` between PASTE START and PASTE END |
| Orchestration | Generative (the agent decides which knowledge and action to use) |
| Web search | **Off** (Settings > Generative AI, or the Web Search toggle on the Overview page) |
| General knowledge (use information from the model's own knowledge) | **Off** |
| Content moderation | High, if the option exists |
| Authentication | Authenticate with Microsoft (default for the test chat) |
| Channels | None published. The agent is used in the **Test your agent** chat only (publishing needs a premium licence). |

## Knowledge (add exactly two sources)

| Source | File | How |
|---|---|---|
| KPI facts | `agent/knowledge/kpi_facts.md` (about 270 KB, one line per period and group) | Knowledge > Add knowledge > Files > upload. Name it "KPI facts". Description: "Aggregated quarterly and yearly HR metrics by department, location, job level. Values below minimum group size are marked NOT ENOUGH DATA." |
| Metric definitions | `agent/knowledge/metric_definitions.md` | Same. Name "Metric definitions". Description: "Definitions of headcount, hires, exits, turnover, absence rate and time to fill." |

If the upload rejects `.md`, rename the files to `.txt` (content is plain text) and note it in the results. Wait until both files show as **Ready** before testing. Do not add SharePoint, websites or other sources.

If answers about numbers are unreliable (retrieval over many similar lines can pick the wrong line), try these fixes in this order and log each one:
1. Ask for the exact period and group in the instructions (already there), and test again.
2. Split `kpi_facts.md` into one file per period (`2026-Q3.md`, and so on) and upload only the periods you need.
3. Replace the file with a Dataverse table or an Excel table knowledge source of `data/kpi_table.csv` (see `docs/04_results.md`).

## Action: Submit report request

Create from the flow `HRSS - 1b Submit report request (agent)` (it must be in the same solution): Actions > Add an action > choose the flow. Settings:

| Field | Value |
|---|---|
| Name | Submit report request |
| Description | Submits a report request to the HR analytics lead for approval. Call only after the user has seen the full request and explicitly confirmed it in their last message. |
| Inputs | `RequestType`, `Department`, `Period`, `BusinessReason`, `Language`, `RequesterEmail` (all text) |
| Input descriptions | Use the allowed values from `flows/00_shared_resources.md` in each description, for example "One of: Turnover report, Absence report, Recruiting report, Headcount report, Other". |
| RequesterEmail | Set to be filled from the signed in user's email (system variable `User.Email` or the equivalent) and not asked from the user. In the test chat it is your own account. |
| Output | `Result` (text) |
| Ask the user for confirmation before running | Turn on the action's own **user confirmation** setting if it exists, as an extra layer. The instructions already enforce confirmation. |

## Topics

Leave the system topics. Do not add custom topics. (Optional later: a Conversation start greeting in English and French.) Set the **Conversation start** message to:

> Hello, I am the HR Metrics Assistant (synthetic demo). I answer aggregated HR metric questions from approved sources, in English or French. I never share information about individuals. / Bonjour, je suis l'assistant des indicateurs RH (démo synthétique). Je réponds aux questions sur les indicateurs RH agrégés à partir de sources approuvées, en français ou en anglais. Je ne partage jamais d'information sur des personnes.

## After building

1. Run all prompts in `agent/test_prompts.csv` following `docs/03_evaluation.md`.
2. Record results in `docs/04_results.md`.
3. Screenshot the Overview page (showing web search off) and the Knowledge page as `docs/images/agent_settings.png` and `docs/images/agent_knowledge.png`. Take a screenshot of the test chat for each failure and for the first full pass.
