# AI Proficiency framework reference

> Reference framework for the **AI Proficiency Coach** Cursor plugin: proficiency levels, steps, gates and API mapping. **Metrics & APIs (section 2) is authoritative** for every level decision; the other sections describe what each level means.
>
> `scripts/score.py` implements section 2 exactly. If you change a threshold here, change it there too and re-run `python3 -m unittest discover -s tests` from the repo root.
>
> Per-step actions, exercises, what to avoid and org unblocks live in `cursor-playbook.md`. Keep them out of this file so there is one place to change them. Steps 1–8 are coaching signals; only the section 2 gates set the level.

## 1. Overview

**AI Proficiency**: One PL1–PL4 scale for AI proficiency in Cursor.

### Why it matters

- Less toil, more time on design and hard problems, and portable skills in building and directing agents.
- One software factory across every team, with human-in-the-loop (HITL) checkpoints and built-in guardrails.

### Four proficiency levels

| | PL1 | PL2 | PL3 | PL4 |
|---|---|---|---|---|
| Level | PL1 | PL2 | PL3 (org target) | PL4 |
| Name | AI-Assisted | Reusable Agents | Delegational Orchestration | Governed Autonomy |
| Maturity stage | Stage 1: Assisted individuals | Stage 2: Codified team workflows | Stage 3: AI SDLC (Software Factory) | Stage 3 → 4: AI SDLC → Cross-functional AI Transformation |
| One-liner | Cursor desktop app (IDE and Agents window) is your daily default for everyday tasks. | Rules and skills allow agents to persist context and behave according to your standards; hooks, plugins and MCP extend them to adapt to your tools and workflows. | You delegate scoped work to Cloud Agents and parallel agents, and agents act as you. You review. | Event-driven agents run behind approval gates, hooks and an audit trail. Others adopt what you build. |
| Steps | Step 1 · Explore<br>Step 2 · Cursor-first | Step 3 · Codify<br>Step 4 · Standardize & verify | Step 5 · Delegate & parallelize<br>Step 6 · Agents act as you | Step 7 · Governed pipelines<br>Step 8 · Multiply |

### The four pillars

| Pillar | Overview description |
|---|---|
| Adoption | Regular Cursor use; from PL2, Agent requests at least match chat requests. |
| Reuse | Skills reused across weeks and Plan mode; team rules or hooks authored at PL4. Hooks, plugins and MCP are encouraged at PL2, not gated. |
| Orchestration | Cloud Agent runs and MCP use from PL3; Automations running week over week at PL4. |
| Outcomes | Persona-specific: AI and cloud commits on the primary branch (IC), team level mix (Leader), accepted agent diffs and Automations (PM). |

### Personas

_Including, but not limited to:_

| Persona | Who | Overview card |
|---|---|---|
| Developer IC | Engineers who ship code | Outcomes: AI-written code (Agent and Tab) on the primary branch; cloud-originated commits from PL3. |
| Eng Leadership | Managers and tech leads | Outcomes: your own level, plus how your team is spread across PL1–PL4. |
| PM / Specialist | PMs, designers, analysts | Outcomes: agent changes you accept, plus Automations you own at PL4. |

### Governance & coaching

- **Guardrails**: Least-privilege access, human review on every agent PR, owned Automations behind approval gates and an audit trail.
- **Org unblocks**: Learning time, shared rules and skills, Cloud Agents, an approved MCP list, service accounts. Per-step detail in `cursor-playbook.md`.
- **Coach**: A Cursor skill reads your weekly progress and suggests next steps.
- **Privacy**: We only see how much people use Cursor, never their chats or code. The level is for coaching; it's not used in appraisals until it's been calibrated.

> **Principle**: PL4 is governed autonomy, not zero human intervention: humans own the risk gates and reward outcomes.

## 2. Metrics & APIs (single source of truth for gates)

Single source of truth for every gate and threshold, and the Cursor API endpoint and field behind each. Trailing 28 days, recomputed every Monday. * = coach check, never sets the PL.

### Threshold grid

