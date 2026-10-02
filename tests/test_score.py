import datetime
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "ai-proficiency-coach")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import local_probe  # noqa: E402
import score  # noqa: E402


def load_example():
    with open(os.path.join(SKILL, "examples", "fake-ic-row.json"), encoding="utf-8") as fh:
        return json.load(fh)


def blank_row(persona="IC", **fields):
    row = {
        "email": "fake.person@example.com",
        "persona": persona,
        "active_days": 0,
        "agent_requests": 0,
        "chat_requests": 0,
        "skills_in_2of4_weeks": 0,
        "skills_in_3of4_weeks": 0,
        "plan_mode_uses": 0,
        "team_rules_hooks_authored": 0,
        "cloud_agent_runs": 0,
        "mcp_days": 0,
        "automations_active_3of4_weeks": 0,
        "commits_with_ai_lines": 0,
        "primary_commits": 0,
        "primary_cloud_commits": 0,
        "primary_cloud_commit_weeks": 0,
        "accepted_diff_days": 0,
    }
    row.update(fields)
    return row


class DataContractExample(unittest.TestCase):
    def test_reproduces_worked_example(self):
        result = score.score_row(load_example())
        self.assertEqual(
            result["pillar_scores"],
            {"adoption": 3, "reuse": 2, "orchestration": 3, "outcomes": 2},
        )
        self.assertEqual(result["gated_level"], 2)
        self.assertEqual(result["displayed_level"], 2)
        self.assertEqual(result["composite"], 2.50)
        gaps = {(g["field"], g["gap"]) for g in result["unmet_gates_for_next_level"]}
        self.assertEqual(gaps, {("skills_in_3of4_weeks", 1), ("primary_cloud_commits", 1)})
        self.assertEqual(result["missing_fields"], [])

    def test_derived_fields_match_raw_arrays(self):
        row = load_example()
        for key in ("skills_in_2of4_weeks", "skills_in_3of4_weeks", "primary_ai_commit_share"):
            row[key] = None
        derived = score.derive(row)
        self.assertEqual(derived["skills_in_2of4_weeks"], 3)
        self.assertEqual(derived["skills_in_3of4_weeks"], 2)
        self.assertAlmostEqual(derived["primary_ai_commit_share"], 0.55)


class Gates(unittest.TestCase):
    def test_not_required_counts_as_met(self):
        result = score.score_row(blank_row())
        self.assertEqual(result["pillar_scores"]["reuse"], 1)
        self.assertEqual(result["pillar_scores"]["orchestration"], 2)
        self.assertEqual(result["gated_level"], 0)
        self.assertTrue(result["never_engaged"])

    def test_agent_must_match_chat_from_pl2(self):
        row = blank_row(active_days=20, agent_requests=10, chat_requests=11)
        self.assertEqual(score.score_row(row)["pillar_scores"]["adoption"], 1)

    def test_pm_pl4_needs_two_automations(self):
        row = blank_row("PM", accepted_diff_days=10, automations_active_3of4_weeks=1)
        self.assertEqual(score.score_row(row)["pillar_scores"]["outcomes"], 3)
        row["automations_active_3of4_weeks"] = 2
        self.assertEqual(score.score_row(row)["pillar_scores"]["outcomes"], 4)

    def test_leader_shares_derived_from_counts(self):
        row = blank_row(
            "LEADER",
            group_size=10,
            group_level_counts={"PL0": 0, "PL1": 2, "PL2": 3, "PL3": 4, "PL4": 1},
            group_never_engaged_share=0.0,
        )
        self.assertEqual(score.score_row(row)["pillar_scores"]["outcomes"], 4)
        row["group_never_engaged_share"] = 0.2
        self.assertEqual(score.score_row(row)["pillar_scores"]["outcomes"], 2)

    def test_missing_field_fails_gate_and_is_reported(self):
        row = blank_row(active_days=None)
        result = score.score_row(row)
        self.assertEqual(result["pillar_scores"]["adoption"], 0)
        self.assertIn("active_days", result["missing_fields"])

    def test_author_log_feeds_reuse_pl4(self):
        row = load_example()
        row.update(skills_in_3of4_weeks=3, team_rules_hooks_authored=None, author_log=[
            {"type": "team_hook", "name": "fake-hook", "saved_by_admin": True,
             "real_author_email": "fake.developer@example.com", "date": "2026-09-20"},
        ])
        self.assertEqual(score.score_row(row)["pillar_scores"]["reuse"], 4)


class WeeklyLevelRule(unittest.TestCase):
    def history(self, gated, displayed):
        return [{"week_ending": "2026-09-%02d" % (i + 1), "gated_level": g, "displayed_level": d}
                for i, (g, d) in enumerate(zip(gated, displayed))]

    def test_up_needs_two_straight_weeks(self):
        self.assertEqual(score.displayed_level(3, self.history([2, 2], [2, 2]))[0], 2)
        self.assertEqual(score.displayed_level(3, self.history([2, 3], [2, 2]))[0], 3)

    def test_down_needs_four_straight_weeks(self):
        self.assertEqual(score.displayed_level(1, self.history([3, 2, 2], [3, 3, 3]))[0], 3)
        self.assertEqual(score.displayed_level(1, self.history([2, 2, 2], [3, 3, 3]))[0], 2)


