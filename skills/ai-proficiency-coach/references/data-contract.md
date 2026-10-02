# AI Proficiency Coach: weekly input data contract

**What this is.** The per-person, per-week input row the "AI Proficiency Coach" plugin reads. The coach turns each row into a weekly level and 1–2 next steps, using the gates in `framework.md` §2 (Metrics & APIs is the source of truth).

**API sources.** Every API field below comes from Cursor's public API docs:

- Admin API
- Analytics API
- AI Code Tracking API

**Field types.**

- **API**: pulled from a Cursor API.
- **Derived**: computed from API fields.
- **Manual \***: a coach check or maintained list. Per the framework, \* items are "shown next to the PL, never used to set it". Two maintained lists (the author log and the Automation owner list) feed attribution; see "Notes for the plugin builder" in `framework.md`.

---

## 1. Time window

| Item | Rule |
|---|---|
| Run cadence | Every Monday (framework: "recomputed every Monday"). |
| Window | Trailing **28 days**, ending the day before the run (`window_start` … `window_end`, inclusive). |
| Week buckets | Four consecutive 7-day buckets **W1–W4** inside the window (W4 is the most recent). Every "in ≥N of 4 weeks" gate counts buckets, not calendar weeks. |
| API date caps | Every date-ranged endpoint caps at 30 days, so one 28-day request per endpoint fits. Analytics endpoints default to 7 days, so always pass `startDate=28d` (or explicit dates). Admin endpoints take epoch-ms `startDate` / `endDate`. |
| Rate limits | 20 req/min for `/teams/daily-usage-data` and `/teams/audit-logs`; 60 req/min for `/teams/filtered-usage-events`. Daily usage data is aggregated hourly (poll at most hourly). |
| Plan | Admin, Analytics and AI Code Tracking APIs are Enterprise-only. AI Code Tracking is Alpha and covers the top-level repo of the workspace only. |

---

## 2. The row

### 2.1 Identity and context

| Field | Type | Source | How to get it |
|---|---|---|---|
| `week_ending` | date | Derived | `window_end`. |
| `window_start`, `window_end` | date | Derived | See §1. |
| `email` | string | API | `GET /teams/members` → `email`. This is the join key for every other endpoint. |
| `user_id` | string | API | `GET /teams/members` → `id` (`user_…`). |
| `name` | string | API | `GET /teams/members` → `name`. |
| `is_removed` | bool | API | `GET /teams/members` → `isRemoved`. Exclude removed members. |
| `persona` | `"IC"` \| `"LEADER"` \| `"PM"` | **Manual \*** | Framework: "Persona: From HR / SCIM groups". Supply it from HR/SCIM, or map directory groups to personas. No Cursor field holds the persona. |
| `led_group_id` | string \| null | **Manual \*** (leaders only) | Which directory group a leader is measured on. Group membership comes from `GET /teams/directory-groups/:groupId/members` → `email`. |

### 2.2 Adoption (all personas)

Source: `POST /teams/daily-usage-data` with `startDate`/`endDate` (epoch ms) **and `page`/`pageSize`**. `isActive` is only returned when you paginate.

| Field | Type | Derivation | Gate use |
|---|---|---|---|
| `active_days` | int 0–28 | Count of days with `isActive = true` for this `email`. | PL1 ≥4 · PL2 ≥12 · PL3 ≥14 · PL4 ≥16 |
| `agent_requests` | int | Sum of `agentRequests`. | PL2–PL4: `agent_requests ≥ chat_requests` |
| `chat_requests` | int | Sum of `chatRequests`. | (as above) |
| `tabs_accepted` | int | Sum of `totalTabsAccepted`. | Not gated. Coaching context for Step 1–2 ("not only Tab"). |
| `inline_edit_uses` | int | Sum of `cmdkUsages`. | Not gated. Coaching context for Step 1–2. |

### 2.3 Reuse

| Field | Type | Source → derivation | Gate use |
|---|---|---|---|
| `skills` | array of `{skill_name, weeks_used (0–4), uses}` | `GET /analytics/by-user/skills?startDate=28d&users=<email>` → `skill_name`, `event_date`, `usage`. Bucket `event_date` into W1–W4. | — |
| `skills_in_2of4_weeks` | int | Derived: number of `skills` with `weeks_used ≥ 2`. | PL2 ≥2 |
| `skills_in_3of4_weeks` | int | Derived: number of `skills` with `weeks_used ≥ 3`. | PL3 ≥3 (PL4 inherits) |
| `plan_mode_uses` | int | `GET /analytics/by-user/plans?startDate=28d` → sum of `usage`. | PL2–PL4 ≥4 |
| `team_rules_hooks_authored` | int | `GET /teams/audit-logs?eventTypes=team_rule,team_hook` (≤30-day range) → count events where `user_email` = this person. Add entries from `author_log` (below) where an admin saved it on this person's behalf. | PL4 ≥1 |

> Open item: the saved docs don't describe `event_data` for `team_rule` / `team_hook`. Check whether it separates create / update / delete before deciding what counts as "authored". Today every event counts.

### 2.4 Orchestration