Gates are cumulative: a person is at the highest level where every pillar gate at that level and below is met.

| Pillar | PL1 | PL2 | PL3 | PL4 | API source (endpoint → field) |
|---|---|---|---|---|---|
| Adoption | ≥4 active days | ≥12 active days; agentRequests ≥ chatRequests | ≥14 active days; agentRequests ≥ chatRequests | ≥16 active days; agentRequests ≥ chatRequests | POST /teams/daily-usage-data → isActive, agentRequests, chatRequests |
| Reuse | Not required | ≥2 skills, each used in ≥2 of 4 weeks; Plan mode ≥4 uses | ≥3 skills, each used in ≥3 of 4 weeks; Plan mode ≥4 uses | PL3 gate, plus ≥1 team rule or team hook authored (admin-saved: real author logged*) | GET /analytics/by-user/skills → skill_name, event_date · /by-user/plans → usage · GET /teams/audit-logs → event_type team_rule, team_hook; user_email |
| Orchestration | Not required | Not required | ≥4 Cloud Agent runs (distinct cloudAgentId); MCP used on ≥3 days | PL3 gate, plus ≥1 Automation active in ≥3 of 4 weeks | POST /teams/filtered-usage-events → cloudAgentId, automationId, serviceAccountId, timestamp · GET /analytics/by-user/mcp → mcp_server_name, event_date |
| Outcomes · Developer IC | ≥1 commit with AI lines | ≥30% of primary-branch commits include AI lines | ≥3 primary-branch commits with commitSource = cloud | Primary-branch cloud commits in ≥3 of 4 weeks | GET /analytics/ai-code/commits → userEmail, isPrimaryBranch, commitSource; AI lines = tabLinesAdded + composerLinesAdded |
| Outcomes · Eng Leadership | ≥50% of group at PL1+ | ≥50% of group at PL2+ | ≥30% of group at PL3+; ≤10% never-engaged | ≥50% of group at PL3+; ≤10% never-engaged | GET /teams/directory-groups/:groupId/members → email, joined to computed PLs |
| Outcomes · PM / Specialist | Accepted agent diffs on ≥1 day | Accepted agent diffs on ≥4 days | Accepted agent diffs on ≥8 days | Accepted agent diffs on ≥8 days; ≥2 Automations active in ≥3 of 4 weeks | GET /analytics/by-user/agent-edits → total_accepted_diffs, event_date · POST /teams/filtered-usage-events → automationId |

### Scoring rules

How gates become a weekly level, plus what is checked or monitored but not scored.

| Rule | Definition | Detail |
|---|---|---|
| Weekly level | Highest level where every pillar gate at that level and below is met (gates are cumulative). | “Not required” counts as met. Recomputed each Monday from the trailing 28 days; there is no smoothing, so a quiet week can move the level. |
| Coach checks * | PL2: repo rules / AGENTS.md in place. PL3: every agent PR human-reviewed. PL4: governance checklist signed off; no unresolved high-severity Bugbot findings; your skills adopted by others. | Shown next to the PL, never used to set it. |
| Governance | Approved MCP servers, hooks and repo blocklists; spend is monitored, not scored. | GET /teams/audit-logs → mcp_server_config, mcp_authentication, team_hook · GET /settings/repo-blocklists/repos · POST /teams/spend → overallSpendCents |
| Never-engaged | Seat holders with zero active days in the trailing 28 days. | GET /teams/members minus active users in POST /teams/daily-usage-data → isActive |

### * Not verifiable by API

Coach-verified or self-reported. Shown next to the PL, never used to set it.

