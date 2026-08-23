import unittest
from pathlib import Path
from main import load_combined_corpus
from src.cli import run_grounded_assistant


class TestAmendmentCitations(unittest.TestCase):

    def setUp(self):
        self.policy_path = Path("data/policy.md")
        self.amendment_path = Path("data/Amendment No. 2026-01.md")
        self.clauses = load_combined_corpus(self.policy_path, self.amendment_path)

    def test_dual_citation_for_determination_amendment(self):
        # Disregard determination on 15 March 2026 -> Cites both amendment rule and transitional paragraph 5.1
        query = "What was the earnings disregard for a determination on 15 March 2026?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("[A2026-01-C02]", output)  # Paragraph 1.1 ($175)
        self.assertIn("[A2026-01-C08]", output)  # Paragraph 5.1 (Transitional provision)

    def test_dual_citation_for_change_reporting_amendment(self):
        # Change reporting on 5 March 2026 -> Cites both amendment rule and transitional paragraph 5.2
        query = "A change happened on 5 March 2026. How long did the household have to report it?"
        output = run_grounded_assistant(query, self.clauses)
        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("[A2026-01-C04]", output)  # Paragraph 2.2 (14 calendar days)
        self.assertIn("[A2026-01-C09]", output)  # Paragraph 5.2 (Transitional provision)


if __name__ == "__main__":
    unittest.main()
