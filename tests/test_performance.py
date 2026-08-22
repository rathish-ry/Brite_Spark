import unittest
import time
from src.models import Clause
from src.parser import parse_markdown_policy
from src.retriever import BM25Retriever


class TestPerformanceBenchmarks(unittest.TestCase):

    def setUp(self):
        self.sample_markdown = """# Section 1
## Clause 1
This is a sample policy clause for testing performance thresholds.
"""
        self.clauses = parse_markdown_policy(self.sample_markdown, source_file="data/policy.md")

    def test_indexing_latency_threshold(self):
        t0 = time.perf_counter()
        retriever = BM25Retriever(self.clauses)
        t1 = time.perf_counter()

        indexing_ms = (t1 - t0) * 1000.0
        self.assertLess(indexing_ms, 100.0, "Indexing latency should be under 100ms for small policies.")

    def test_retrieval_latency_threshold(self):
        retriever = BM25Retriever(self.clauses)
        t0 = time.perf_counter()
        results = retriever.retrieve("testing performance", top_k=5)
        t1 = time.perf_counter()

        retrieval_ms = (t1 - t0) * 1000.0
        self.assertLess(retrieval_ms, 50.0, "Retrieval latency should be under 50ms.")


if __name__ == "__main__":
    unittest.main()