| Item | Why / how it is checked |
|---|---|
| Repo rules / AGENTS.md | Not exposed by Cursor APIs; GitHub repo scan or coach check. |
| Hooks, plugins, MCP at PL2 | Encouraged, not gated at PL2; MCP use is gated from PL3. |
| Skill authorship | Usage is exposed per user; authorship and adoption by others are not. |
| Bugbot per person | Bugbot data is per repo / PR; needs a GitHub PR-author join. |
| Governance checklist | Approval gates, rollback plan, kill switch: admin / coach checklist. |
| Automation owner | Automations under a service account carry serviceAccountId, not a person; they are credited to their owner via a maintained owner list. |
| Team rule / hook author | Audit logs credit whoever saved it. When an admin saves one on someone's behalf, the admin records the real author in the author log. |
| Parallel agents | Only a proxy (overlapping conversationId); not used as a gate. |
| Output quality | Agent and Automation output quality, defect rate, cycle time: coach check or GitHub / Jira, not Cursor APIs. |
| Persona | From HR / SCIM groups. |

API notes: Admin, Analytics and AI Code Tracking APIs are Enterprise-only. AI Code Tracking is in Alpha and covers the top-level repo only. Every date-ranged endpoint caps at 30 days (Analytics defaults to 7; pass startDate=28d). Rate limits: 20/min for daily usage and audit logs, 60/min for usage events.

## PL1 | AI-Assisted

_Proficiency level 1 of 4._ Header: Assisted individuals. Cursor desktop becomes your home base, in the editor and the Agents window.

**Why this matters to you**: You stop doing the tedious parts by hand. In the editor, Tab and inline edit handle the obvious lines; in the Agents window, Agent explains unfamiliar code, drafts tests and fixes the boring bugs. You get back time lost to lookups, boilerplate and context-switching, and knowing when to type, edit inline or brief an agent is a skill that goes with you to any team.

**Why it matters to the organization**: One shared baseline across teams: everyone on the same Cursor setup, licensed seats in real use, and a clear starting point for the software factory.

### Step 1 · Explore

_“This can actually help.”  You get fluent in Cursor desktop, in the editor and the Agents window._

**What it looks like**

In the editor, Tab completes the obvious lines, inline edit rewrites a selected block, and Ask explains an unfamiliar module. In the Agents window, you hand Agent a first real task, such as a unit test or a small bug fix, and review the diff before you keep it.

**To advance**

- Next: Step 2.
- Signal: you reach for Agent most weeks, not only Tab and inline edit.
- PL1 gate: regular active days (Metrics & APIs).

### Step 2 · Cursor-first

_“Coding starts in Cursor.”  Agent is your default for anything beyond a small edit._

**What it looks like**

Coding work starts in Cursor, in whichever surface fits. Small edits stay in the editor with Tab and inline edit. Anything bigger, such as a test suite, a refactor or a new API, goes to Agent in the editor or the Agents window; you review the diff and keep what's right.

**To advance**

- Next: PL2.
- Meet every PL2 gate: steady Agent use, skills reused week to week, Plan mode, AI lines on the primary branch.
- Thresholds: Metrics & APIs.

### At this level, by persona

_One shared scale; the evidence behind each level differs by role._

- **Developer IC**: The editor and the Agents window are both part of your day; Agent takes tests, refactors and debugging. Evidence: active days, Agent share of requests, AI lines in your commits.
- **Eng Leadership**: Use Cursor on your own work (reviews, design docs, scripts) and get your group active. Follow up on the never-engaged list.
- **PM / Specialist**: Use Ask and Agent in Cursor desktop to read code, draft specs and answer “how does this work?” without waiting for an engineer. Evidence: active days, accepted agent diffs.
- **Guardrails & HITL**: Know which code and data are allowed in Cursor. Review every diff before you accept it: you own what you merge.

**Key Shift**: From “AI is something I try now and then” to “coding starts in Cursor, and Agent takes anything bigger than a small edit.”

## PL2 | Reusable Agents

_Proficiency level 2 of 4._ Header: Codified team workflows. Rules and skills make your agents persist and behave the same every time.

**Why this matters to you**: You stop re-explaining your codebase every chat. Rules carry your conventions and skills carry your workflows, so the agent gets it right the first time and you fix less rework. Hooks, plugins and MCP servers extend what it can see and do. You get back the setup time on every task, and turning good practice into reusable agents is a skill any team values.

