import unittest
from tests.audit_system import (
    audit_file_structure,
    audit_python_syntax,
    audit_policy_parsing,
    audit_eval_datasets,
)


class TestSystemAudit(unittest.TestCase):

    def test_file_structure_integrity(self):
        self.assertTrue(audit_file_structure())

    def test_python_syntax_and_imports(self):
        ok, count = audit_python_syntax()
        self.assertTrue(ok)
        self.assertGreaterEqual(count, 10)

    def test_policy_parsing_integrity(self):
        ok, count, errs = audit_policy_parsing()
        self.assertTrue(ok)
        self.assertGreater(count, 0)
        self.assertEqual(errs, 0)

    def test_eval_datasets_integrity(self):
        self.assertTrue(audit_eval_datasets())


if __name__ == "__main__":
    unittest.main()
