import unittest
from scripts.final_verification import (
    audit_1_parser,
    audit_2_retrieval,
    audit_3_evidence_gate,
    audit_8_benchmark,
    audit_10_documentation,
)


class TestFinalVerification(unittest.TestCase):

    def test_parser_audit(self):
        self.assertTrue(audit_1_parser())

    def test_retrieval_audit(self):
        self.assertTrue(audit_2_retrieval())

    def test_evidence_gate_audit(self):
        self.assertTrue(audit_3_evidence_gate())

    def test_benchmark_audit(self):
        ok, passed, total = audit_8_benchmark()
        self.assertTrue(ok)
        self.assertEqual(passed, 10)

    def test_documentation_audit(self):
        self.assertTrue(audit_10_documentation())


if __name__ == "__main__":
    unittest.main()
