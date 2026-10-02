#!/usr/bin/env python3
"""Score weekly AI Proficiency rows (PL1-PL4) per references/framework.md section 2.

Input: one JSON object, a JSON array of objects, or a CSV file, each row shaped
like references/data-contract.md section 2. In CSV, list/object fields
(skills, automations, author_log, automation_owner_list, group_level_counts)
are JSON-encoded cells, and coach checks may be given as `coach_checks.<name>`
columns.

Usage:
  python3 score.py ROW.json              # human-readable summary
  python3 score.py ROWS.csv --json       # machine-readable output
  python3 score.py ROWS.csv --team       # add PL0-PL4 mix and never-engaged count
  python3 score.py ROW.json --self-reported
  cat ROW.json | python3 score.py -

Standard library only. Missing (null) inputs fail their gate and are listed
under missing_fields; they are never treated as real zeros in the output text.
"""

import argparse
import csv
import io
import json
import sys

PILLARS = ("adoption", "reuse", "orchestration", "outcomes")
PERSONAS = ("IC", "LEADER", "PM")

COACH_CHECKS = {
    "repo_rules_in_place": (2, "Repo rules / AGENTS.md in place"),
    "agent_prs_human_reviewed": (3, "Every agent PR human-reviewed"),
    "governance_checklist_signed_off": (4, "Governance checklist signed off"),
    "no_unresolved_high_sev_bugbot": (4, "No unresolved high-severity Bugbot findings"),
    "skills_adopted_by_others": (4, "Your skills adopted by others"),
}

JSON_CELL_FIELDS = (
    "skills",
    "automations",
    "author_log",
    "automation_owner_list",
    "group_level_counts",
    "coach_checks",
)


class Gate:
    """One comparison inside a pillar gate."""

    def __init__(self, field, label, value, op, threshold):
        self.field = field
        self.label = label
        self.value = value
        self.op = op
        self.threshold = threshold

    @property
    def missing(self):
        return self.value is None or self.threshold is None

    @property
    def met(self):
        if self.missing:
            return False
        if self.op == ">=":
            return self.value >= self.threshold
        return self.value <= self.threshold

    @property
    def unmet(self):
        """Only a gate we have data for can block a level. Missing data is unknown, not failed."""
        return not self.missing and not self.met

    @property
    def gap(self):
        if self.met:
            return 0
        if self.missing:
            return None
        return abs(self.threshold - self.value)

    @property
    def relative_gap(self):
        if self.missing:
            return float("inf")
        if self.met:
            return 0.0
        base = abs(self.threshold) if self.threshold else 1.0
        return self.gap / base

    def to_dict(self, pillar, level):
        return {
            "level": level,
            "pillar": pillar,
            "field": self.field,
            "gate": self.label,
            "have": self.value,
            "need": "%s %s" % (self.op, _fmt(self.threshold)),
            "gap": _round(self.gap),
            "missing_data": self.missing,
        }


def _fmt(value):
    if isinstance(value, float):
        return ("%.2f" % value).rstrip("0").rstrip(".")
    return str(value)


def _round(value):
    if isinstance(value, float):
        return round(value, 4)
    return value


def _num(row, key):
    value = row.get(key)
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return value
    try:
        text = str(value).strip()
        return float(text) if "." in text else int(text)
    except ValueError:
        return None


def _bool(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "y"):
        return True
    if text in ("false", "0", "no", "n"):
        return False
    return None


