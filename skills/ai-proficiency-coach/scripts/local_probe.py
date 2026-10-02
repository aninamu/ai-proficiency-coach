#!/usr/bin/env python3
"""Build a partial weekly row from the local Cursor install, for one signed-in user.

This is the ad-hoc fallback when no admin export exists. It reads the local
stores listed in references/data-contract.md section 5, over the same trailing
28-day window, and prints a row that scripts/score.py can read:

  python3 scripts/local_probe.py > my-row.json
  python3 scripts/score.py my-row.json --local-probe

Privacy: every query selects metadata columns only. This script never reads
conversation titles, bodies, summaries (`tldr`, `overview`), commit messages,
prompts, or file contents, and it never opens a transcript. Columns holding
that content are listed in SKIPPED_CONTENT_COLUMNS and are asserted against the
projection so the restriction fails loudly if a query is edited.

What it cannot fill is left null and listed under `_local_probe.not_available`,
so the scorer reports those gates as unmet with the input missing, never as a
real zero. The row covers this machine only: `active_days` is a floor.
"""

import argparse
import json
import os
import platform
import sqlite3
import sys
import time
from datetime import datetime, timedelta

DAY_MS = 86400000
WINDOW_DAYS = 28

# Content columns that exist in the local stores and must never be selected.
SKIPPED_CONTENT_COLUMNS = (
    "title",
    "body",
    "tldr",
    "overview",
    "summaryBullets",
    "commitMessage",
    "content",
)

PRIMARY_BRANCHES = ("main", "master")

# Fields no local store can answer. Each one stays null in the row.
NOT_AVAILABLE = {
    "mcp_days": "No local store records MCP use per day; mcp.json lists configured servers only.",
    "skills_in_2of4_weeks": "cursor.slashUsage.v1 keeps lifetime counters and one last-used stamp, with no per-week history.",
    "skills_in_3of4_weeks": "cursor.slashUsage.v1 keeps lifetime counters and one last-used stamp, with no per-week history.",
    "primary_cloud_commits": "scored_commits has no commitSource column, so cloud commits cannot be separated from local ones.",
    "primary_cloud_commit_weeks": "scored_commits has no commitSource column.",
    "team_rules_hooks_authored": "Local files show personal rules and hooks; team authorship is an audit-log event.",
    "automations_active_3of4_weeks": "Automation runs are not recorded locally.",
    "accepted_diff_days": "Accepted agent diffs per day are not recorded locally.",
}


def default_paths():
    home = os.path.expanduser("~")
    if platform.system() == "Darwin":
        support = os.path.join(home, "Library", "Application Support", "Cursor")
    elif platform.system() == "Windows":
        support = os.path.join(os.environ.get("APPDATA", home), "Cursor")
    else:
        support = os.path.join(home, ".config", "Cursor")
    global_storage = os.path.join(support, "User", "globalStorage")
    return {
        "ai_tracking_db": os.path.join(home, ".cursor", "ai-tracking", "ai-code-tracking.db"),
        "conversation_db": os.path.join(global_storage, "conversation-search.db"),
        "state_db": os.path.join(global_storage, "state.vscdb"),
        "cursor_dir": os.path.join(home, ".cursor"),
    }


def query(path, sql, params=()):
    """Run one read-only query. Returns [] when the store is absent or unreadable."""
    for column in SKIPPED_CONTENT_COLUMNS:
        if column in sql:
            raise AssertionError("query selects content column %r: %s" % (column, sql))
    if not os.path.exists(path):
        return []
    uri = "file:%s?mode=ro" % path.replace("?", "%3f").replace("#", "%23")
    try:
        conn = sqlite3.connect(uri, uri=True, timeout=5)
    except sqlite3.Error:
        return []
    try:
        return conn.execute(sql, params).fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def local_date(ms):
    return time.strftime("%Y-%m-%d", time.localtime(ms / 1000))


