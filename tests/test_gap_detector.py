import unittest
from src.config import EvidenceGateConfig
from src.models import Clause, EvidenceStatus
from src.retriever import RetrievalResult
from src.evidence_gate import EvidenceGate
from src.gap_detector import detect_apparent_gap


class TestApparentGapDetection(unittest.TestCase):

    def setUp(self):
        self.clause_appeal = Clause(
            id="C053",
            section="12.1 Right of appeal",
            heading="12.1 Right of appeal",
            text="An applicant may file a written appeal. The appeal must be lodged within 30 days of receiving notice.",
            source_start=584,
            source_end=588,
            source_file="data/policy.md",
        )
        self.config = EvidenceGateConfig(min_term_coverage=0.30)
        self.gate = EvidenceGate(self.config)

    def test_apparent_gap_detection(self):
        query = "Can a representative submit an appeal for a resident?"
        results = [
            RetrievalResult(
                clause=self.clause_appeal,
                score=0.85,
                matched_terms=["appeal", "submit"],
            )
        ]
        
        gap_res = detect_apparent_gap(query, [self.clause_appeal])
        self.assertTrue(gap_res.has_gap)

        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.REFUSE)
        self.assertIn("does not contain provisions or rules regarding", decision.reason)

    def test_no_apparent_gap_case(self):
        query = "How long do I have to file an appeal?"
        results = [
            RetrievalResult(
                clause=self.clause_appeal,
                score=0.85,
                matched_terms=["appeal", "days", "file"],
            )
        ]
        decision = self.gate.evaluate(query, results)
        self.assertEqual(decision.status, EvidenceStatus.ANSWERABLE)


if __name__ == "__main__":
    unittest.main()
