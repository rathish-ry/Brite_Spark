import unittest
from src.models import Clause
from src.citations import (
    extract_citation_tags,
    validate_citations,
    format_sources_block,
)


class TestCitations(unittest.TestCase):

    def setUp(self):
        self.clause1 = Clause(
            id="C021",
            section="Appeals",
            heading="Appeal Deadline",
            text="An applicant may appeal within 30 calendar days of receiving the decision.",
            source_start=142,
            source_end=148,
            source_file="data/policy.md",
        )
        self.clause2 = Clause(
            id="C005",
            section="Eligibility",
            heading="Income Limit",
            text="Gross income must not exceed 50% AMI.",
            source_start=42,
            source_end=48,
            source_file="data/policy.md",
        )

    def test_extract_citation_tags(self):
        text = "An applicant may appeal within 30 days. [C021] Additional rules apply. [c005]"
        tags = extract_citation_tags(text)
        self.assertEqual(tags, ["C021", "C005"])

    def test_validate_citations_success(self):
        answer_text = "An applicant may appeal within 30 calendar days of receiving the decision. [C021]"
        res = validate_citations(answer_text, [self.clause1])
        self.assertTrue(res.is_valid)
        self.assertEqual(res.cited_ids, ["C021"])

    def test_validate_citations_uncited_claim_failure(self):
        # Sentence without citation tag
        answer_text = "According to the policy manual, you have 30 days to appeal."
        res = validate_citations(answer_text, [self.clause1])
        self.assertFalse(res.is_valid)
        self.assertIn("without clause citations", res.error_message)

    def test_validate_citations_unapproved_id_failure(self):
        answer_text = "An applicant may appeal within 30 calendar days. [C999]"
        res = validate_citations(answer_text, [self.clause1])
        self.assertFalse(res.is_valid)
        self.assertIn("unapproved or non-existent", res.error_message)

    def test_format_sources_block(self):
        formatted = format_sources_block([self.clause1])
        self.assertIn("[C021] Appeals — Appeal Deadline", formatted)
        self.assertIn("Source: data/policy.md lines 142-148", formatted)
        self.assertIn("\"An applicant may appeal within 30 calendar days of receiving the decision.\"", formatted)


if __name__ == "__main__":
    unittest.main()
