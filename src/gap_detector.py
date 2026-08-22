from dataclasses import dataclass
from typing import List, Set
from src.models import Clause
from src.retriever import tokenize, STOP_WORDS

# Common policy actions, verbs, question descriptors, and general terms
GENERAL_TOPIC_TERMS: Set[str] = {
    "appeal", "appeals", "apply", "application", "determination", "decision",
    "income", "residence", "residency", "benefit", "benefits", "payment",
    "award", "review", "overpayment", "grant", "allowance", "qualify",
    "eligibility", "eligible", "hearing", "notice", "time", "limit", "period",
    "file", "lodged", "lodge", "submit", "submission", "make", "request", "receive",
    "long", "much", "many", "take", "need", "give", "get", "type", "days", "months", "years"
}


@dataclass
class GapCheckResult:
    """
    Represents the outcome of an apparent policy gap check.
    """
    has_gap: bool
    reason: str
    missing_terms: List[str]


def detect_apparent_gap(query: str, clauses: List[Clause]) -> GapCheckResult:
    """
    Analyzes whether a query contains specific subject/entity terms that are absent
    from the retrieved policy evidence text, indicating an apparent policy gap.
    """
    if not clauses or not query.strip():
        return GapCheckResult(has_gap=False, reason="", missing_terms=[])

    query_tokens = tokenize(query)
    
    qualifier_terms = [
        tok for tok in query_tokens
        if tok not in GENERAL_TOPIC_TERMS and tok not in STOP_WORDS
    ]

    if not qualifier_terms:
        return GapCheckResult(has_gap=False, reason="", missing_terms=[])

    combined_text = " ".join([f"{c.section} {c.heading} {c.text}" for c in clauses])
    evidence_tokens = set(tokenize(combined_text))

    missing_qualifiers = [term for term in set(qualifier_terms) if term not in evidence_tokens]

    if missing_qualifiers:
        missing_str = ", ".join([f"'{term}'" for term in sorted(missing_qualifiers)])
        topic_heading = clauses[0].heading if clauses else "the policy topic"
        reason = (
            f"The policy manual discusses {topic_heading}, but does not contain provisions "
            f"or rules regarding {missing_str}."
        )
        return GapCheckResult(
            has_gap=True,
            reason=reason,
            missing_terms=sorted(missing_qualifiers),
        )

    return GapCheckResult(has_gap=False, reason="", missing_terms=[])
