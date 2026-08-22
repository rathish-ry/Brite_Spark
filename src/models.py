from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, List


class EvidenceStatus(str, Enum):
    ANSWERABLE = "ANSWERABLE"
    REFUSE = "REFUSE"
    CONFLICT = "CONFLICT"


@dataclass
class Clause:
    """
    Represents a structured policy clause extracted from Markdown.
    """
    id: str
    section: str
    heading: str
    text: str
    source_start: int
    source_end: int
    source_file: str = "data/policy.md"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        return f"[{self.id}] {self.section} — {self.heading} (Lines {self.source_start}-{self.source_end})"


@dataclass
class EvidenceDecision:
    """
    Structured outcome returned by the Evidence Gate.
    """
    status: EvidenceStatus
    reason: str
    supported_clauses: List[Clause]
    top_score: float
    term_coverage: float

    def summary(self) -> str:
        clauses_str = ", ".join([c.id for c in self.supported_clauses]) if self.supported_clauses else "None"
        return (
            f"Status: {self.status.value}\n"
            f"Reason: {self.reason}\n"
            f"Top Score: {self.top_score:.4f}\n"
            f"Term Coverage: {self.term_coverage:.2%}\n"
            f"Supported Clauses: [{clauses_str}]"
        )
