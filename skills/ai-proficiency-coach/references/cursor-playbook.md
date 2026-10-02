# Cursor playbook: Steps 1-8

Use this to turn a smallest unmet gate into a concrete Cursor action. Each Step lists the Cursor features it relies on, a 10-minute exercise, and the data-contract fields the exercise moves. Thresholds live only in `framework.md` section 2.

Only Cursor features are listed. Grok Bot appears as an optional extra at Steps 6 and 8 for knowledge work outside coding; it never counts toward a gate.

## Gap → first action

| Smallest unmet gate (field) | First Cursor action | Step |
|---|---|---|
| `active_days` | Open Cursor first thing each workday. Start the day's first task in Agent, not by hand. | 1-2 |
| `agent_requests` vs `chat_requests` | When you catch yourself asking "how would I…", switch the question to an Agent task that makes the change, then review the diff. | 2 |
| `plan_mode_uses` | Press Shift+Tab in the chat input to rotate to Plan Mode for any change over an hour. Edit the plan, then build. | 2-3 |
| `skills_in_2of4_weeks` / `skills_in_3of4_weeks` | Turn a workflow you repeat weekly into a skill with `/create-skill`, then invoke it with `/skill-name` every time that task comes up. | 3-4 |
| `primary_ai_commit_share` / `commits_with_ai_lines` | Let Agent or Tab write the change. Run tests, then merge to the primary branch rather than re-typing the change by hand. | 1-2 |
| `cloud_agent_runs` / `primary_cloud_commits` | Hand one well-scoped ticket to a Cloud Agent. Review its PR and merge it. | 5 |
| `mcp_days` | Connect one approved MCP server and use it on a real ticket, a few days a week. | 4, 6 |
| `automations_active_3of4_weeks` | Create one owned, recurring Automation with `/automate`. Keep it running week over week. | 6-7 |
| `team_rules_hooks_authored` | Promote a proven project rule or hook to a team rule or team hook. If an admin saves it, they log you in the author log. | 8 |
| `accepted_diff_days` (PM) | Use Agent to make small, real edits (spec docs, copy, config, test plans) and accept the diffs you agree with. | 1-3 |
| Leader group shares / never-engaged | See "Leaders" at the end. | — |

## PL1 · AI-Assisted

### Step 1 · Explore

You'll recognize this stage when… you mostly use Tab and the occasional chat question, and you still write most of your code by hand.

**Cursor features**: Tab completions; inline edit (Cmd/Ctrl+K) on a selected block; Ask with @-context for the right files; Agent in the Agents Window on a first real task; the diff view to review changes before keeping them.

**10-minute exercise**

1. Open a module you don't know well. In Ask, @-mention the file and ask it to explain the main flow.
2. Select one function and use inline edit (Cmd/Ctrl+K) to add input validation. Review the diff.
3. In the Agents Window, give Agent one real task, such as "write unit tests for `<function>` and run them". Read the diff before you keep it.

**Moves**: `active_days`, `agent_requests`, `commits_with_ai_lines`, `accepted_diff_days`.

### Step 2 · Cursor-first

You'll recognize this stage when… you reach for Agent most days, but you keep re-explaining the same context at the start of every chat.

**Cursor features**: Agent as the default for anything beyond a small edit, in the editor or the Agents Window; Plan Mode (Shift+Tab, or the mode picker); @-context for files, docs and terminal output; model choice per task; diff review before keeping changes.

**10-minute exercise**

1. Take tomorrow's largest task. Rotate to Plan Mode and describe the goal and constraints.
2. Answer its clarifying questions. Edit the plan until it matches what you'd do, then build it.
3. Write down every piece of context you had to re-explain. That list becomes your first rule or skill in Step 3.

**Moves**: `plan_mode_uses`, `agent_requests` vs `chat_requests`, `primary_ai_commit_share`.

## PL2 · Reusable Agents

### Step 3 · Codify

You'll recognize this stage when… you keep pasting the same instructions into chat and wish the agent just knew your conventions.

**Cursor features**: project rules in `.cursor/rules/*.mdc` (create one with `/create-rule`); `AGENTS.md` for build, test and lint steps; skills in `.cursor/skills/<name>/SKILL.md` (create one with `/create-skill`), picked up by Agent automatically or invoked with `/skill-name`; Customize to view and manage rules and skills; Plan Mode before multi-file changes.

**10-minute exercise**

1. Run `/create-rule` and give it your last three corrections to Agent. Keep the rule short and specific.
2. Run `/create-skill` and turn your PR review checklist, or another weekly workflow, into a skill.
3. Add `AGENTS.md` at the repo root listing how to build, test and lint.
4. Put the skill on your calendar: invoke `/skill-name` every time that task comes up this week.

**Moves**: `skills_in_2of4_weeks`, `plan_mode_uses`; coach check `repo_rules_in_place`*.

### Step 4 · Standardize & verify

You'll recognize this stage when… your rules and skills work well for you, but teammates get different results and you still check every output by eye.

**Cursor features**:

- Team rules, and skills shared through the team marketplace. To publish a personal skill, open Customize → Skills → Publish.
- Hooks in `.cursor/hooks.json`, created with `/create-hook`. Use `afterFileEdit` to run your formatter after agent edits, and `beforeShellExecution` to gate risky commands.
- Plugins from the Cursor Marketplace, installed from Customize.
- An approved MCP server for docs or tickets while you drive.
- Bugbot on every PR. Run `/review-bugbot` locally before you push.

**10-minute exercise**

1. Run `/create-hook` with "after every agent file edit, run our formatter and linter on the edited file".
2. Add one line to your main skill: "run the tests and report results before saying done".
3. Publish your most-used skill to the team marketplace from Customize → Skills.

