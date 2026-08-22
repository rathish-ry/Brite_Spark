import unittest
from src.models import Clause
from src.interactive import print_help


class TestInteractiveCLI(unittest.TestCase):

    def setUp(self):
        self.clause = Clause(
            id="C001",
            section="Section 1",
            heading="Heading 1",
            text="Text for clause C001.",
            source_start=1,
            source_end=5,
            source_file="data/policy.md",
        )

    def test_print_help_output(self):
        # Verify print_help executes without error
        try:
            print_help()
            success = True
        except Exception:
            success = False
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