def derive(row):
    """Fill derived fields from their raw arrays when the derived value is absent."""
    row = dict(row)
    skills = row.get("skills") or []
    if _num(row, "skills_in_2of4_weeks") is None and row.get("skills") is not None:
        row["skills_in_2of4_weeks"] = sum(1 for s in skills if (s.get("weeks_used") or 0) >= 2)
    if _num(row, "skills_in_3of4_weeks") is None and row.get("skills") is not None:
        row["skills_in_3of4_weeks"] = sum(1 for s in skills if (s.get("weeks_used") or 0) >= 3)

    autos = row.get("automations") or []
    if _num(row, "automations_active_3of4_weeks") is None and row.get("automations") is not None:
        row["automations_active_3of4_weeks"] = sum(
            1 for a in autos if (a.get("weeks_active") or 0) >= 3
        )

    if _num(row, "team_rules_hooks_authored") is None and row.get("author_log") is not None:
        email = (row.get("email") or "").lower()
        row["team_rules_hooks_authored"] = sum(
            1
            for entry in row["author_log"]
            if (entry.get("real_author_email") or "").lower() == email
        )

    if _num(row, "primary_ai_commit_share") is None:
        primary = _num(row, "primary_commits")
        with_ai = _num(row, "primary_commits_with_ai_lines")
        if primary and with_ai is not None:
            row["primary_ai_commit_share"] = with_ai / primary
        elif primary == 0:
            # The contract nulls the share when there are no primary commits; that is a real 0%.
            row["primary_ai_commit_share"] = 0.0

    counts = row.get("group_level_counts")
    size = _num(row, "group_size")
    if isinstance(counts, dict) and size:
        def share(levels):
            return sum(_num(counts, "PL%d" % lvl) or 0 for lvl in levels) / size

        if _num(row, "group_share_pl1_plus") is None:
            row["group_share_pl1_plus"] = share((1, 2, 3, 4))
        if _num(row, "group_share_pl2_plus") is None:
            row["group_share_pl2_plus"] = share((2, 3, 4))
        if _num(row, "group_share_pl3_plus") is None:
            row["group_share_pl3_plus"] = share((3, 4))
    return row


def pillar_gates(row, persona):
    """Return {pillar: {level: [Gate, ...]}} for levels 1-4. Empty list = "Not required"."""
    n = lambda key: _num(row, key)  # noqa: E731
    agent, chat = n("agent_requests"), n("chat_requests")
    agent_vs_chat = Gate(
        "agent_requests",
        "agentRequests >= chatRequests",
        agent,
        ">=",
        chat,
    )

    def active(days):
        return Gate("active_days", "active days", n("active_days"), ">=", days)

    def plan():
        return Gate("plan_mode_uses", "Plan mode uses", n("plan_mode_uses"), ">=", 4)

    adoption = {
        1: [active(4)],
        2: [active(12), agent_vs_chat],
        3: [active(14), agent_vs_chat],
        4: [active(16), agent_vs_chat],
    }

    reuse_pl3 = [
        Gate("skills_in_3of4_weeks", "skills each used in >=3 of 4 weeks",
             n("skills_in_3of4_weeks"), ">=", 3),
        plan(),
    ]
    reuse = {
        1: [],
        2: [
            Gate("skills_in_2of4_weeks", "skills each used in >=2 of 4 weeks",
                 n("skills_in_2of4_weeks"), ">=", 2),
            plan(),
        ],
        3: reuse_pl3,
        4: reuse_pl3 + [
            Gate("team_rules_hooks_authored", "team rules or team hooks authored",
                 n("team_rules_hooks_authored"), ">=", 1),
        ],
    }

    orch_pl3 = [
        Gate("cloud_agent_runs", "Cloud Agent runs (distinct cloudAgentId)",
             n("cloud_agent_runs"), ">=", 4),
        Gate("mcp_days", "days with MCP use", n("mcp_days"), ">=", 3),
    ]
    orchestration = {
        1: [],
        2: [],
        3: orch_pl3,
        4: orch_pl3 + [
            Gate("automations_active_3of4_weeks", "Automations active in >=3 of 4 weeks",
                 n("automations_active_3of4_weeks"), ">=", 1),
        ],
    }

    if persona == "IC":
        outcomes = {
            1: [Gate("commits_with_ai_lines", "commits with AI lines",
                     n("commits_with_ai_lines"), ">=", 1)],
            2: [Gate("primary_ai_commit_share", "share of primary-branch commits with AI lines",
                     n("primary_ai_commit_share"), ">=", 0.30)],
            3: [Gate("primary_cloud_commits", "primary-branch commits with commitSource = cloud",
                     n("primary_cloud_commits"), ">=", 3)],
            4: [Gate("primary_cloud_commit_weeks", "weeks (of 4) with primary-branch cloud commits",
                     n("primary_cloud_commit_weeks"), ">=", 3)],
        }
    elif persona == "LEADER":
        never = Gate("group_never_engaged_share", "share of group never-engaged",
                     n("group_never_engaged_share"), "<=", 0.10)
        outcomes = {
            1: [Gate("group_share_pl1_plus", "share of group at PL1+",
                     n("group_share_pl1_plus"), ">=", 0.50)],
            2: [Gate("group_share_pl2_plus", "share of group at PL2+",
                     n("group_share_pl2_plus"), ">=", 0.50)],
            3: [Gate("group_share_pl3_plus", "share of group at PL3+",
                     n("group_share_pl3_plus"), ">=", 0.30), never],
            4: [Gate("group_share_pl3_plus", "share of group at PL3+",
                     n("group_share_pl3_plus"), ">=", 0.50), never],
        }
    else:
        def diffs(days):
            return Gate("accepted_diff_days", "days with accepted agent diffs",
                        n("accepted_diff_days"), ">=", days)

        outcomes = {
            1: [diffs(1)],
            2: [diffs(4)],
            3: [diffs(8)],
            4: [diffs(8), Gate("automations_active_3of4_weeks",
                               "Automations active in >=3 of 4 weeks",
                               n("automations_active_3of4_weeks"), ">=", 2)],
        }

    return {
        "adoption": adoption,
        "reuse": reuse,
        "orchestration": orchestration,
        "outcomes": outcomes,
    }


