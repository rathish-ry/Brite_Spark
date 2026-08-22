import unittest
from scripts.package_submission import check_required_artifacts, run_eval_benchmark


class TestSubmissionPackaging(unittest.TestCase):

    def test_required_artifacts_present(self):
        self.assertTrue(check_required_artifacts())

    def test_eval_benchmark_ready(self):
        ok, passed, total = run_eval_benchmark()
        self.assertTrue(ok)
        self.assertEqual(passed, total)
        self.assertEqual(total, 10)


if __name__ == "__main__":
    unittest.main()
