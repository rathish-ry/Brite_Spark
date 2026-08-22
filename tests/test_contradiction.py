import unittest
from src.models import Clause, EvidenceStatus
from src.retriever import RetrievalResult
from src.contradiction import ContradictionDetector
from src.evidence_gate import EvidenceGate
from src.refusal import build_refusal_response


class TestContradictionDetection(unittest.TestCase):

    def setUp(self):
        self.c1 = Clause(
            id="C017",
            section="Appeals",
            heading="Appeal Deadline Standard",
            text="Appeals must be filed within 30 days of the decision notice.",
            source_start=140,
            source_end=146,
            source_file="data/policy.md",
        )
        self.c2 = Clause(
            id="C031",
            section="Appeals",
            heading="Appeal Deadline Fast-Track",
            text="Appeals must be filed within 15 days of the decision notice.",
            source_start=360,
            source_end=366,
            source_file="data/policy.md",
        )
        self.detector = ContradictionDetector()
        self.gate = EvidenceGate()

    def test_detect_numerical_contradiction(self):
        query = "How long do I have to file an appeal?"
        res = self.detector.detect(query, [self.c1, self.c2])
        self.assertTrue(res.has_conflict)
        self.assertEqual(len(res.conflicting_clauses), 2)
        self.assertIn("30 days", res.reason)
        self.assertIn("15 days", res.reason)

    def test_evidence_gate_returns_conflict_status(self):
        query = "How long do I have to file an appeal?"
        results = [
            RetrievalResult(clause=self.c1, score=0.90, matched_terms=["appeal", "days"]),
            RetrievalResult(clause=self.c2, score=0.88, matched_terms=["appeal", "days"]),
        ]
        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.CONFLICT)

        refusal = build_refusal_response(
            question=query,
            reason=decision.reason,
            status=decision.status.value,
            conflicting_clauses=decision.supported_clauses,
        )
        formatted = refusal.format_cli()
        self.assertIn("REFUSAL — CONFLICTING POLICY", formatted)
        self.assertIn("[C017]", formatted)
        self.assertIn("[C031]", formatted)
        self.assertIn("STATUS: REFUSED_CONFLICT", formatted)


if __name__ == "__main__":
    unittest.main()