**Why it matters to the organization**: The same rules, skills and checks in every repo, so output is consistent across teams. This is Stage 2, codified team workflows: the foundation the software factory is built on, and what makes delegation safe later.

### Step 3 · Codify

_“I wrote it down once.”  Rules and skills remember how you work._

**What it looks like**

You turn what you keep repeating into rules and skills: a project rule for conventions, AGENTS.md for how the repo builds and tests, a skill for your PR review or migration workflow. You manage them in Customize, and big changes start in Plan mode.

**To advance**

- Next: Step 4.
- Signal: your skills get reused week to week, big changes start in Plan mode, and repo rules / AGENTS.md are in place*.

### Step 4 · Standardize & verify

_“I have a system for this.”  Same setup, same result, every time._

**What it looks like**

Each task type starts from a skill with tests in the loop, and team rules keep output consistent. You extend the agent where it helps: a hook that runs format and lint, a plugin from the Cursor Marketplace, an MCP server that gives it your docs or tickets while you drive. Bugbot reviews your PRs.

**To advance**

- Next: PL3.
- Meet every PL3 gate: skills used most weeks, Cloud Agent runs, MCP use, cloud-originated commits.
- Thresholds: Metrics & APIs.

### At this level, by persona

_One shared scale; the evidence behind each level differs by role._

- **Developer IC**: Your repo has rules, AGENTS.md and skills you use every week, plus the hooks and MCP servers your work needs. Evidence: skills reused across weeks, Plan mode, AI lines on the primary branch.
- **Eng Leadership**: Sponsor shared rules and skills per repo, an approved plugin and MCP list, and tests and Bugbot as the default. Team outcome: your group's share at PL2+.
- **PM / Specialist**: Codify recurring work as skills (spec templates, release notes, test plans) and pull in docs and tickets via MCP. Evidence: skills reused across weeks, accepted agent diffs.
- **Guardrails & HITL**: Rules and hooks are where guardrails start: blocked shell commands, protected paths, no secrets in context. Only vetted plugins and MCP servers. Keep a human review on every merge.

**Key Shift**: From “re-explain it every time” to “rules and skills set it up once, and I get the same result every time.”

## PL3 | Delegational Orchestration  (Org Target)

_Proficiency level 3 of 4._ Header: AI SDLC (Software Factory).  You hand scoped work to parallel agents that act on your behalf, and review the results.

**Why this matters to you**: You stop being the bottleneck on every task. Cloud Agents work through well-specified tickets in parallel while you focus on design, review and the hard problems. You get back whole blocks of time, and breaking work into delegable pieces and directing agents is becoming a core engineering skill.

**Why it matters to the organization**: This is the AI SDLC (Software Factory): agents carry work across requirements, code, hardening, testing and deployment, with human-in-the-loop checkpoints. It is the recommended org target.

### Step 5 · Delegate & parallelize

_“Let me hand this off.”  Several agents work while you review._

**What it looks like**

You write a clear spec, then hand it off: a Cloud Agent implements the feature on its own branch while another writes the tests. Locally you run parallel agents in worktrees to compare approaches. You come back to PRs, review and merge.

**To advance**

- Next: Step 6.
- Signal: well-scoped tickets go to Cloud Agents and come back as PRs you review.

### Step 6 · Agents act as you

_“My agents use my tools.”  With your access, inside guardrails._

**What it looks like**

Agents read the Jira ticket, check Confluence and open the PR as you through MCP. A scheduled Automation triages new issues each morning and drafts fixes for your review. For non-code work, the same pattern can extend to your other tools (optional), for example Grok Bot for knowledge-work tasks outside the editor.

**To advance**

- Next: PL4.
- Meet every PL4 gate: an Automation running week over week, a team rule or hook you authored (if an admin saves it, they log you as author), cloud commits most weeks.
- Thresholds: Metrics & APIs.

### At this level, by persona

_One shared scale; the evidence behind each level differs by role._

