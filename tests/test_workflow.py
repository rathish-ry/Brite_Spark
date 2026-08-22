import unittest
from src.models import Clause
from src.cli import run_grounded_assistant


class TestCLIWorkflow(unittest.TestCase):

    def setUp(self):
        self.clause_appeal = Clause(
            id="C053",
            section="12.1 Right of appeal",
            heading="12.1 Right of appeal",
            text="An applicant may file a written appeal within 30 days of receiving notice.",
            source_start=584,
            source_end=588,
            source_file="data/policy.md",
        )
        self.clauses = [self.clause_appeal]

    def test_workflow_answerable_case(self):
        query = "How long do I have to file an appeal?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("GROUNDED POLICY ASSISTANT", output)
        self.assertIn("Question:\n> How long do I have to file an appeal?", output)
        self.assertIn("ANSWER", output)
        self.assertIn("[C053]", output)
        self.assertIn("SOURCES", output)
        self.assertIn("Source: data/policy.md lines 584-588", output)
        self.assertIn("STATUS: ANSWERED", output)

    def test_workflow_apparent_gap_refusal_case(self):
        query = "Can a representative submit an appeal for a resident?"
        output = run_grounded_assistant(query, self.clauses)

        self.assertIn("GROUNDED POLICY ASSISTANT", output)
        self.assertIn("REFUSAL", output)
        self.assertIn("The manual does not settle this question with sufficient confidence.", output)
        self.assertIn("does not contain provisions or rules regarding 'representative'", output)
        self.assertIn("STATUS: REFUSE", output)


if __name__ == "__main__":
    unittest.main()
