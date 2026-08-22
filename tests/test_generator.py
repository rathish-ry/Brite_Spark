import unittest
from src.models import Clause
from src.generator import GroundedGenerator


class TestGroundedGenerator(unittest.TestCase):

    def setUp(self):
        self.clause = Clause(
            id="C053",
            section="12.1 Right of appeal",
            heading="12.1 Right of appeal",
            text="An appeal must be lodged within 30 days of receiving the determination notice.",
            source_start=584,
            source_end=588,
            source_file="data/policy.md",
        )
        self.generator = GroundedGenerator()

    def test_generate_grounded_answer(self):
        query = "How long do I have to appeal?"
        answer = self.generator.generate(query, [self.clause])

        self.assertEqual(answer.status, "ANSWERED")
        self.assertIn("[C053]", answer.answer_text)
        self.assertIn("An appeal must be lodged within 30 days", answer.answer_text)
        self.assertIn("C053", answer.cited_clause_ids)
        self.assertIn("Source: data/policy.md lines 584-588", answer.sources_text)

    def test_generate_empty_clauses_refusal(self):
        query = "Unknown question"
        answer = self.generator.generate(query, [])

        self.assertEqual(answer.status, "REFUSED")
        self.assertEqual(len(answer.cited_clause_ids), 0)


if __name__ == "__main__":
    unittest.main()
