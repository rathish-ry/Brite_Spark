import io
import sys
import unittest
from src.models import Clause
from src.cli import list_clauses, show_clause


class TestCLIInspection(unittest.TestCase):

    def setUp(self):
        self.sample_clauses = [
            Clause(
                id="C001",
                section="Eligibility Requirements",
                heading="Income Requirements",
                text="Income must not exceed 50% AMI.",
                source_start=10,
                source_end=15,
                source_file="data/policy.md",
            ),
            Clause(
                id="C002",
                section="Appeals and Hearings",
                heading="Appeal Deadline",
                text="Appeals must be filed within 30 days.",
                source_start=40,
                source_end=46,
                source_file="data/policy.md",
            ),
        ]

    def test_list_clauses_output(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            list_clauses(self.sample_clauses)
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("[C001] Eligibility Requirements — Income Requirements", output)
        self.assertIn("[C002] Appeals and Hearings — Appeal Deadline", output)

    def test_show_clause_valid_id(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            found = show_clause(self.sample_clauses, "C002")
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertTrue(found)
        self.assertIn("[C002]", output)
        self.assertIn("Section: Appeals and Hearings", output)
        self.assertIn("Heading: Appeal Deadline", output)
        self.assertIn("Source: data/policy.md lines 40-46", output)
        self.assertIn("Appeals must be filed within 30 days.", output)

    def test_show_clause_case_insensitive(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            found = show_clause(self.sample_clauses, "c001")
        finally:
            sys.stdout = sys.__stdout__

        self.assertTrue(found)
        self.assertIn("[C001]", captured_output.getvalue())

    def test_show_clause_invalid_id(self):
        captured_stderr = io.StringIO()
        sys.stderr = captured_stderr
        try:
            found = show_clause(self.sample_clauses, "C999")
        finally:
            sys.stderr = sys.__stderr__

        self.assertFalse(found)
        self.assertIn("ERROR: Clause 'C999' not found.", captured_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