| Field | Type | Source → derivation | Gate use |
|---|---|---|---|
| `cloud_agent_runs` | int | `POST /teams/filtered-usage-events` with `email=<email>`, `cloudAgentId="*"`, 28-day range → count of **distinct** `cloudAgentId`. | PL3 ≥4 (PL4 inherits) |
| `mcp_days` | int 0–28 | `GET /analytics/by-user/mcp?startDate=28d` → distinct `event_date` with `usage > 0` (any `mcp_server_name`). | PL3 ≥3 (PL4 inherits) |
| `automations` | array of `{automation_id, weeks_active (0–4), attribution}` | `POST /teams/filtered-usage-events` with `automationId="*"` → `automationId`, `timestamp`, `userEmail`, `serviceAccountId`. A week is active if there is ≥1 event in that bucket. `attribution` = `"direct"` when `userEmail` = this person and `serviceAccountId` is absent, or `"owner_list"` when the event has a `serviceAccountId` and `automation_owner_list` maps it to this person. | — |
| `automations_active_3of4_weeks` | int | Derived: number of `automations` with `weeks_active ≥ 3`. | Orchestration PL4 ≥1 · PM Outcomes PL4 ≥2 |

### 2.5 Outcomes by persona

**Developer IC.** Source: `GET /analytics/ai-code/commits?startDate=28d&user=<email>` → `isPrimaryBranch`, `commitSource`, `tabLinesAdded`, `composerLinesAdded`, `commitTs`.
**Drop `message` at ingestion** (privacy).
Here "AI lines" = `tabLinesAdded + composerLinesAdded` > 0.

| Field | Type | Derivation | Gate use |
|---|---|---|---|
| `commits_with_ai_lines` | int | Commits on any branch with AI lines. | PL1 ≥1 |
| `primary_commits` | int | Commits with `isPrimaryBranch = true`. | — |
| `primary_commits_with_ai_lines` | int | Primary-branch commits with AI lines. | — |
| `primary_ai_commit_share` | float 0–1 \| null | `primary_commits_with_ai_lines / primary_commits` (null if 0). | PL2 ≥0.30 |
| `primary_cloud_commits` | int | Primary-branch commits with `commitSource = "cloud"`. | PL3 ≥3 |
| `primary_cloud_commit_weeks` | int 0–4 | Number of W1–W4 buckets (by `commitTs`) with ≥1 primary cloud commit. | PL4 ≥3 |

**PM / Specialist.** Also uses `automations_active_3of4_weeks` (§2.4).

| Field | Type | Source → derivation | Gate use |
|---|---|---|---|
| `accepted_diff_days` | int 0–28 | `GET /analytics/by-user/agent-edits?startDate=28d` → distinct `event_date` with `total_accepted_diffs > 0`. | PL1 ≥1 · PL2 ≥4 · PL3 ≥8 · PL4 ≥8 (+ ≥2 Automations in ≥3 of 4 weeks) |

**Eng Leadership.** Computed in a second pass, after every individual's level is known. Members come from `GET /teams/directory-groups/:groupId/members` → `email`, joined to their computed levels.

| Field | Type | Derivation | Gate use |
|---|---|---|---|
| `group_size` | int | Members of `led_group_id`. | — |
| `group_level_counts` | `{PL0, PL1, PL2, PL3, PL4}` | Members' computed weekly levels (PL0 = below PL1). | — |
| `group_share_pl1_plus` | float | (PL1+PL2+PL3+PL4) / size | PL1 ≥0.50 |
| `group_share_pl2_plus` | float | (PL2+PL3+PL4) / size | PL2 ≥0.50 |
| `group_share_pl3_plus` | float | (PL3+PL4) / size | PL3 ≥0.30 · PL4 ≥0.50 |
| `group_never_engaged_share` | float | Members with `active_days = 0` / size. Framework: "`GET /teams/members` minus active users in `daily-usage-data`". | PL3, PL4 ≤0.10 |

### 2.6 Coach checks and maintained lists (manual \*)

These are never fetched from Cursor APIs. Use `null` when unknown.

| Field | Type | Who supplies it | Shown at |
|---|---|---|---|
| `coach_checks.repo_rules_in_place` | bool \| null | GitHub repo scan or coach ("Repo rules / AGENTS.md"). | PL2 |
| `coach_checks.agent_prs_human_reviewed` | bool \| null | Coach. | PL3 |
| `coach_checks.governance_checklist_signed_off` | bool \| null | Admin / coach checklist (approval gates, rollback plan, kill switch). | PL4 |
| `coach_checks.no_unresolved_high_sev_bugbot` | bool \| null | `GET /analytics/team/bugbot-reviews` → `bugs[].severity`, `bugs[].resolution_status`, `repo`, `pr_number`, joined to PR authors from **GitHub**. Bugbot data has no author field. | PL4 |
| `coach_checks.skills_adopted_by_others` | bool \| null | Coach. Skill usage is per user; authorship is not exposed. | PL4 |
| `author_log` | array of `{type: "team_rule" \| "team_hook", name, saved_by_admin, real_author_email, date}` | Admins, when they save a team rule or hook on someone's behalf. | Feeds `team_rules_hooks_authored` |
| `automation_owner_list` | array of `{service_account_id \| automation_id, owner_email}` | Maintained by admins. Automations under a service account carry `serviceAccountId`, not a person. | Feeds `automations[].attribution` |

