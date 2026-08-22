import unittest
from src.models import Clause
from src.retriever import BM25Retriever


class TestBM25Retriever(unittest.TestCase):

    def setUp(self):
        self.sample_clauses = [
            Clause(
                id="C001",
                section="Eligibility",
                heading="Income Requirements",
                text="The household gross income must not exceed 50 percent of the Area Median Income.",
                source_start=10,
                source_end=15,
                source_file="data/policy.md",
            ),
            Clause(
                id="C002",
                section="Appeals",
                heading="Appeal Deadline",
                text="An applicant must submit a written appeal within 30 calendar days of the decision notice.",
                source_start=20,
                source_end=25,
                source_file="data/policy.md",
            ),
            Clause(
                id="C003",
                section="Residency",
                heading="Residency Requirements",
                text="Applicants must demonstrate continuous legal residency in the municipality for 12 months.",
                source_start=30,
                source_end=35,
                source_file="data/policy.md",
            ),
        ]
        self.retriever = BM25Retriever(self.sample_clauses)

    def test_clearly_relevant_question(self):
        query = "How long do I have to submit an appeal?"
        results = self.retriever.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].clause.id, "C002")
        self.assertGreater(results[0].score, 0.5)

    def test_synonym_and_stemming_variation(self):
        # "appeals deadline timeline submitting"
        query = "appeals deadline timeline submitting"
        results = self.retriever.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].clause.id, "C002")

    def test_irrelevant_question(self):
        query = "What is the recipe for baking chocolate fudge cake?"
        results = self.retriever.retrieve(query, top_k=3)
        self.assertEqual(len(results), 0)

    def test_short_question(self):
        query = "Income limit?"
        results = self.retriever.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].clause.id, "C001")

    def test_long_question(self):
        query = "Can you provide full details on how many months of continuous legal residency an applicant needs prior to applying?"
        results = self.retriever.retrieve(query, top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].clause.id, "C003")


if __name__ == "__main__":
    unittest.main()
