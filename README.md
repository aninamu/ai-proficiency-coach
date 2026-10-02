# AI Proficiency Coach

A Cursor plugin with one coaching skill. It shows an engineer, eng leader or PM where they sit on a four-level AI proficiency framework (PL1-PL4), based on their Cursor usage metadata. Then it gives one or two concrete Cursor next steps for the week and one thing to avoid.

The skill is **manual-only** (`disable-model-invocation: true`). Agent never applies it on its own; it runs only when you invoke it. In Agent chat, type `/ai-proficiency-coach` followed by your question:

```text
/ai-proficiency-coach How am I doing with AI? Here's my weekly row: <paste or @-mention the file>
/ai-proficiency-coach How do I get to PL3?
/ai-proficiency-coach Here's my team's export. What's our PL mix, and who's never engaged?
/ai-proficiency-coach I have no data. Can we do a quick self-assessment?
```

The skill is grounded in one framework (`skills/ai-proficiency-coach/references/framework.md`) and one input contract (`references/data-contract.md`). A dependency-free scorer (`scripts/score.py`) applies the gates, so levels are computed the same way every time.

## Framework at a glance

| | PL1 | PL2 | PL3 (org target) | PL4 |
|---|---|---|---|---|
| Name | AI-Assisted | Reusable Agents | Delegational Orchestration | Governed Autonomy |
| Steps | 1 Explore · 2 Cursor-first | 3 Codify · 4 Standardize & verify | 5 Delegate & parallelize · 6 Agents act as you | 7 Governed pipelines · 8 Multiply |
| In practice | Cursor desktop (editor and Agents Window) is your daily default; Agent handles anything beyond a small edit. | Rules, `AGENTS.md` and skills carry your standards; Plan Mode for big changes; hooks, plugins and MCP extend the agent. | Scoped work goes to Cloud Agents and parallel agents; MCP lets agents act as you; you review. | Event-driven Automations behind approval gates, hooks and an audit trail; others adopt what you build. |

- **Four pillars**, each scored 0-4: Adoption, Reuse, Orchestration and Outcomes. Outcomes depends on persona: AI and cloud commits on the primary branch for a Developer IC, the group's level mix for Eng Leadership, and accepted agent diffs and Automations for a PM / Specialist.
- **Gates are cumulative.** Your level is the highest level where every pillar gate at that level and below is met. The displayed level moves up after 2 straight weeks at a new level and down after 4 straight weeks below.
- **Composite** = persona-weighted sum of the pillar scores (0-4). It's informational and never sets the level.
- **Coach checks (\*)**, such as repo rules / `AGENTS.md`, human review of agent PRs and the governance checklist, are shown next to the level and never set it.
- Trailing 28 days, recomputed every Monday. All thresholds and weights are in `framework.md` section 2, the single source of truth.

## Repository layout

```text
.cursor-plugin/
  plugin.json            # Cursor plugin manifest (name: ai-proficiency-coach)
  marketplace.json       # single-plugin marketplace manifest, source "./"
assets/logo.svg
skills/ai-proficiency-coach/
  SKILL.md               # the coaching procedure
  references/
    framework.md         # levels, Steps 1-8, gates (section 2 is authoritative)
    data-contract.md     # weekly input row and Cursor API source per field
    cursor-playbook.md   # Step -> Cursor features -> 10-minute exercise
  scripts/score.py       # scorer (Python 3 standard library only)
  examples/
    fake-ic-row.json     # the data-contract worked example (FAKE data)
    fake-team.csv        # four FAKE people, for --team
tests/test_score.py      # unit tests, including the worked example
```

## Install

### As a local plugin

```bash
git clone <this-repo-url> ~/.cursor/plugins/local/ai-proficiency-coach
```

Then restart Cursor, or run **Developer: Reload Window**. Open **Customize** and check that the `ai-proficiency-coach` skill appears under Skills. Invoke it by typing `/ai-proficiency-coach` in Agent chat. Because the skill is manual-only, asking "what PL am I?" without the slash command won't load it.

Notes:

- Clone or copy the repo into the folder. Cursor skips symlinks in `~/.cursor/plugins/local` that point outside that folder.
- On Teams and Enterprise, local plugins load only if an admin has turned on **Allow Local Plugin Imports**. It's under Dashboard → Settings → Security & Identity → Marketplace and Plugins, and it's off by default on Enterprise.

### Through a team marketplace (Teams and Enterprise)

1. A team admin opens **Dashboard → Plugins & MCPs → Team Marketplaces → Add Marketplace**.
2. Choose **Import from Repo** and paste this repository's URL (or your fork's). The repo includes `.cursor-plugin/marketplace.json`, so the plugin is discovered automatically.
3. Under **Marketplace Settings**, set Marketplace Access and optionally turn on Auto Refresh. Choose an installation mode: Default Off, Default On or Required.
4. Developers then install it from **Customize**.