class Window:
    """The trailing 28 days ending the day before the run, bucketed into W1-W4."""

    def __init__(self, end=None):
        end = end or (datetime.now() - timedelta(days=1)).date()
        self.end = end
        self.start = end - timedelta(days=WINDOW_DAYS - 1)
        self.start_ms = int(time.mktime(
            datetime(self.start.year, self.start.month, self.start.day).timetuple()) * 1000)
        self.end_ms = self.start_ms + WINDOW_DAYS * DAY_MS

    def contains(self, ms):
        return ms is not None and self.start_ms <= ms < self.end_ms

    def bucket(self, ms):
        """W1 (oldest) .. W4 (most recent), or None outside the window."""
        if not self.contains(ms):
            return None
        return int((ms - self.start_ms) // (7 * DAY_MS)) + 1


def parse_commit_date(text):
    """Parse the `git log` date stored in scored_commits, e.g. 'Thu Oct 1 17:08:00 2026 +0000'."""
    if not text:
        return None
    cleaned = " ".join(str(text).split())
    for fmt in ("%a %b %d %H:%M:%S %Y %z", "%a %b %d %H:%M:%S %Y"):
        try:
            return int(datetime.strptime(cleaned, fmt).timestamp() * 1000)
        except ValueError:
            continue
    return None


def is_primary(branch):
    return str(branch or "").strip().lower() in PRIMARY_BRANCHES


def probe_adoption(paths, window):
    """active_days from AI-code events and conversation activity; mode mix as a request proxy."""
    code_days = {
        local_date(row[0])
        for row in query(paths["ai_tracking_db"],
                         "select createdAt from ai_code_hashes where createdAt >= ? and createdAt < ?",
                         (window.start_ms, window.end_ms))
    }
    chat_days = {
        local_date(row[0])
        for row in query(paths["conversation_db"],
                         "select updated_at from conversations where updated_at >= ? and updated_at < ?",
                         (window.start_ms, window.end_ms))
    }
    modes = {}
    for mode, in query(paths["ai_tracking_db"],
                       "select mode from conversation_summaries where updatedAt >= ? and updatedAt < ?",
                       (window.start_ms, window.end_ms)):
        key = (mode or "unknown").strip().lower()
        modes[key] = modes.get(key, 0) + 1

    agentish = sum(count for key, count in modes.items() if key in ("agent", "plan"))
    askish = sum(count for key, count in modes.items() if key in ("ask", "chat", "edit"))
    return {
        "active_days": len(code_days | chat_days),
        "agent_requests": agentish,
        "chat_requests": askish,
        "_mode_counts": modes,
        "_active_days_from_code": len(code_days),
        "_active_days_from_chats": len(chat_days),
    }


def probe_reuse(paths, window):
    """Skill invocations from cursor.slashUsage.v1, and Plan mode from plan files plus modes."""
    skills_seen = []
    rows = query(paths["state_db"], "select value from ItemTable where key = ?",
                 ("cursor.slashUsage.v1",))
    if rows:
        try:
            entries = (json.loads(rows[0][0]) or {}).get("entries") or {}
        except (ValueError, TypeError):
            entries = {}
        for key, entry in entries.items():
            try:
                kind, scope, _, name = json.loads(key.split("slash:v1:", 1)[1])
            except (ValueError, IndexError):
                continue
            if kind != "skill":
                continue
            last = (entry.get("lastAt") or {}).get("selectedAtMs")
            skills_seen.append({
                "skill_name": name,
                "scope": scope,
                "lifetime_uses": (entry.get("counters") or {}).get("selected", 0),
                "last_used": local_date(last) if last else None,
                "used_in_window": bool(window.contains(last)),
            })
    skills_seen.sort(key=lambda s: (not s["used_in_window"], s["skill_name"]))

    plan_dir = os.path.join(paths["cursor_dir"], "plans")
    plan_files = 0
    if os.path.isdir(plan_dir):
        for name in os.listdir(plan_dir):
            full = os.path.join(plan_dir, name)
            if os.path.isfile(full) and window.contains(int(os.path.getmtime(full) * 1000)):
                plan_files += 1
    plan_conversations = len(query(
        paths["ai_tracking_db"],
        "select 1 from conversation_summaries where mode = 'plan' and updatedAt >= ? and updatedAt < ?",
        (window.start_ms, window.end_ms)))

    return {
        "plan_mode_uses": max(plan_files, plan_conversations),
        "_plan_files": plan_files,
        "_plan_conversations": plan_conversations,
        "_skills_seen": skills_seen,
        "_skills_used_in_window": sum(1 for s in skills_seen if s["used_in_window"]),
    }


def probe_orchestration(paths, window):
    """Cloud Agent runs from the local agent list; MCP servers configured, which is not usage."""
    runs, days, weeks = set(), set(), set()
    for key, value in query(paths["state_db"],
                            "select key, value from ItemTable where key like ?",
                            ("cloudAgentRepository.agents.%",)):
        try:
            agents = json.loads(value)
        except (ValueError, TypeError):
            continue
        if not isinstance(agents, list):
            continue
        for agent in agents:
            created = agent.get("createdAt")
            if not window.contains(created):
                continue
            runs.add(agent.get("bcId") or created)
            days.add(local_date(created))
            weeks.add(window.bucket(created))

    mcp_path = os.path.join(paths["cursor_dir"], "mcp.json")
    configured = []
    if os.path.exists(mcp_path):
        try:
            with open(mcp_path, encoding="utf-8") as fh:
                configured = sorted((json.load(fh).get("mcpServers") or {}).keys())
        except (ValueError, OSError):
            configured = []

    return {
        "cloud_agent_runs": len(runs),
        "_cloud_agent_days": len(days),
        "_cloud_agent_weeks": len(weeks),
        "_mcp_servers_configured": configured,
    }


def probe_ic_outcomes(paths, window):
    """IC commit outcomes from scored_commits. AI lines = tab + composer lines added."""
    rows = query(paths["ai_tracking_db"],
                 "select branchName, commitDate, tabLinesAdded, composerLinesAdded "
                 "from scored_commits")
    commits_with_ai = 0
    primary = 0
    primary_with_ai = 0
    for branch, date_text, tab_added, composer_added in rows:
        when = parse_commit_date(date_text)
        if not window.contains(when):
            continue
        ai_lines = (tab_added or 0) + (composer_added or 0)
        if ai_lines > 0:
            commits_with_ai += 1
        if is_primary(branch):
            primary += 1
            if ai_lines > 0:
                primary_with_ai += 1
    return {
        "commits_with_ai_lines": commits_with_ai,
        "primary_commits": primary,
        "primary_commits_with_ai_lines": primary_with_ai,
        "_scored_commits_total": len(rows),
    }


def build_row(persona, paths=None, window=None, email=None):
    paths = paths or default_paths()
    window = window or Window()

    adoption = probe_adoption(paths, window)
    reuse = probe_reuse(paths, window)
    orchestration = probe_orchestration(paths, window)
    outcomes = probe_ic_outcomes(paths, window) if persona == "IC" else {}

    row = {
        "week_ending": window.end.isoformat(),
        "window_start": window.start.isoformat(),
        "window_end": window.end.isoformat(),
        "email": email,
        "persona": persona,
        "is_removed": False,
        "data_source": "local-probe",
    }
    for part in (adoption, reuse, orchestration, outcomes):
        row.update({k: v for k, v in part.items() if not k.startswith("_")})
    for field in NOT_AVAILABLE:
        row.setdefault(field, None)

    notes = {
        "active_days": "Floor, not a count: this machine only, from %d AI-code days and %d conversation days."
                       % (adoption["_active_days_from_code"], adoption["_active_days_from_chats"]),
        "agent_requests": "Proxy: agent and plan mode conversations, not request counts.",
        "chat_requests": "Proxy: ask, chat, and edit mode conversations, not request counts.",
        "plan_mode_uses": "Proxy: max of %d plan files written and %d plan-mode conversations."
                          % (reuse["_plan_files"], reuse["_plan_conversations"]),
        "cloud_agent_runs": "Measured: %d distinct agents on %d days, spanning %d of 4 weeks."
                            % (orchestration["cloud_agent_runs"], orchestration["_cloud_agent_days"],
                               orchestration["_cloud_agent_weeks"]),
    }
    if persona == "IC":
        notes["primary_commits"] = ("Measured from %d locally scored commits; only repos opened on "
                                    "this machine are scored." % outcomes["_scored_commits_total"])

    row["_local_probe"] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "machine": "single install; other machines, web, and CLI sessions are not included",
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat(), "days": WINDOW_DAYS},
        "field_notes": notes,
        "not_available": NOT_AVAILABLE,
        "mode_counts": adoption["_mode_counts"],
        "mcp_servers_configured": orchestration["_mcp_servers_configured"],
        "skills_seen": reuse["_skills_seen"],
        "skills_used_in_window": reuse["_skills_used_in_window"],
    }
    return row


