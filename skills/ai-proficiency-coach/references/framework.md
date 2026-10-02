# AI Proficiency framework reference

> Reference framework for the **AI Proficiency Coach** Cursor plugin: what the four proficiency levels and eight Steps mean, and what each looks like from the outside (section 2).
>
> This is a coaching framework, not a scoring one. Nothing here is computed, and the plugin reads no usage data; it places people by conversation and recognition cues.
>
> Per-step actions, exercises, what to avoid and org unblocks live in `cursor-playbook.md`. Keep them out of this file so there is one place to change them.

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

## 2. Signals you'd notice

What each pillar looks like from the outside at each level. These are signals for a coaching conversation, not thresholds: they help you place someone and name what's holding them back. Levels are cumulative, so someone is roughly at the lowest level their four pillars agree on.

| Pillar | PL1 | PL2 | PL3 | PL4 |
|---|---|---|---|---|
| Adoption | Cursor open most workdays; Tab and the odd question | Agent is the default for anything beyond a small edit | Cursor is where work starts, and several agents run at once | Work arrives already started by an agent |
| Reuse | Context re-explained each chat | Rules, `AGENTS.md` and a skill or two, reused week to week; Plan Mode before big changes | The same skills carry most task types; hooks and MCP extend them | Team rules and hooks others pick up |
| Orchestration | One agent, watched | Agent extended with hooks, plugins or an MCP server | Cloud Agents take scoped tickets; MCP lets agents act as you | Automations run on events and schedules, behind approval gates |
| Outcomes · Developer IC | AI writes code you keep | AI-written code lands on the primary branch regularly | Cloud Agents open PRs you review and merge | Cloud commits most weeks, from pipelines you own |
| Outcomes · Eng Leadership | You use Cursor on your own work; your group is active | Most of the group has rules and skills in place | Much of the group delegates to Cloud Agents; nobody is never-engaged | The group runs governed pipelines, and you set the gates |
| Outcomes · PM / Specialist | You accept agent edits on real work | Recurring work is codified as skills | MCP pulls tickets and docs; agents draft and report | Recurring work runs as Automations you own |

Things to notice but never score: repo rules and `AGENTS.md` in place, human review on every agent PR, a signed-off governance checklist, Bugbot findings resolved, and whether other people have adopted what someone built. Raise them as coaching points, not criteria.

**Placement, not measurement.** Someone is usually between two Steps and uneven across pillars. Say so, coach the pillar that's holding them back, and don't attach a number to it. If an org wants to measure this rather than coach it, that's a separate exercise built on the Cursor Admin, Analytics and AI Code Tracking APIs (Enterprise); this skill deliberately doesn't do it.

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

### Step 2 · Cursor-first

_“Coding starts in Cursor.”  Agent is your default for anything beyond a small edit._

**What it looks like**

Coding work starts in Cursor, in whichever surface fits. Small edits stay in the editor with Tab and inline edit. Anything bigger, such as a test suite, a refactor or a new API, goes to Agent in the editor or the Agents window; you review the diff and keep what's right.

**To advance**

- Next: PL2.
- What PL2 looks like: steady Agent use, skills reused week to week, Plan Mode before big changes, AI-written code on the primary branch.

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
- What PL3 looks like: skills used most weeks, Cloud Agents running, MCP in daily work, cloud-originated commits.

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
- What PL4 looks like: an Automation running week over week, a team rule or hook you authored, cloud commits most weeks.

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
- Keep the PL4 habits going. Others adopting what you publish is the sign this one landed.

### At this level, by persona

_One shared scale; the evidence behind each level differs by role._

- **Developer IC**: You design and own governed pipelines for your repos. Evidence: Automations over time, cloud-originated commits, team rules and hooks you authored (admin-saved ones logged under your name).
- **Eng Leadership**: You set the gates: which changes need approval, who owns each Automation, how audits run. Team outcome: your group's share at PL3+.
- **PM / Specialist**: Recurring PM work (status, release notes, triage) runs as owned Automations. Grok Bot can optionally carry the cross-workflow knowledge work around them; it never counts toward a gate. Evidence: Automations running week over week.
- **Guardrails & HITL**: Human sign-off at architecture, security, data / schema and prod deploy. Hooks, audit logs and a rollback plan on every pipeline. Not zero human intervention.

**Key Shift**: From “I run the agents” to “I design governed systems that run them.” Humans still own the risk gates.

## Notes for the plugin builder

- **Nothing here is computed.** Place people from the recognition cues in `cursor-playbook.md` and the signals in section 2. Never produce a score, a percentage or a level with a number attached beyond PL1-PL4.
- **Next steps come only from `cursor-playbook.md`**, from the person's current Step. Don't invent actions, and don't recommend non-Cursor tools.
- **Privacy.** Coach from what someone tells you and what's visible in the conversation. Don't ask for usage exports or dashboards, and don't go reading their history, prompts, code or diffs to assess them.
- **Coaching, not appraisal.** Say so if anyone asks whether this feeds a review.
