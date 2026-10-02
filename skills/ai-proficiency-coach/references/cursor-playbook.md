# Cursor playbook: Steps 1-8

Use this to turn what's holding someone back into a concrete Cursor action. Each Step lists a recognition cue, the Cursor features it relies on, a 10-minute exercise, what to avoid, and what the org has to unblock. What each level means lives in `framework.md`; actions live only here.

Only Cursor features are listed. Grok Bot appears as an optional extra at Steps 6 and 8 for knowledge work outside coding; it is never required.

## What's holding them back → first action

| If the thing holding them back is… | First Cursor action | Step |
|---|---|---|
| Cursor isn't part of most days yet | Open Cursor first thing each workday. Start the day's first task in Agent, not by hand. | 1-2 |
| They ask about code more than they change it | When you catch yourself asking "how would I…", switch the question to an Agent task that makes the change, then review the diff. | 2 |
| Big changes start without a plan | Press Shift+Tab in the chat input to rotate to Plan Mode for any change over an hour. Edit the plan, then build. | 2-3 |
| The same context gets re-explained every chat | Turn a workflow you repeat weekly into a skill with `/create-skill`, then invoke it with `/skill-name` every time that task comes up. | 3-4 |
| AI output rarely reaches the primary branch | Let Agent or Tab write the change. Run tests, then merge rather than re-typing it by hand. | 1-2 |
| Everything waits on them to run it | Hand one well-scoped ticket to a Cloud Agent. Review its PR and merge it. | 5 |
| Agents can't see the tickets or docs they need | Connect one approved MCP server and use it on a real ticket, a few days a week. | 4, 6 |
| Nothing runs unless they start it | Create one owned, recurring Automation with `/automate`. Keep it running week over week. | 6-7 |
| Their setup only works for them | Promote a proven project rule or hook to a team rule or team hook, and publish a skill with an owner. | 8 |
| (PM) They read with AI but don't change anything | Use Agent to make small, real edits (spec docs, copy, config, test plans) and accept the diffs you agree with. | 1-3 |
| They lead a group | See "Leaders" at the end. | — |

## PL1 · AI-Assisted

### Step 1 · Explore

You'll recognize this stage when… you mostly use Tab and the occasional chat question, and you still write most of your code by hand.

**Cursor features**: Tab completions; inline edit (Cmd/Ctrl+K) on a selected block; Ask with @-context for the right files; Agent in the Agents Window on a first real task; the diff view to review changes before keeping them.

**10-minute exercise**

1. Open a module you don't know well. In Ask, @-mention the file and ask it to explain the main flow.
2. Select one function and use inline edit (Cmd/Ctrl+K) to add input validation. Review the diff.
3. In the Agents Window, give Agent one real task, such as "write unit tests for `<function>` and run them". Read the diff before you keep it.

**You'll notice**: you open Cursor without thinking about it, and Agent has written code you kept.

**Avoid**: waiting until you're stuck to try AI; one-line prompts with no context; stopping at Tab instead of giving Agent a real task.

**Org unblock**: protected learning time; a published list of which code and data are allowed in Cursor; clients kept current so everyone has the Agents Window.

### Step 2 · Cursor-first

You'll recognize this stage when… you reach for Agent most days, but you keep re-explaining the same context at the start of every chat.

**Cursor features**: Agent as the default for anything beyond a small edit, in the editor or the Agents Window; Plan Mode (Shift+Tab, or the mode picker); @-context for files, docs and terminal output; model choice per task; diff review before keeping changes.

**10-minute exercise**

1. Take tomorrow's largest task. Rotate to Plan Mode and describe the goal and constraints.
2. Answer its clarifying questions. Edit the plan until it matches what you'd do, then build it.
3. Write down every piece of context you had to re-explain. That list becomes your first rule or skill in Step 3.

**You'll notice**: big changes start with a plan instead of a guess, and AI-written code is reaching your primary branch.

**Avoid**: doing by hand what Agent should do; accepting diffs without running tests; re-typing the same context every chat.

**Org unblock**: write down team conventions so they can become rules; fund test coverage so AI output can be verified; set a default model-routing policy.

## PL2 · Reusable Agents

### Step 3 · Codify