**Moves**: `skills_in_3of4_weeks`, `mcp_days`.

## PL3 · Delegational Orchestration (org target)

### Step 5 · Delegate & parallelize

You'll recognize this stage when… you're waiting on one agent to finish when you could be starting the next task with another.

**Cursor features**:

- Cloud Agents. Start one by selecting Cloud in the dropdown under the agent input in Cursor Desktop, from cursor.com/agents, by commenting `@cursor` on a GitHub issue or PR, or with `@cursor` in Slack. Each Cloud Agent works on its own branch and opens a PR.
- Parallel agents in worktrees from the Agents Window. In the IDE, use `/worktree` for one isolated run or `/best-of-n` to compare approaches.
- Subagents for focused sub-tasks; create custom ones with `/create-subagent`.
- Plan Mode to write the spec first.

**10-minute exercise**

1. Pick a ticket that is small, well specified and not tightly coupled to other work.
2. In Plan Mode, write the acceptance criteria and the test that proves it's done.
3. Start a Cloud Agent with that plan. Come back to the PR, review it like a teammate's, and merge it to the primary branch.

**Moves**: `cloud_agent_runs`, `primary_cloud_commits`, `primary_cloud_commit_weeks`; coach check `agent_prs_human_reviewed`*.

### Step 6 · Agents act as you

You'll recognize this stage when… you copy ticket details and doc links into chat by hand, and the same morning chores still wait for you to kick them off.

**Cursor features**:

- MCP servers for the tools you already use (tickets, docs, source control). For Cloud Agents, manage them from the MCP dropdown at cursor.com/agents.
- Automations: create one with `/automate`, in the Agents Window, or at cursor.com/automations. Triggers include schedules, GitHub events, Slack, Linear and webhooks. "Run as" can be Me or a service account; only admins can choose the service account.
- The Cursor CLI in headless mode (`agent -p "…"`) for scripted runs.
- Optional: Grok Bot for knowledge-work and cross-workflow tasks outside coding.

**10-minute exercise**

1. Connect one approved MCP server and use it on today's ticket, for example to read the ticket and linked doc before planning.
2. Run `/automate` with "every weekday at 9am, triage new issues labeled bug in `<repo>` and open a draft fix PR for my review". Name yourself as owner.
3. Check what tools and repos the Automation can touch before you activate it.

**Moves**: `mcp_days`, `automations_active_3of4_weeks`.

## PL4 · Governed Autonomy

### Step 7 · Governed pipelines

You'll recognize this stage when… your agents do good work, but only when you start them, and you'd hesitate to let one run unattended without guardrails.

**Cursor features**:

- Automations on events and schedules, such as the GitHub "CI completed" trigger for failed checks, or a weekly dependency-update run.
- The CLI in headless mode inside GitHub Actions.
- Hooks that block or ask for approval. `beforeShellExecution` and `beforeMCPExecution` return `permission: "allow" | "deny" | "ask"`. Exit code 2 blocks. Hooks fail open by default; set `failClosed: true` on security-critical hooks.
- Service accounts for Automations, and least-privilege MCP.

**10-minute exercise**: add an approval gate for schema changes.

`.cursor/hooks.json`:

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": ".cursor/hooks/ask-before-schema-change.sh",
        "matcher": "DROP|ALTER|drop table|alter table"
      }
    ]
  }
}
```

`.cursor/hooks/ask-before-schema-change.sh` (make it executable):

```bash
#!/bin/bash
cat > /dev/null
echo '{"permission":"ask","user_message":"Schema change detected: approve before it runs.","agent_message":"This command changes a schema and needs human approval."}'
```

Then write the rollback plan and kill switch for your Automation before you widen its triggers.

**Moves**: `automations_active_3of4_weeks`, `primary_cloud_commit_weeks`; coach checks `governance_checklist_signed_off`* and `no_unresolved_high_sev_bugbot`*.

### Step 8 · Multiply

You'll recognize this stage when… teammates keep asking for your rules, skills and Automations, and you're answering the same setup questions twice.

**Cursor features**:

- Team rules and team hooks. Team hooks are configured in the web dashboard (Enterprise) and synced to members.
- Shared skills and plugins in the team marketplace. Admins set each plugin to Default Off, Default On or Required.
- Automation templates reused across repos.
- Optional: Grok Bot to extend the pattern to knowledge work beyond engineering.

**10-minute exercise**

1. Pick your most-used project rule or hook and propose it as a team rule or team hook. If an admin saves it, ask them to record you in the author log.
2. Publish one skill to the team marketplace, with a README and an owner.
3. Put a quarterly review on your calendar to retire unused Automations.

**Moves**: `team_rules_hooks_authored`; coach check `skills_adopted_by_others`*.

## Leaders

Match the org unblock to where most of the group sits (framework.md "What the org needs to unblock"):

- **Mostly PL0-PL1**: protected learning time; publish which code and data are allowed in Cursor; keep clients current. Follow up personally and supportively with never-engaged seats.
- **Mostly PL2**: agree on conventions to encode; publish team rules and skills in the team marketplace; turn on Bugbot; approve a plugin and MCP list; fund test coverage.
- **Mostly PL3**: enable Cloud Agents; set branch protection and required review; provision service accounts; staff review so it doesn't become the bottleneck.
- **Toward PL4**: approval gates and audit-log review; an owner for every Automation; a platform owner for shared assets.

For the leader's own work, Cursor is useful for reviews, design docs and scripts. Ask in Cursor can answer "how does this work?" about the codebase before a design review.
