import re
from typing import List, Set
from src.config import EvidenceGateConfig
from src.models import Clause, EvidenceDecision, EvidenceStatus
from src.retriever import RetrievalResult, tokenize
from src.gap_detector import detect_apparent_gap
from src.contradiction import ContradictionDetector

RULE_KEYWORDS: Set[str] = {
    "must", "shall", "may", "will", "entitle", "entitled", "require", "required",
    "within", "exceed", "limit", "deadline", "period", "eligible", "eligibility",
    "prohibit", "prohibited", "grant", "deny", "denied", "terminate", "suspend",
    "recover", "amount", "percent", "days", "months", "year", "years"
}


def calculate_term_coverage(query_tokens: List[str], evidence_text: str) -> float:
    if not query_tokens:
        return 0.0
    evidence_tokens = set(tokenize(evidence_text))
    matched_count = sum(1 for q_tok in set(query_tokens) if q_tok in evidence_tokens)
    return matched_count / len(set(query_tokens))


def contains_rule_language(text: str) -> bool:
    text_lower = text.lower()
    has_keyword = any(kw in text_lower for kw in RULE_KEYWORDS)
    has_digits = bool(re.search(r"\b\d+\b", text_lower))
    return has_keyword or has_digits


class EvidenceGate:
    """
    Safety component that evaluates whether retrieved policy evidence is sufficient
    to safely answer a given question, checking for gaps and internal contradictions.
    """

    def __init__(self, config: EvidenceGateConfig = None):
        self.config = config or EvidenceGateConfig()
        self.contradiction_detector = ContradictionDetector()

    def evaluate(self, query: str, retrieved_results: List[RetrievalResult]) -> EvidenceDecision:
        if not retrieved_results or not query.strip():
            return EvidenceDecision(
                status=EvidenceStatus.REFUSE,
                reason="No policy evidence was retrieved for the question.",
                supported_clauses=[],
                top_score=0.0,
                term_coverage=0.0,
            )

        top_result = retrieved_results[0]
        top_score = top_result.score
        query_tokens = tokenize(query)

        eval_clauses = [res.clause for res in retrieved_results[: self.config.top_k_eval]]
        combined_evidence_text = " ".join([f"{c.heading} {c.text}" for c in eval_clauses])

        term_coverage = calculate_term_coverage(query_tokens, combined_evidence_text)

        # 1. Retrieval Score Threshold Check
        if top_score < self.config.min_retrieval_score:
            return EvidenceDecision(
                status=EvidenceStatus.REFUSE,
                reason=f"Retrieval confidence ({top_score:.4f}) is below minimum threshold ({self.config.min_retrieval_score:.4f}).",
                supported_clauses=[],
                top_score=top_score,
                term_coverage=term_coverage,
            )

        # 2. Contradiction Detection Check
        conflict_check = self.contradiction_detector.detect(query, eval_clauses)
        if conflict_check.has_conflict:
            return EvidenceDecision(
                status=EvidenceStatus.CONFLICT,
                reason=conflict_check.reason,
                supported_clauses=conflict_check.conflicting_clauses,
                top_score=top_score,
                term_coverage=term_coverage,
            )

        # 3. Apparent Gap Detection Check
        gap_check = detect_apparent_gap(query, eval_clauses)
        if gap_check.has_gap:
            return EvidenceDecision(
                status=EvidenceStatus.REFUSE,
                reason=gap_check.reason,
                supported_clauses=[],
                top_score=top_score,
                term_coverage=term_coverage,
            )

        # 4. Term Coverage Threshold Check
        if term_coverage < self.config.min_term_coverage:
            return EvidenceDecision(
                status=EvidenceStatus.REFUSE,
                reason=f"Query term coverage ({term_coverage:.2%}) is insufficient to answer the question with certainty.",
                supported_clauses=[],
                top_score=top_score,
                term_coverage=term_coverage,
            )

        # 5. Rule-like Language Verification
        if not contains_rule_language(top_result.clause.text):
            return EvidenceDecision(
                status=EvidenceStatus.REFUSE,
                reason="Retrieved text is topically related but lacks definitive policy rules or conditions.",
                supported_clauses=[],
                top_score=top_score,
                term_coverage=term_coverage,
            )

        # Collect top supported clauses matching score threshold
        supported = [top_result.clause]
        for res in retrieved_results[1: self.config.top_k_eval]:
            if res.score >= top_score * 0.7 and res.clause.id not in [c.id for c in supported]:
                supported.append(res.clause)

        return EvidenceDecision(
            status=EvidenceStatus.ANSWERABLE,
            reason="Sufficient grounding evidence identified with high confidence and query coverage.",
            supported_clauses=supported,
            top_score=top_score,
            term_coverage=term_coverage,
        )
