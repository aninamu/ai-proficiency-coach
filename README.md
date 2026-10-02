# AI Proficiency Coach

A Cursor plugin with one coaching skill. It places an engineer, eng leader, or PM on a four-level AI proficiency framework (PL1-PL4) from their Cursor usage metadata, names the smallest unmet gate, and gives one or two concrete Cursor next steps for the week plus one thing to avoid. For a team export it reports the PL0-PL4 mix, the share at PL3+ (the org target), and the never-engaged count, along with the leader's own level and one or two org unblocks. With no usage row, it runs the same gates on a self-reported estimate.

The skill is **manual-only** (`disable-model-invocation: true`). Agent never applies it on its own; it runs only when you invoke it. In Agent chat, type `/ai-proficiency-coach` followed by your question:

```text
/ai-proficiency-coach How am I doing with AI? Here's my weekly row: <paste or @-mention the file>
/ai-proficiency-coach How do I get to PL3?
/ai-proficiency-coach Here's my team's export. What's our PL mix, and who's never engaged?
/ai-proficiency-coach I have no data. Can we do a quick self-assessment?
```

The skill is grounded in one framework (`skills/ai-proficiency-coach/references/framework.md`) and one input contract (`skills/ai-proficiency-coach/references/data-contract.md`). It scores by running `scripts/score.py` (Python 3 standard library only) from the skill directory. If Python is unavailable, it applies `framework.md` section 2 by hand and shows its working. It reads a row you provide. It calls Cursor APIs only if you ask and credentials are already in your environment, and it never asks for a key in chat. A missing field fails its gate; the skill does not fill in numbers.

## Framework at a glance

| | PL1 | PL2 | PL3 (org target) | PL4 |
|---|---|---|---|---|
| Name | AI-Assisted | Reusable Agents | Delegational Orchestration | Governed Autonomy |
| Steps | 1 Explore · 2 Cursor-first | 3 Codify · 4 Standardize & verify | 5 Delegate & parallelize · 6 Agents act as you | 7 Governed pipelines · 8 Multiply |
| In practice | Cursor desktop (editor and Agents Window) is your daily default; Agent handles anything beyond a small edit. | Rules, `AGENTS.md` and skills carry your standards; Plan Mode for big changes; hooks, plugins and MCP extend the agent. | Scoped work goes to Cloud Agents and parallel agents; MCP lets agents act as you; you review. | Event-driven Automations behind approval gates, hooks and an audit trail; others adopt what you build. |

- **Four pillars**, each scored 0-4: Adoption, Reuse, Orchestration, and Outcomes. Outcomes depends on persona: AI and cloud commits on the primary branch for a Developer IC; the group's displayed level mix, plus the never-engaged share at PL3 and PL4, for Eng Leadership; accepted agent diffs for a PM / Specialist, plus Automations at PL4.
- **Gates are cumulative.** The gated level is the highest level where every pillar gate at that level and below is met. Missing a PL1 gate means PL0. The displayed level moves up after 2 straight weeks at a new level and down after 4 straight weeks below.
- **Composite** = persona-weighted sum of the pillar scores (0-4). It's informational and never sets the level.
- **Coach checks (\*)** are shown next to the level and never set it. They are repo rules / `AGENTS.md` (PL2), human review of every agent PR (PL3), and at PL4 the governance checklist, no unresolved high-severity Bugbot findings, and skills adopted by others. Unknown values are shown as "unknown".
- An individual reply also includes the current Step's "You'll recognize this stage when…" line, and each next step names the field it moves. Next steps are Cursor actions. Grok Bot may be mentioned as optional for knowledge work outside coding at PL3 and PL4; it never counts toward a level.
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
    data-contract.md     # weekly input row, with API, local and manual sources
    cursor-playbook.md   # Step -> Cursor features -> 10-minute exercise
  scripts/
    score.py             # scorer (Python 3 standard library only)
    local_probe.py       # partial row from the local install, metadata columns only
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

