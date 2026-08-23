import unittest
from pathlib import Path
from main import load_combined_corpus
from src.cli import run_grounded_assistant


class TestTemporalRetrievalIntegration(unittest.TestCase):

    def setUp(self):
        self.policy_path = Path("data/policy.md")
        self.amendment_path = Path("data/Amendment No. 2026-01.md")
        self.clauses = load_combined_corpus(self.policy_path, self.amendment_path)

    def test_pre_march_determination_disregard(self):
        query = "What was the earnings disregard for a determination on 15 February 2026?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("120", output)
        self.assertIn("[C024]", output)

    def test_post_march_determination_disregard(self):
        query = "What was the earnings disregard for a determination on 15 March 2026?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("175", output)
        self.assertIn("[A2026-01-C02]", output)

    def test_pre_march_change_reporting_period(self):
        query = "A change happened on 20 February 2026. How long did the household have to report it?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: REFUSED_CONFLICT", output)
        self.assertIn("C015", output)
        self.assertIn("C038", output)

    def test_post_march_change_reporting_period(self):
        query = "A change happened on 5 March 2026. How long did the household have to report it?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("14", output)
        self.assertIn("[A2026-01-C04]", output)


if __name__ == "__main__":
    unittest.main()
