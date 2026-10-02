import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "ai-proficiency-coach")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import score  # noqa: E402


def load_example():
    with open(os.path.join(SKILL, "examples", "fake-ic-row.json"), encoding="utf-8") as fh:
        return json.load(fh)


def pillars(row):
    """Pillar scores are an internal detail of the level, so compute them directly."""
    derived = score.derive(row)
    gates = score.pillar_gates(derived, derived["persona"])
    return {p: score.pillar_score(gates[p]) for p in score.PILLARS}


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
        row = load_example()
        self.assertEqual(
            pillars(row),
            {"adoption": 3, "reuse": 2, "orchestration": 3, "outcomes": 2},
        )
        result = score.score_row(row)
        self.assertEqual(result["level"], 2)
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
        row = blank_row()
        self.assertEqual(pillars(row)["reuse"], 1)
        self.assertEqual(pillars(row)["orchestration"], 2)
        result = score.score_row(row)
        self.assertEqual(result["level"], 0)
        self.assertTrue(result["never_engaged"])

    def test_agent_must_match_chat_from_pl2(self):
        row = blank_row(active_days=20, agent_requests=10, chat_requests=11)
        self.assertEqual(pillars(row)["adoption"], 1)

    def test_pm_pl4_needs_two_automations(self):
        row = blank_row("PM", accepted_diff_days=10, automations_active_3of4_weeks=1)
        self.assertEqual(pillars(row)["outcomes"], 3)
        row["automations_active_3of4_weeks"] = 2
        self.assertEqual(pillars(row)["outcomes"], 4)

    def test_leader_shares_derived_from_counts(self):
        row = blank_row(
            "LEADER",
            group_size=10,
            group_level_counts={"PL0": 0, "PL1": 2, "PL2": 3, "PL3": 4, "PL4": 1},
            group_never_engaged_share=0.0,
        )
        self.assertEqual(pillars(row)["outcomes"], 4)
        row["group_never_engaged_share"] = 0.2
        self.assertEqual(pillars(row)["outcomes"], 2)

    def test_missing_field_is_unknown_not_failed(self):
        row = blank_row(active_days=None)
        result = score.score_row(row)
        self.assertIn("active_days", result["missing_fields"])
        self.assertTrue(result["level_provisional"])
        # chat_requests is the PL2+ threshold, so adoption is only judged on what is known.
        self.assertEqual(pillars(row)["adoption"], 4)

    def test_unknown_pillar_does_not_cap_the_level(self):
        row = load_example()
        row.update(skills_in_3of4_weeks=3, team_rules_hooks_authored=1,
                   automations_active_3of4_weeks=1, active_days=16)
        for key in ("commits_with_ai_lines", "primary_commits", "primary_ai_commit_share",
                    "primary_commits_with_ai_lines", "primary_cloud_commits",
                    "primary_cloud_commit_weeks"):
            row[key] = None
        result = score.score_row(row)
        self.assertEqual(result["level"], 4)
        self.assertEqual(result["unknown_pillars"], ["outcomes"])
        self.assertTrue(result["level_provisional"])
        self.assertIsNone(result["next_level"])
        self.assertIn("At PL4", score.render_text(result))
        self.assertTrue(any(c["shown_at"] == "PL4" for c in result["coach_checks"]))

    def test_known_zero_still_fails_its_gate(self):
        row = load_example()
        row.update(commits_with_ai_lines=0, primary_commits=0,
                   primary_commits_with_ai_lines=0, primary_ai_commit_share=0,
                   primary_cloud_commits=0, primary_cloud_commit_weeks=0)
        result = score.score_row(row)
        self.assertEqual(result["level"], 0)
        self.assertEqual(result["unknown_pillars"], [])
        self.assertFalse(result["level_provisional"])

    def test_row_with_no_data_is_not_scored(self):
        row = {"email": "empty@example.com", "persona": "IC"}
        result = score.score_row(row)
        self.assertIsNone(result["level"])
        self.assertTrue(result["level_provisional"])
        self.assertEqual(len(result["unknown_pillars"]), 4)
        self.assertIsNone(result["next_level"])
        self.assertEqual(result["coach_checks"], [])
        text = score.render_text(result)
        self.assertIn("not scored", text)
        self.assertNotIn("At PL4", text)

    def test_author_log_feeds_reuse_pl4(self):
        row = load_example()
        row.update(skills_in_3of4_weeks=3, team_rules_hooks_authored=None, author_log=[
            {"type": "team_hook", "name": "fake-hook", "saved_by_admin": True,
             "real_author_email": "fake.developer@example.com", "date": "2026-09-20"},
        ])
        self.assertEqual(pillars(row)["reuse"], 4)


class CsvInput(unittest.TestCase):
    def test_team_csv(self):
        rows = score.load_rows(os.path.join(SKILL, "examples", "fake-team.csv"))
        results = [score.score_row(r) for r in rows]
        by_email = {r["email"]: r for r in results}
        dev = by_email["fake.developer@example.com"]
        self.assertEqual(dev["level"], 2)
        team = score.team_summary(results)
        self.assertEqual(team["level_counts"], {"PL0": 1, "PL1": 1, "PL2": 2, "PL3": 0, "PL4": 0})
        self.assertEqual(team["never_engaged"], 1)


if __name__ == "__main__":
    unittest.main()