class MissingDataIsAFloor(unittest.TestCase):
    def test_complete_row_is_not_a_floor(self):
        self.assertFalse(score.score_row(load_example())["level_is_floor"])

    def test_missing_input_marks_the_level_as_a_floor(self):
        result = score.score_row(blank_row(skills_in_3of4_weeks=None))
        self.assertTrue(result["level_is_floor"])
        self.assertIn("skills_in_3of4_weeks", result["missing_fields"])

    def test_data_source_comes_from_flag_then_row(self):
        self.assertEqual(score.score_row(blank_row())["data_source"], "usage-data")
        self.assertEqual(
            score.score_row(blank_row(data_source="local-probe"))["data_source"], "local-probe")
        self.assertEqual(
            score.score_row(blank_row(data_source="local-probe"), "self-reported")["data_source"],
            "self-reported")


class LocalProbe(unittest.TestCase):
    def test_window_buckets_oldest_to_newest(self):
        window = local_probe.Window(datetime.date(2026, 9, 27))
        self.assertEqual(window.start, datetime.date(2026, 8, 31))
        self.assertEqual(window.bucket(window.start_ms), 1)
        self.assertEqual(window.bucket(window.end_ms - 1), 4)
        self.assertIsNone(window.bucket(window.start_ms - 1))
        self.assertIsNone(window.bucket(window.end_ms))

    def test_parses_the_git_log_date_scored_commits_stores(self):
        window = local_probe.Window(datetime.date(2026, 10, 1))
        padded = local_probe.parse_commit_date("Fri Sep 18 13:17:51 2026 -0400")
        unpadded = local_probe.parse_commit_date("Thu Oct 1 17:08:00 2026 +0000")
        self.assertTrue(window.contains(padded))
        self.assertTrue(window.contains(unpadded))
        self.assertIsNone(local_probe.parse_commit_date("not a date"))
        self.assertIsNone(local_probe.parse_commit_date(None))

    def test_primary_branch_detection(self):
        self.assertTrue(local_probe.is_primary("main"))
        self.assertTrue(local_probe.is_primary(" Master "))
        self.assertFalse(local_probe.is_primary("demo/dashboard-lookup-api"))
        self.assertFalse(local_probe.is_primary(None))

    def test_queries_refuse_to_select_content_columns(self):
        with self.assertRaises(AssertionError):
            local_probe.query("/nonexistent.db", "select commitMessage from scored_commits")

    def test_missing_stores_yield_a_row_of_nulls_not_zeros(self):
        paths = {key: "/nonexistent/%s" % key for key in
                 ("ai_tracking_db", "conversation_db", "state_db", "cursor_dir")}
        row = local_probe.build_row("IC", paths, local_probe.Window(datetime.date(2026, 10, 1)))
        self.assertEqual(row["data_source"], "local-probe")
        for field in local_probe.NOT_AVAILABLE:
            self.assertIsNone(row[field], field)
        # Fields the probe owns are real counts from empty stores, so zero is correct.
        self.assertEqual(row["cloud_agent_runs"], 0)
        result = score.score_row(row)
        self.assertTrue(result["level_is_floor"])

    def test_not_available_follows_persona_outcomes(self):
        paths = {key: "/nonexistent/%s" % key for key in
                 ("ai_tracking_db", "conversation_db", "state_db", "cursor_dir")}
        window = local_probe.Window(datetime.date(2026, 10, 1))

        ic = local_probe.build_row("IC", paths, window)["_local_probe"]["not_available"]
        self.assertIn("primary_cloud_commits", ic)
        self.assertNotIn("group_share_pl1_plus", ic)

        leader = local_probe.build_row("LEADER", paths, window)
        missing = leader["_local_probe"]["not_available"]
        for field in ("group_share_pl1_plus", "group_share_pl2_plus",
                      "group_share_pl3_plus", "group_never_engaged_share"):
            self.assertIn(field, missing)
            self.assertIsNone(leader[field])
        self.assertNotIn("primary_cloud_commits", missing)
        self.assertNotIn("primary_cloud_commit_weeks", missing)
        result = score.score_row(leader)
        self.assertIn("group_share_pl1_plus", result["missing_fields"])
        self.assertIn("group_never_engaged_share", result["missing_fields"])
        self.assertNotIn("primary_cloud_commits", result["missing_fields"])

        pm = local_probe.build_row("PM", paths, window)["_local_probe"]["not_available"]
        self.assertIn("accepted_diff_days", pm)
        self.assertNotIn("primary_cloud_commits", pm)
        self.assertNotIn("group_never_engaged_share", pm)

    def test_probe_row_leaves_week_based_skill_gates_unknown(self):
        paths = {key: "/nonexistent/%s" % key for key in
                 ("ai_tracking_db", "conversation_db", "state_db", "cursor_dir")}
        row = local_probe.build_row("IC", paths, local_probe.Window(datetime.date(2026, 10, 1)))
        # A `skills` array would let derive() turn "unknown" into a hard zero.
        self.assertNotIn("skills", row)
        self.assertIsNone(score.derive(row)["skills_in_3of4_weeks"])


class CsvInput(unittest.TestCase):
    def test_team_csv(self):
        rows = score.load_rows(os.path.join(SKILL, "examples", "fake-team.csv"))
        results = [score.score_row(r) for r in rows]
        by_email = {r["email"]: r for r in results}
        dev = by_email["fake.developer@example.com"]
        self.assertEqual((dev["gated_level"], dev["composite"]), (2, 2.50))
        team = score.team_summary(results)
        self.assertEqual(team["level_counts"], {"PL0": 1, "PL1": 1, "PL2": 2, "PL3": 0, "PL4": 0})
        self.assertEqual(team["never_engaged"], 1)


if __name__ == "__main__":
    unittest.main()