---

## 3. What the coach computes (outputs, not inputs)

- **`level`**: the highest level with no *failed* gate at that level or below (gates are cumulative; "Not required" counts as met). One week's snapshot, recomputed from scratch each Monday. `null` when no pillar had any data.
- **`level_provisional`** / **`unknown_pillars`**: true when some gate input was unknown rather than failed. A provisional level is an **upper bound**: the unknown gate could still fail once the data arrives.
- **`unmet_gates_for_next_level`**: every gate blocking the next level, smallest relative gap first.
- **`missing_fields`**: gate inputs that were null. A null is unknown, not zero: it neither meets nor fails its gate, so it cannot by itself push someone down a level.
- **`never_engaged`**: `active_days == 0`.
- **`next_steps`**: 1–2 suggestions, from the smallest unmet gate via the "Gap → first action" table in `cursor-playbook.md`.

---

## 4. Example row (ALL VALUES ARE FAKE, for illustration only)

```json
{
  "_comment": "FAKE EXAMPLE DATA. Not a real person, not real usage.",
  "week_ending": "2026-09-27",
  "window_start": "2026-08-31",
  "window_end": "2026-09-27",
  "email": "fake.developer@example.com",
  "user_id": "user_FAKE000000000000",
  "name": "Fake Developer",
  "is_removed": false,
  "persona": "IC",
  "led_group_id": null,

  "active_days": 15,
  "agent_requests": 240,
  "chat_requests": 95,
  "tabs_accepted": 1300,
  "inline_edit_uses": 42,

  "skills": [
    {"skill_name": "fake-pr-review", "weeks_used": 4, "uses": 19},
    {"skill_name": "fake-migration-helper", "weeks_used": 3, "uses": 7},
    {"skill_name": "fake-release-notes", "weeks_used": 2, "uses": 3}
  ],
  "skills_in_2of4_weeks": 3,
  "skills_in_3of4_weeks": 2,
  "plan_mode_uses": 9,
  "team_rules_hooks_authored": 0,

  "cloud_agent_runs": 5,
  "mcp_days": 6,
  "automations": [],
  "automations_active_3of4_weeks": 0,

  "commits_with_ai_lines": 31,
  "primary_commits": 40,
  "primary_commits_with_ai_lines": 22,
  "primary_ai_commit_share": 0.55,
  "primary_cloud_commits": 2,
  "primary_cloud_commit_weeks": 2,

  "accepted_diff_days": null,
  "group_size": null,
  "group_level_counts": null,
  "group_share_pl1_plus": null,
  "group_share_pl2_plus": null,
  "group_share_pl3_plus": null,
  "group_never_engaged_share": null,

  "coach_checks": {
    "repo_rules_in_place": true,
    "agent_prs_human_reviewed": null,
    "governance_checklist_signed_off": null,
    "no_unresolved_high_sev_bugbot": null,
    "skills_adopted_by_others": null
  },
  "author_log": [],
  "automation_owner_list": []
}
```

**How the fake row scores** (worked against the Metrics gates):

- **Adoption** clears PL3: 15 active days (≥14, short of PL4's ≥16) and agent requests ≥ chat requests.
- **Reuse** stops at PL2: 2 skills in ≥3 of 4 weeks, short of PL3's ≥3.
- **Orchestration** clears PL3: 5 Cloud Agent runs (≥4) and 6 MCP days (≥3); no Automations for PL4.
- **Outcomes (IC)** stops at PL2: a 55% primary-branch share clears PL2 (≥30%), but 2 primary cloud commits miss PL3 (≥3).
- **Level = PL2.** Gates are cumulative, so Reuse and Outcomes cap it.
- **The two smallest gaps.** One more skill used in ≥3 of 4 weeks, and one more primary-branch cloud commit.

---

## 5. Feeding `scripts/score.py`

- **JSON**: one row object, or an array of row objects, exactly as in §4. See `examples/fake-ic-row.json`.
- **CSV**: one row per person-week with the §2 field names as headers. List and object fields (`skills`, `automations`, `author_log`, `automation_owner_list`, `group_level_counts`) go in JSON-encoded cells. Coach checks may be given as `coach_checks.<name>` columns. See `examples/fake-team.csv`.
- **Derived fields** may be omitted when their raw source is present. The script derives `skills_in_2of4_weeks` and `skills_in_3of4_weeks` from `skills`, `automations_active_3of4_weeks` from `automations`, `team_rules_hooks_authored` from `author_log` (matched on `real_author_email`), `primary_ai_commit_share` from the commit counts, and leader `group_share_*` from `group_level_counts` and `group_size`.
- **Nulls**: a null gate input is *unknown*. It neither meets nor fails its gate, is reported under `missing_fields`, and marks the level provisional. Send a real `0` only when you know the value is zero; a null that should have been a zero inflates the level, and a zero that should have been a null deflates it.
- Rows with `is_removed = true` are skipped.
