import unittest
from src.models import Clause
from tests.evaluate_citations import verify_clause_support


class TestCitationEvaluation(unittest.TestCase):

    def setUp(self):
        self.clause = Clause(
            id="C021",
            section="Appeals",
            heading="Appeal Deadline",
            text="An applicant may appeal within 30 calendar days of receiving the determination notice.",
            source_start=142,
            source_end=148,
            source_file="data/policy.md",
        )

    def test_verify_clause_support_success(self):
        answer_text = "An applicant may appeal within 30 calendar days of receiving notice. [C021]"
        supported = verify_clause_support(answer_text, self.clause)
        self.assertTrue(supported)

    def test_verify_clause_support_unrelated(self):
        answer_text = "Pet allowance amounts are limited to $500 per month. [C021]"
        supported = verify_clause_support(answer_text, self.clause)
        self.assertFalse(supported)


if __name__ == "__main__":
    unittest.main()