To add it to an existing team marketplace repo instead, add an entry to that repo's `marketplace.json` that points at a copy of this plugin folder.

## Feeding it data

The coach works best on a real weekly row. It never fabricates data. If no row is available, it runs a short self-assessment and labels the result **self-reported**.

### Where the numbers come from (Enterprise)

Every field in the row maps to a Cursor Admin, Analytics or AI Code Tracking API endpoint. The field-by-field derivation is in `references/data-contract.md`. In summary:

| Pillar | Endpoint → fields |
|---|---|
| Identity | `GET /teams/members` → `email`, `id`, `name`, `isRemoved` |
| Adoption | `POST /teams/daily-usage-data` (paginate with `page`/`pageSize` to get `isActive`) → `isActive`, `agentRequests`, `chatRequests`, `totalTabsAccepted`, `cmdkUsages` |
| Reuse | `GET /analytics/by-user/skills` → `skill_name`, `event_date`, `usage` · `GET /analytics/by-user/plans` → `usage` · `GET /teams/audit-logs?eventTypes=team_rule,team_hook` → `user_email` |
| Orchestration | `POST /teams/filtered-usage-events` → `cloudAgentId`, `automationId`, `serviceAccountId`, `userEmail`, `timestamp` · `GET /analytics/by-user/mcp` → `mcp_server_name`, `event_date`, `usage` |
| Outcomes · IC | `GET /analytics/ai-code/commits` → `isPrimaryBranch`, `commitSource`, `tabLinesAdded`, `composerLinesAdded`, `commitTs` (drop `message`) |
| Outcomes · PM | `GET /analytics/by-user/agent-edits` → `total_accepted_diffs`, `event_date` |
| Outcomes · Leader | `GET /teams/directory-groups/:groupId/members` → `email`, joined to computed levels |

A typical weekly pipeline, run by an admin each Monday:

1. Pull the trailing 28 days from each endpoint. Analytics endpoints default to 7 days, so pass `startDate=28d`. Admin endpoints take epoch-ms `startDate`/`endDate`. Respect the rate limits: 20/min for daily usage and audit logs, 60/min for usage events.
2. Bucket the window into W1-W4 and build one row per person, following `data-contract.md` §2. Add persona from HR/SCIM, plus the manual lists: the author log, the Automation owner list and coach checks.
3. Score everyone, then fill each leader's `group_*` fields from their members' levels, and score the leaders.
4. Store weekly snapshots in `history`, so the up-after-2 / down-after-4 rule can apply.
5. Give each person their own row, and each leader the team summary, to use with the skill.

Keep API keys in your environment or secret manager. Never commit them, and never paste them into chat.

### Running the scorer directly

```bash
cd skills/ai-proficiency-coach
python3 scripts/score.py examples/fake-ic-row.json          # one person
python3 scripts/score.py examples/fake-team.csv --team      # team mix
python3 scripts/score.py examples/fake-ic-row.json --json   # machine-readable
```

On the fake worked example, the output is `PL2`, pillars Adoption 3 / Reuse 2 / Orchestration 3 / Outcomes 2, and composite `2.50`. The two smallest gaps to PL3 are one more skill used in ≥3 of 4 weeks and one more primary-branch cloud commit.

## Privacy

- **Usage metadata only.** The coach never asks for, opens or quotes chats, prompts, code, diffs or commit messages. Drop the commit `message` field at ingestion, and don't call conversation-level or file-level blame endpoints.
- **For coaching, not appraisal.** The level isn't used in appraisals until it has been calibrated.
- **Leaders see aggregates by default.** The team view reports the PL mix and never-engaged count.
- All example data in this repo is fake (`example.com` addresses, `FAKE` ids).

## Limitations

- The Admin, Analytics and AI Code Tracking APIs are Enterprise-only. AI Code Tracking is in Alpha and covers only the top-level repo of a workspace. Without an export, the result is self-reported.
- Date-ranged endpoints cap at 30 days, which is enough for the 28-day window.
- Some items can't be verified by API, so they are coach checks or maintained lists: repo rules / `AGENTS.md`, skill authorship and adoption by others, Bugbot findings per person, the governance checklist, Automation owners under service accounts, team rule or hook authors saved by an admin, parallel agents, output quality, and persona. See `framework.md` "Not verifiable by API".
- Audit-log `team_rule` / `team_hook` events are all counted as authored for now. Whether `event_data` separates create, update and delete is an open item in the data contract.
- "Not required" pillar gates count as met, so a new user's Reuse and Orchestration scores start above zero. This raises the composite, but never the level.

## Development

```bash
python3 -m unittest discover -s tests -v
```

If you change a threshold or weight in `framework.md` section 2, make the same change in `scripts/score.py` and the tests.

## License

[MIT](LICENSE)
