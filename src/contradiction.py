import re
from dataclasses import dataclass
from typing import List, Tuple, Set
from src.models import Clause
from src.retriever import tokenize


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
    Extracts active numerical values paired with units (e.g. (30, 'days'), (15, 'days'), (50, 'percent')).
    If text is an amendment substitution, extracts the substituted active value (after 'substitute').
    Strips explanatory staff notes before parsing.
    """
    text_clean = re.sub(r"\*Note for staff:.*?\*", "", text, flags=re.DOTALL | re.IGNORECASE)
    sub_match = re.search(r"substitute\s+[\"'\*]*([^\n\"\*\.]+)[\"'\*]*", text_clean, re.IGNORECASE)
    if sub_match:
        text_to_parse = sub_match.group(1)
    else:
        text_to_parse = text_clean

    matches = []
    pattern = re.compile(
        r"\b(\d+)\s*(calendar days?|business days?|days?|weeks?|months?|years?|percent|%)\b",
        re.IGNORECASE,
    )
    for m in pattern.finditer(text_to_parse):
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
    among top-ranked relevant clauses sharing the exact same policy requirement.
    """

    def detect(self, query: str, clauses: List[Clause]) -> ContradictionResult:
        """
        Analyzes candidate clauses for genuine internal contradictions.
        """
        if len(clauses) < 2:
            return ContradictionResult(has_conflict=False, reason="", conflicting_clauses=[])

        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                c1 = clauses[i]
                c2 = clauses[j]

                # Amendment target substitutions are not contradictions
                if (c1.target_clause_id and c1.target_clause_id == c2.id) or (c2.target_clause_id and c2.target_clause_id == c1.id):
                    continue

                t1 = set(tokenize(f"{c1.section} {c1.heading} {c1.text}"))
                t2 = set(tokenize(f"{c2.section} {c2.heading} {c2.text}"))

                # Disambiguate interview notice from change reporting or appeal
                if ("interview" in t1 or "interview" in t2) and ("interview" not in t1 or "interview" not in t2):
                    continue

                topic_clusters = [
                    {"appeal"},
                    {"report", "reporting"},
                    {"disregard"},
                    {"sanction"},
                    {"overpayment"},
                ]

                has_same_topic = any((t1 & cluster) and (t2 & cluster) for cluster in topic_clusters)
                if not has_same_topic:
                    continue

                constraints1 = extract_numerical_constraints(c1.text)
                constraints2 = extract_numerical_constraints(c2.text)

                for val1, unit1 in constraints1:
                    for val2, unit2 in constraints2:
                        if unit1 == unit2 and val1 != val2:
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
