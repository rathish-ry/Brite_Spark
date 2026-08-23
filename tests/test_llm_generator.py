import unittest
from pathlib import Path
from main import load_combined_corpus
from src.cli import run_grounded_assistant
from src.llm_generator import GroqGroundedGenerator, LLMAnswerResult
from src.temporal import extract_temporal_context


class TestGroqGroundedGenerator(unittest.TestCase):

    def setUp(self):
        self.policy_path = Path("data/policy.md")
        self.amendment_path = Path("data/Amendment No. 2026-01.md")
        self.clauses = load_combined_corpus(self.policy_path, self.amendment_path)
        self.generator = GroqGroundedGenerator()

    def test_march_2026_disregard_answer(self):
        query = "What was the earnings disregard for a determination on 15 March 2026?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("175", output)
        self.assertIn("[A2026-01-C02]", output)

    def test_february_2026_disregard_answer(self):
        query = "What was the earnings disregard for a determination on 15 February 2026?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("120", output)
        self.assertNotIn("175", output.split("SOURCES")[0])

    def test_pre_march_change_reporting_period(self):
        query = "A change of circumstances occurred on 20 February 2026. How long did the household have to report it?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("10", output)

    def test_post_march_change_reporting_period(self):
        query = "A change of circumstances occurred on 5 March 2026. How long did the household have to report it?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("STATUS: ANSWERED", output)
        self.assertIn("14", output)

    def test_refusal_when_unanswerable(self):
        query = "What is the exact dollar amount of the maximum grant for pet care allowance?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertTrue("STATUS: REFUSE" in output or "STATUS: REFUSED" in output)

    def test_structured_llm_result_model(self):
        res = LLMAnswerResult(
            status="answered",
            answer="The earnings disregard was $175 per month.",
            reason="Determination on or after 1 March 2026.",
            citation_ids=["A2026-01-C02", "A2026-01-C08"],
        )
        self.assertEqual(res.status, "answered")
        self.assertEqual(len(res.citation_ids), 2)


if __name__ == "__main__":
    unittest.main()