def render_text(row):
    probe = row["_local_probe"]
    lines = [
        "Local probe for %s to %s (persona %s)"
        % (probe["window"]["start"], probe["window"]["end"], row["persona"]),
        "  Measured:",
        "    active_days          %s   (%s)" % (row["active_days"], probe["field_notes"]["active_days"]),
        "    cloud_agent_runs     %s   (%s)" % (row["cloud_agent_runs"],
                                                probe["field_notes"]["cloud_agent_runs"]),
        "    plan_mode_uses       %s   (%s)" % (row["plan_mode_uses"],
                                                probe["field_notes"]["plan_mode_uses"]),
        "    agent/chat requests  %s / %s   (proxy: conversations by mode)"
        % (row["agent_requests"], row["chat_requests"]),
    ]
    if row["persona"] == "IC":
        lines.append("    commits with AI      %s of %s primary-branch commits"
                     % (row["primary_commits_with_ai_lines"], row["primary_commits"]))
    lines.append("  Skills invoked in window: %d (%d ever)"
                 % (probe["skills_used_in_window"], len(probe["skills_seen"])))
    lines.append("  Not available locally, left null:")
    for field, why in sorted(probe["not_available"].items()):
        lines.append("    - %s: %s" % (field, why))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--persona", choices=("IC", "LEADER", "PM"), default="IC",
                        help="persona for the row (default IC)")
    parser.add_argument("--email", help="label the row with an email; not read from the install")
    parser.add_argument("--week-ending", help="window end date YYYY-MM-DD (default: yesterday)")
    parser.add_argument("--text", action="store_true",
                        help="print a readable summary instead of the JSON row")
    args = parser.parse_args(argv)

    end = None
    if args.week_ending:
        end = datetime.strptime(args.week_ending, "%Y-%m-%d").date()

    paths = default_paths()
    row = build_row(args.persona, paths, Window(end), args.email)

    if not os.path.exists(paths["state_db"]):
        sys.stderr.write("warning: %s not found; cloud agent and skill fields will be empty\n"
                         % paths["state_db"])

    print(render_text(row) if args.text else json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