The coach works best on a real weekly row. Without one it can probe the local install for what it can measure. Failing that, it asks for trailing-28-day estimates (active days, Agent vs chat, skills and how many of the 4 weeks, Plan mode, team rules or hooks authored, Cloud Agent runs, MCP days, Automations and how many weeks each ran, and the persona's outcome fields), builds a row, scores it with `--self-reported`, and labels every result **self-reported**.

### Ad hoc, from your own machine

No Enterprise API and no admin needed. `scripts/local_probe.py` reads the stores your signed-in Cursor install already keeps on disk and prints a partial row:

```bash
cd skills/ai-proficiency-coach
python3 scripts/local_probe.py --persona IC --text          # what it found, and what it can't see
python3 scripts/local_probe.py --persona IC | python3 scripts/score.py - --local-probe
```

It measures `active_days`, `cloud_agent_runs`, a Plan-mode count, the agent-versus-ask mix, and the IC commit fields, from `~/.cursor/ai-tracking/ai-code-tracking.db`, `conversation-search.db`, `state.vscdb`, and `~/.cursor/plans`. Every query selects metadata columns only, and the script asserts its own SQL against a deny list, so it can never pull a conversation title, body, summary, or commit message.

Two caveats worth stating up front. It sees **one install**, so `active_days` is a floor rather than a count. And it cannot derive `skills_in_3of4_weeks`, `primary_cloud_commits`, or `mcp_days` — which are the PL3 gates — so a probe row comes back with `level_is_floor` set and should feed the self-assessment questions rather than stand in for an export. The field-by-field detail, and the full list of what is unavailable, is in `references/data-contract.md` section 5.

### Where the numbers come from (Enterprise)

API-backed fields come from a Cursor Admin, Analytics, or AI Code Tracking endpoint. Persona, coach checks, the author log, the Automation owner list, and weekly history are supplied outside those APIs. The field-by-field list is in `skills/ai-proficiency-coach/references/data-contract.md`. In summary:

| Pillar | Endpoint → fields |
|---|---|
| Identity | `GET /teams/members` → `email`, `id`, `name`, `isRemoved` |
| Adoption | `POST /teams/daily-usage-data` (paginate with `page`/`pageSize` to get `isActive`) → `isActive`, `agentRequests`, `chatRequests`, `totalTabsAccepted`, `cmdkUsages` |
| Reuse | `GET /analytics/by-user/skills` → `skill_name`, `event_date`, `usage` · `GET /analytics/by-user/plans` → `usage` · `GET /teams/audit-logs?eventTypes=team_rule,team_hook` → `user_email` |
| Orchestration | `POST /teams/filtered-usage-events` → `cloudAgentId`, `automationId`, `serviceAccountId`, `userEmail`, `timestamp` · `GET /analytics/by-user/mcp` → `mcp_server_name`, `event_date`, `usage` |
| Outcomes · IC | `GET /analytics/ai-code/commits` → `isPrimaryBranch`, `commitSource`, `tabLinesAdded`, `composerLinesAdded`, `commitTs` (drop `message`) |
| Outcomes · PM | `GET /analytics/by-user/agent-edits` → `total_accepted_diffs`, `event_date`. PL4 also counts Automations from filtered usage events. |
| Outcomes · Leader | `GET /teams/directory-groups/:groupId/members` → `email`, joined to members' displayed levels |

A typical weekly pipeline, run by an admin each Monday:

1. Pull the trailing 28 days from each endpoint. Analytics endpoints default to 7 days, so pass `startDate=28d`. Admin endpoints take epoch-ms `startDate`/`endDate`. Respect the rate limits: 20/min for daily usage and audit logs, 60/min for usage events.
2. Bucket the window into W1-W4 and build one row per person, following `data-contract.md` §2. Add persona from HR/SCIM, plus the manual lists: the author log, the Automation owner list and coach checks.
3. Score everyone, then fill each leader's `group_*` fields from their members' displayed levels, and score the leaders.
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

On the fake worked example, the output is displayed `PL2` (gated `PL2`, steady), pillars Adoption 3 / Reuse 2 / Orchestration 3 / Outcomes 2, and composite `2.50`. The unmet PL3 gates, smallest first, are one more skill used in ≥3 of 4 weeks and one more primary-branch cloud commit. On `examples/fake-team.csv --team`, the mix is PL0 1, PL1 1, PL2 2, PL3 0, PL4 0, with 1 never-engaged (25%) and 0% at PL3+. Never-engaged means zero active days in the trailing 28 days.

## Privacy

- **Usage metadata only.** The coach never asks for, opens or quotes chats, prompts, code, diffs or commit messages. Drop the commit `message` field at ingestion, and don't call conversation-level or file-level blame endpoints.
- **For coaching, not appraisal.** The level isn't used in appraisals until it has been calibrated.
- **Leaders see aggregates by default.** The team view reports the PL mix, the share at PL3+, and the never-engaged count. An individual's row comes up only when the leader already has it and asks.
- All example data in this repo is fake (`example.com` addresses, `FAKE` ids).

## Limitations

- The Admin, Analytics and AI Code Tracking APIs are Enterprise-only. AI Code Tracking is in Alpha and covers only the top-level repo of a workspace. Without an export, the result comes from the local probe or is self-reported.
- The local probe covers one install, so `active_days` is a floor, and it cannot see `skills_in_3of4_weeks`, `primary_cloud_commits`, `mcp_days`, Automations or `accepted_diff_days`. Any row with missing inputs is reported as a floor (`level_is_floor`), never as a settled level.
- Date-ranged endpoints cap at 30 days, which is enough for the 28-day window.
- Coach checks never set the level. They are repo rules / `AGENTS.md` (PL2), human review of every agent PR (PL3), and at PL4 the governance checklist, no unresolved high-severity Bugbot findings, and skills adopted by others. Checks up through the next level are shown; at PL4, all of them. Bugbot data is per repo and PR, so the per-person check needs a GitHub author join. Two maintained lists only attribute work: Automation owners under service accounts, and the real author when an admin saves a team rule or hook. Persona comes from HR/SCIM. Parallel agents, output quality, and hooks, plugins, and MCP at PL2 are not gates. See `framework.md` "Not verifiable by API".
- Audit-log `team_rule` / `team_hook` events are all counted as authored for now. Whether `event_data` separates create, update and delete is an open item in the data contract.
- Reuse has no PL1 gate and Orchestration has no PL1 or PL2 gate, so those scores start at 1 and 2 when the later gates are unmet. That lifts the composite, and it can lift the gated level when Reuse or Orchestration would otherwise be the lowest pillar. Someone with no activity stays at PL0, because Adoption and Outcomes still have PL1 gates.

## Development

```bash
python3 -m unittest discover -s tests -v
```

If you change a threshold or weight in `framework.md` section 2, make the same change in `scripts/score.py` and the tests.

## License

[MIT](LICENSE)
