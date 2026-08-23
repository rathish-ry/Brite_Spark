import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
_scripts = _root / "scripts"
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_scripts))

import unittest
from package_submission import check_required_artifacts, run_eval_benchmark


class TestSubmissionPackaging(unittest.TestCase):

    def test_required_artifacts_present(self):
        self.assertTrue(check_required_artifacts())

    def test_eval_benchmark_ready(self):
        ok, passed, total = run_eval_benchmark()
        self.assertTrue(ok)
        self.assertEqual(passed, total)
        self.assertEqual(total, 18)


if __name__ == "__main__":
    unittest.main()
