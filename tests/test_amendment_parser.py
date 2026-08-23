import unittest
from pathlib import Path
from src.amendment_parser import parse_amendment_policy


class TestAmendmentParser(unittest.TestCase):

    def setUp(self):
        self.amendment_path = Path("data/Amendment No. 2026-01.md")
        with open(self.amendment_path, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_parse_amendment_clauses(self):
        clauses = parse_amendment_policy(self.content, source_file=str(self.amendment_path))
        self.assertGreater(len(clauses), 0)

        # Check metadata on amendment clauses
        for c in clauses:
            self.assertEqual(c.amendment_id, "A2026-01")
            self.assertEqual(c.effective_date, "2026-03-01")
            self.assertEqual(c.source_file, str(self.amendment_path))

    def test_amendment_rule_mappings(self):
        clauses = parse_amendment_policy(self.content, source_file=str(self.amendment_path))
        
        # Verify target clause mappings and applicability types
        target_map = {c.target_clause_id: c for c in clauses if c.target_clause_id}
        
        self.assertIn("C024", target_map)  # §6.4.1(a) $120 -> $175
        self.assertEqual(target_map["C024"].applicability_type, "determination")
        self.assertIn("$175", target_map["C024"].text)

        self.assertIn("C013", target_map)  # §4.3.2 10 -> 14 days
        self.assertEqual(target_map["C013"].applicability_type, "change_of_circumstance")
        self.assertIn("14 calendar days", target_map["C013"].text)

        self.assertIn("C038", target_map)  # §9.1.4 30 -> 14 days
        self.assertEqual(target_map["C038"].applicability_type, "change_of_circumstance")

        self.assertIn("C048", target_map)  # §10.5.2 20% -> 15%
        self.assertEqual(target_map["C048"].applicability_type, "determination")

        self.assertIn("C048A", target_map) # §10.5.3A insertion
        self.assertEqual(target_map["C048A"].amendment_type, "insertion")

        # Verify transitional provisions presence
        transitional_clauses = [c for c in clauses if c.applicability_type == "transitional"]
        self.assertGreater(len(transitional_clauses), 0)


if __name__ == "__main__":
    unittest.main()
