from dataclasses import dataclass, asdict
from typing import Dict, Any


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
