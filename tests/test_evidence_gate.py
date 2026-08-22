import unittest
from src.config import EvidenceGateConfig
from src.models import Clause, EvidenceStatus
from src.retriever import RetrievalResult
from src.evidence_gate import EvidenceGate


class TestEvidenceGate(unittest.TestCase):

    def setUp(self):
        self.clause_appeal = Clause(
            id="C053",
            section="Appeals",
            heading="Right of Appeal",
            text="An appeal must be lodged within 30 days of receiving the determination notice.",
            source_start=584,
            source_end=588,
            source_file="data/policy.md",
        )
        self.clause_vague = Clause(
            id="C001",
            section="General",
            heading="Overview",
            text="This document provides general information about municipal support programs.",
            source_start=1,
            source_end=5,
            source_file="data/policy.md",
        )
        self.config = EvidenceGateConfig(
            min_retrieval_score=0.25,
            min_term_coverage=0.25,
        )
        self.gate = EvidenceGate(self.config)

    def test_answerable_case(self):
        query = "How long do I have to file an appeal?"
        results = [
            RetrievalResult(
                clause=self.clause_appeal,
                score=0.85,
                matched_terms=["appeal", "days"],
            )
        ]
        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.ANSWERABLE)
        self.assertEqual(len(decision.supported_clauses), 1)
        self.assertEqual(decision.supported_clauses[0].id, "C053")

    def test_low_retrieval_score_refusal(self):
        query = "How long do I have to file an appeal?"
        results = [
            RetrievalResult(
                clause=self.clause_appeal,
                score=0.10,  # Below min threshold 0.25
                matched_terms=["appeal"],
            )
        ]
        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.REFUSE)
        self.assertIn("below minimum threshold", decision.reason)

    def test_low_term_coverage_refusal(self):
        # Query has many terms, but evidence only matches 1 out of 6
        query = "What specific medical certificate documents are required for disabled veteran exemption?"
        results = [
            RetrievalResult(
                clause=self.clause_vague,
                score=0.40,
                matched_terms=["document"],
            )
        ]
        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.REFUSE)
        self.assertTrue("term coverage" in decision.reason or "does not contain" in decision.reason)

    def test_empty_retrieval_refusal(self):
        query = "Can I request space exploration funding?"
        decision = self.gate.evaluate(query, [])
        self.assertEqual(decision.status, EvidenceStatus.REFUSE)
        self.assertIn("No policy evidence was retrieved", decision.reason)


if __name__ == "__main__":
    unittest.main()