You'll recognize this stage when… you keep pasting the same instructions into chat and wish the agent just knew your conventions.

**Cursor features**: project rules in `.cursor/rules/*.mdc` (create one with `/create-rule`); `AGENTS.md` for build, test and lint steps; skills in `.cursor/skills/<name>/SKILL.md` (create one with `/create-skill`), picked up by Agent automatically or invoked with `/skill-name`; Customize to view and manage rules and skills; Plan Mode before multi-file changes.

**10-minute exercise**

1. Run `/create-rule` and give it your last three corrections to Agent. Keep the rule short and specific.
2. Run `/create-skill` and turn your PR review checklist, or another weekly workflow, into a skill.
3. Add `AGENTS.md` at the repo root listing how to build, test and lint.
4. Put the skill on your calendar: invoke `/skill-name` every time that task comes up this week.

**You'll notice**: you stop re-explaining your conventions, and the repo tells the agent how to build and test itself.

**Avoid**: long, vague rules; skills nobody invokes; skipping Plan Mode on big changes.

**Org unblock**: agree on the conventions worth encoding; publish team rules and skills in a shared repo or team marketplace; tell developers what rules may contain.

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

**You'll notice**: a teammate gets the same result you do, and checks run without you remembering them.

**Avoid**: trusting output because it looks right; installing plugins or MCP servers you haven't vetted; keeping a setup only you can use. When a rule fails, fix the rule, not the output.

**Org unblock**: turn on Bugbot; approve a plugin and MCP list; name owners for shared rules and skills; fund test coverage.

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

**You'll notice**: you're reviewing PRs you didn't write, and you started the next task while the first was still running.

**Avoid**: parallelizing tightly coupled work; delegating without a clear spec; letting agent PRs pile up unreviewed.

**Org unblock**: enable Cloud Agents; turn on Bugbot and branch protection; staff review so it doesn't become the bottleneck.

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

**You'll notice**: you stop copying ticket details into chat, and something useful is already done when you sit down.

**Avoid**: granting broad tokens "to make it work"; Automations nobody owns; skipping the check on what an agent did in your name.

**Org unblock**: approve an MCP list; provision service accounts; give security review a clear path to yes for tool access.

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

**You'll notice**: an agent runs unattended and you're comfortable with it, because the risky paths stop for your approval.

**Avoid**: automating without a rollback path; granting more permission than the task needs; ignoring alerts.

**Org unblock**: provision service accounts and approval gates; review audit logs; assign an owner to every Automation.

### Step 8 · Multiply

You'll recognize this stage when… teammates keep asking for your rules, skills and Automations, and you're answering the same setup questions twice.

**Cursor features**:

- Team rules and team hooks. Team hooks are configured in the web dashboard (Enterprise) and synced to members.
- Shared skills and plugins in the team marketplace. Admins set each plugin to Default Off, Default On or Required.
- Automation templates reused across repos.
- Optional: Grok Bot to extend the pattern to knowledge work beyond engineering.

**10-minute exercise**

1. Pick your most-used project rule or hook and propose it as a team rule or team hook.
2. Publish one skill to the team marketplace, with a README and an owner.
3. Put a quarterly review on your calendar to retire unused Automations.

**You'll notice**: other teams are running what you built, and you're not the one answering the setup questions.

**Avoid**: building only for yourself; shipping shared assets without an owner or docs; chasing autonomy for its own sake.

**Org unblock**: fund a platform team to own shared assets; agree on a definition of "safe to automate"; recognize people who build for others.

## Leaders

Match the org unblock to where most of the group sits:

- **Mostly PL0-PL1**: protected learning time; publish which code and data are allowed in Cursor; keep clients current. Follow up personally and supportively with never-engaged seats.
- **Mostly PL2**: agree on conventions to encode; publish team rules and skills in the team marketplace; turn on Bugbot; approve a plugin and MCP list; fund test coverage.
- **Mostly PL3**: enable Cloud Agents; set branch protection and required review; provision service accounts; staff review so it doesn't become the bottleneck.
- **Toward PL4**: approval gates and audit-log review; an owner for every Automation; a platform owner for shared assets.

For the leader's own work, Cursor is useful for reviews, design docs and scripts. Ask in Cursor can answer "how does this work?" about the codebase before a design review.