def pillar_score(levels):
    """Highest level L with no failed gate at levels 1..L (cumulative; unknowns don't block)."""
    score = 0
    for level in (1, 2, 3, 4):
        if any(g.unmet for g in levels[level]):
            break
        score = level
    return score


def pillar_has_data(levels):
    """True when at least one gate in the pillar has a value to judge."""
    return any(not g.missing for level in (1, 2, 3, 4) for g in levels[level])


def pillar_fully_known(levels, score):
    """True when every gate up to the pillar's score has data behind it."""
    return all(not g.missing
               for level in range(1, score + 1)
               for g in levels[level])


def score_row(raw, self_reported=False):
    row = derive(raw)
    persona = str(row.get("persona") or "").strip().upper()
    if persona not in PERSONAS:
        raise ValueError(
            "persona must be one of %s (got %r) for %s"
            % ("/".join(PERSONAS), row.get("persona"), row.get("email") or "row")
        )

    gates = pillar_gates(row, persona)
    scored = [p for p in PILLARS if pillar_has_data(gates[p])]
    unknown_pillars = [p for p in PILLARS if p not in scored]
    if scored:
        level = min(pillar_score(gates[p]) for p in scored)
        provisional = bool(unknown_pillars) or not all(
            pillar_fully_known(gates[p], pillar_score(gates[p])) for p in scored
        )
    else:
        level = None
        provisional = True

    next_level = level + 1 if level is not None and level < 4 else None
    unmet = []
    if next_level:
        for p in PILLARS:
            for g in gates[p][next_level]:
                if not g.met:
                    unmet.append((g.relative_gap, PILLARS.index(p), g.to_dict(p, next_level)))
    unmet.sort(key=lambda item: (item[0], item[1]))
    unmet_gates = [item[2] for item in unmet]

    missing = set()
    for p in PILLARS:
        for lvl in (1, 2, 3, 4):
            for g in gates[p][lvl]:
                if g.value is None:
                    missing.add(g.field)
                if g.threshold is None:
                    missing.add("chat_requests")
    missing = sorted(missing)

    checks_in = row.get("coach_checks") or {}
    for key in COACH_CHECKS:
        dotted = row.get("coach_checks." + key)
        if dotted not in (None, "") and key not in checks_in:
            checks_in[key] = dotted
    coach_checks = [
        {"check": key, "label": label, "shown_at": "PL%d" % lvl, "value": _bool(checks_in.get(key))}
        for key, (lvl, label) in COACH_CHECKS.items()
        if level is not None and lvl <= (next_level or 4)
    ]

    return {
        "email": row.get("email"),
        "persona": persona,
        "week_ending": row.get("week_ending"),
        "data_source": "self-reported" if self_reported else "usage-data",
        "level": level,
        "level_provisional": provisional,
        "unknown_pillars": unknown_pillars,
        "never_engaged": _num(row, "active_days") == 0,
        "next_level": next_level,
        "smallest_unmet_gate": unmet_gates[0] if unmet_gates else None,
        "unmet_gates_for_next_level": unmet_gates,
        "missing_fields": missing,
        "coach_checks": coach_checks,
    }


