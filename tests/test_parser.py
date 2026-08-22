import unittest
from src.parser import parse_markdown_policy


class TestMarkdownParser(unittest.TestCase):

    def test_normal_heading_and_multiple_clauses(self):
        doc = (
            "# Document Title\n"
            "\n"
            "## Section 1: General\n"
            "\n"
            "### 1.1 Overview\n"
            "This is the first overview clause.\n"
            "\n"
            "### 1.2 Purpose\n"
            "This is the purpose clause.\n"
        )
        clauses = parse_markdown_policy(doc, source_file="test.md")
        self.assertEqual(len(clauses), 2)

        self.assertEqual(clauses[0].id, "C001")
        self.assertEqual(clauses[0].section, "Section 1: General")
        self.assertEqual(clauses[0].heading, "1.1 Overview")
        self.assertEqual(clauses[0].text, "This is the first overview clause.")
        self.assertEqual(clauses[0].source_start, 6)
        self.assertEqual(clauses[0].source_end, 6)

        self.assertEqual(clauses[1].id, "C002")
        self.assertEqual(clauses[1].section, "Section 1: General")
        self.assertEqual(clauses[1].heading, "1.2 Purpose")
        self.assertEqual(clauses[1].text, "This is the purpose clause.")
        self.assertEqual(clauses[1].source_start, 9)
        self.assertEqual(clauses[1].source_end, 9)

    def test_empty_section(self):
        doc = (
            "## Empty Section\n"
            "\n"
            "## Section With Content\n"
            "### Subheading\n"
            "Content goes here.\n"
        )
        clauses = parse_markdown_policy(doc, source_file="test.md")
        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0].id, "C001")
        self.assertEqual(clauses[0].section, "Section With Content")
        self.assertEqual(clauses[0].heading, "Subheading")
        self.assertEqual(clauses[0].text, "Content goes here.")

    def test_lists_and_paragraphs(self):
        doc = (
            "## Eligibility\n"
            "### Requirements\n"
            "Applicants must meet:\n"
            "* Income under 50% AMI\n"
            "* 12 months residency\n"
            "\n"
            "Second paragraph with additional notes.\n"
        )
        clauses = parse_markdown_policy(doc, source_file="test.md")
        self.assertEqual(len(clauses), 1)
        self.assertIn("* Income under 50% AMI", clauses[0].text)
        self.assertIn("Second paragraph with additional notes.", clauses[0].text)
        self.assertEqual(clauses[0].source_start, 3)
        self.assertEqual(clauses[0].source_end, 7)

    def test_different_heading_levels(self):
        doc = (
            "# Main Title\n"
            "## Section Level 2\n"
            "### Subsection Level 3\n"
            "Level 3 text.\n"
            "#### Sub-subsection Level 4\n"
            "Level 4 text.\n"
        )
        clauses = parse_markdown_policy(doc, source_file="test.md")
        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0].heading, "Subsection Level 3")
        self.assertEqual(clauses[0].text, "Level 3 text.")
        self.assertEqual(clauses[1].heading, "Sub-subsection Level 4")
        self.assertEqual(clauses[1].text, "Level 4 text.")

    def test_end_of_file_clause(self):
        doc = (
            "## Final Section\n"
            "### Final Clause\n"
            "This clause ends exactly at EOF without trailing newline."
        )
        clauses = parse_markdown_policy(doc, source_file="test.md")
        self.assertEqual(len(clauses), 1)
        self.assertEqual(clauses[0].id, "C001")
        self.assertEqual(clauses[0].text, "This clause ends exactly at EOF without trailing newline.")
        self.assertEqual(clauses[0].source_start, 3)
        self.assertEqual(clauses[0].source_end, 3)


if __name__ == "__main__":
    unittest.main()