- **Developer IC**: Well-specified tickets go to Cloud Agents; you review the PRs. Evidence: Cloud Agent runs, cloud-originated commits, days with MCP use.
- **Eng Leadership**: Make delegation safe: branch protection, required review, Bugbot, an approved MCP list. Team outcome: your group's share at PL3+ and never-engaged count.
- **PM / Specialist**: Agents pull tickets and docs through MCP, draft specs and release notes, and run recurring reports as Automations. Evidence: MCP days, Cloud Agent and Automation runs, accepted agent diffs.
- **Guardrails & HITL**: Every agent PR gets a human review and Bugbot. MCP servers are least-privilege and team-approved. You are accountable for what agents do as you.

**Key Shift**: From “one agent, me watching” to “several agents working, me reviewing.”

## PL4 | Governed Autonomy

_Proficiency level 4 of 4._ Header: AI SDLC → Cross-functional AI Transformation.  Event-driven agents run end to end behind approval gates, hooks and an audit trail.

**Why this matters to you**: You design the system instead of running every task. Routine work such as CI failures, dependency updates and triage is handled by pipelines you built, so your time goes to architecture and the calls only a human should make. Building governed agent systems is senior engineering work anywhere.

**Why it matters to the organization**: Autonomy the organization can trust: policy checkpoints are built into the agent workflow, blocked actions leave an audit trail, and every change can be rolled back. PL4 means governed, not unsupervised. Your patterns become the shared delivery blueprint other teams adopt.

### Step 7 · Governed pipelines

_“My agents run without me starting them.”  Behind gates you designed._

**What it looks like**

A CI failure triggers an agent that diagnoses it and opens a fix PR before you're in. Dependency updates run on a schedule. Changes to data, schemas, security or prod stop at an approval gate. Hooks block destructive commands with a clear blocked-action path, and every run is in the audit log.

**To advance**

- Next: Step 8.
- Signal: an Automation runs week over week behind approval gates, with the governance checklist signed off*.

### Step 8 · Multiply

_“Others run what I built.”  Your patterns become the standard._

**What it looks like**

You publish the rules, skills, hooks and Automations other teams adopt. You watch how they're used, fix what breaks and retire what doesn't pay off. You help the next team adopt the pattern as a shared delivery blueprint, and extend it beyond engineering where it fits (optionally with Grok Bot for cross-workflow knowledge work).

**To advance**

- Stay at PL4.
- Keep meeting every PL4 gate; others adopting the skills you publish is a coach check*.
- Thresholds: Metrics & APIs.

### At this level, by persona

_One shared scale; the evidence behind each level differs by role._

- **Developer IC**: You design and own governed pipelines for your repos. Evidence: Automations over time, cloud-originated commits, team rules and hooks you authored (admin-saved ones logged under your name).
- **Eng Leadership**: You set the gates: which changes need approval, who owns each Automation, how audits run. Team outcome: your group's share at PL3+.
- **PM / Specialist**: Recurring PM work (status, release notes, triage) runs as owned Automations. Grok Bot can optionally carry the cross-workflow knowledge work around them; it never counts toward a gate. Evidence: Automations running week over week.
- **Guardrails & HITL**: Human sign-off at architecture, security, data / schema and prod deploy. Hooks, audit logs and a rollback plan on every pipeline. Not zero human intervention.

**Key Shift**: From “I run the agents” to “I design governed systems that run them.” Humans still own the risk gates.

## Notes for the plugin builder

- **Metrics & APIs is authoritative.** Compute levels only from the threshold grid and scoring rules (section 2). Treat the Overview and PL-level text as description, not as gates.
- **\* items never set the level.** Coach checks and items that can't be verified by API are shown next to the level only. Two maintained lists do feed attribution, so decide up front how to treat a missing entry:
  - the author log, for team rules and hooks an admin saves on someone's behalf;
  - the Automation owner list, for runs under a service account.
- **Privacy.** Usage metadata only. Drop commit `message` when ingesting `/analytics/ai-code/commits`. Don't call conversation-insights or the file-level blame endpoints.
- **Next steps.** Draw them from the smallest unmet gate, via the "Gap → first action" table in `cursor-playbook.md`.