def team_summary(results):
    counts = {"PL%d" % lvl: 0 for lvl in range(5)}
    unscored = 0
    never = 0
    provisional = 0
    for result in results:
        if result["level"] is None:
            unscored += 1
        else:
            counts["PL%d" % result["level"]] += 1
            if result["level_provisional"]:
                provisional += 1
        if result["never_engaged"]:
            never += 1
    size = len(results)
    scored = size - unscored

    def share(levels):
        """Shares are over the people we could score, so unscorable rows don't dilute them."""
        return round(sum(counts["PL%d" % lvl] for lvl in levels) / scored, 4) if scored else None

    return {
        "size": size,
        "scored": scored,
        "unscored": unscored,
        "provisional": provisional,
        "level_counts": counts,
        "never_engaged": never,
        "never_engaged_share": round(never / size, 4) if size else None,
        "share_pl1_plus": share((1, 2, 3, 4)),
        "share_pl2_plus": share((2, 3, 4)),
        "share_pl3_plus": share((3, 4)),
    }


def _parse_csv(text):
    rows = []
    for record in csv.DictReader(io.StringIO(text)):
        row = {}
        for key, value in record.items():
            if key is None:
                continue
            key = key.strip()
            value = value.strip() if isinstance(value, str) else value
            if value == "":
                row[key] = None
            elif key in JSON_CELL_FIELDS:
                row[key] = json.loads(value)
            elif key == "is_removed":
                row[key] = _bool(value)
            else:
                row[key] = value
        rows.append(row)
    return rows


def load_rows(path):
    if path == "-":
        text = sys.stdin.read()
    else:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    return _parse_csv(text)


def _level_text(result):
    if result["level"] is None:
        return "not scored (no usage data for any pillar)"
    text = "PL%d" % result["level"]
    if result["level_provisional"]:
        unknown = result["unknown_pillars"]
        reason = ("%s unknown" % ", ".join(p.capitalize() for p in unknown) if unknown
                  else "some inputs unknown")
        text += " (provisional: %s, so treat it as an upper bound)" % reason
    return text


def render_text(result):
    lines = [
        "%s (%s, week ending %s, %s)"
        % (result["email"] or "unknown", result["persona"], result["week_ending"] or "?",
           result["data_source"]),
        "  Level: " + _level_text(result),
    ]
    if result["never_engaged"]:
        lines.append("  Never-engaged: zero active days in the trailing 28 days")
    if result["next_level"]:
        lines.append("  Unmet gates for PL%d (smallest first):" % result["next_level"])
        for g in result["unmet_gates_for_next_level"]:
            have = "missing" if g["missing_data"] else _fmt(g["have"])
            gap = "" if g["gap"] is None else ", gap %s" % _fmt(g["gap"])
            lines.append("    - %s: %s (have %s, need %s%s)"
                         % (g["pillar"].capitalize(), g["gate"], have, g["need"], gap))
    elif result["level"] == 4:
        lines.append("  At PL4: keep meeting every PL4 gate.")
    if result["missing_fields"]:
        lines.append("  Unknown inputs (gate neither met nor failed): "
                     + ", ".join(result["missing_fields"]))
    checks = ["%s=%s" % (c["label"], "unknown" if c["value"] is None else c["value"])
              for c in result["coach_checks"]]
    if checks:
        lines.append("  Coach checks* (never set the level): " + "; ".join(checks))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("input", help="JSON or CSV file, or - for stdin")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--team", action="store_true", help="add a PL0-PL4 team mix summary")
    parser.add_argument("--self-reported", action="store_true",
                        help="label results as self-reported rather than usage data")
    args = parser.parse_args(argv)

    rows = [r for r in load_rows(args.input) if not _bool(r.get("is_removed"))]
    try:
        results = [score_row(r, args.self_reported) for r in rows]
    except ValueError as exc:
        parser.error(str(exc))

    team = team_summary(results) if args.team else None
    if args.json:
        payload = {"results": results}
        if team:
            payload["team"] = team
        print(json.dumps(payload, indent=2))
        return 0

    print("\n\n".join(render_text(r) for r in results))
    if team:
        counts = team["level_counts"]
        print("\nTeam mix (%d scored of %d): %s; never-engaged %d (%.0f%%); PL3+ %.0f%%"
              % (team["scored"], team["size"],
                 ", ".join("%s %d" % (k, v) for k, v in counts.items()),
                 team["never_engaged"], 100 * (team["never_engaged_share"] or 0),
                 100 * (team["share_pl3_plus"] or 0)))
        if team["unscored"] or team["provisional"]:
            print("  %d not scored (no data); %d provisional (a pillar is unknown)"
                  % (team["unscored"], team["provisional"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
