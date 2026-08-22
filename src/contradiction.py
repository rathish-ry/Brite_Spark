import re
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional
from src.models import Clause
from src.retriever import tokenize, STOP_WORDS


@dataclass
class ContradictionResult:
    """
    Represents the outcome of a policy contradiction check.
    """
    has_conflict: bool
    reason: str
    conflicting_clauses: List[Clause]


def extract_numerical_constraints(text: str) -> List[Tuple[int, str]]:
    """
    Extracts numerical values paired with units (e.g. (30, 'days'), (15, 'days'), (50, 'percent')).
    """
    matches = []
    # Pattern for numbers followed by units like days, weeks, months, percent, etc.
    pattern = re.compile(
        r"\b(\d+)\s*(calendar days?|business days?|days?|weeks?|months?|years?|percent|%)\b",
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        val = int(m.group(1))
        unit = m.group(2).lower()
        if "day" in unit:
            unit = "days"
        elif "month" in unit:
            unit = "months"
        elif "year" in unit:
            unit = "years"
        elif "%" in unit:
            unit = "percent"
        matches.append((val, unit))
    return matches


class ContradictionDetector:
    """
    Conservative contradiction detector that identifies conflicting policy rules
    among top-ranked relevant clauses.
    """

    def detect(self, query: str, clauses: List[Clause]) -> ContradictionResult:
        """
        Analyzes candidate clauses for genuine internal contradictions.
        """
        if len(clauses) < 2:
            return ContradictionResult(has_conflict=False, reason="", conflicting_clauses=[])

        query_tokens = set(tokenize(query))

        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                c1 = clauses[i]
                c2 = clauses[j]

                # Check topic overlap between clauses
                t1 = set(tokenize(f"{c1.section} {c1.heading} {c1.text}"))
                t2 = set(tokenize(f"{c2.section} {c2.heading} {c2.text}"))
                
                shared_tokens = t1 & t2 & (query_tokens | {"appeal", "income", "day", "days", "limit", "period", "overpayment"})
                
                # Must share core policy keywords to be compared
                if len(shared_tokens) < 1:
                    continue

                # Extract numerical rules
                constraints1 = extract_numerical_constraints(c1.text)
                constraints2 = extract_numerical_constraints(c2.text)

                for val1, unit1 in constraints1:
                    for val2, unit2 in constraints2:
                        if unit1 == unit2 and val1 != val2:
                            # Genuine conflicting requirement detected
                            reason = (
                                f"Clause [{c1.id}] specifies {val1} {unit1}, whereas "
                                f"Clause [{c2.id}] specifies {val2} {unit2} for the same policy requirement."
                            )
                            return ContradictionResult(
                                has_conflict=True,
                                reason=reason,
                                conflicting_clauses=[c1, c2],
                            )

        return ContradictionResult(has_conflict=False, reason="", conflicting_clauses=[])
