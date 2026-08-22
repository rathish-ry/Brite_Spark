from dataclasses import dataclass, field
from typing import List
from src.models import Clause


@dataclass
class RefusalResponse:
    """
    Encapsulates a structured policy refusal when the manual cannot answer a question safely.
    """
    question: str
    reason: str
    next_step: str = "Refer the case to the Benefits Policy Supervisor for a formal policy ruling."
    status: str = "REFUSED"
    conflicting_clauses: List[Clause] = field(default_factory=list)

    def format_cli(self) -> str:
        """
        Formats the refusal output for CLI presentation according to challenge requirements.
        """
        if self.status in ("CONFLICT", "REFUSED_CONFLICT"):
            clauses_block = ""
            for c in self.conflicting_clauses:
                clauses_block += f"[{c.id}] {c.section} — {c.heading}\nSource: {c.source_file} lines {c.source_start}-{c.source_end}\n{c.text}\n\n"

            return (
                "========================================\n"
                "       GROUNDED POLICY ASSISTANT        \n"
                "========================================\n\n"
                f"Question:\n> {self.question}\n\n"
                "REFUSAL — CONFLICTING POLICY\n\n"
                "The manual contains conflicting clauses.\n\n"
                f"{clauses_block}"
                "The system cannot determine which requirement controls.\n\n"
                "Next step:\n"
                f"{self.next_step}\n\n"
                "STATUS: REFUSED_CONFLICT"
            )

        return (
            "========================================\n"
            "       GROUNDED POLICY ASSISTANT        \n"
            "========================================\n\n"
            f"Question:\n> {self.question}\n\n"
            "REFUSAL\n\n"
            "The manual does not settle this question with sufficient confidence.\n\n"
            "Reason:\n"
            f"{self.reason}\n\n"
            "Next step:\n"
            f"{self.next_step}\n\n"
            f"STATUS: {self.status}"
        )


def build_refusal_response(
    question: str,
    reason: str,
    status: str = "REFUSED",
    conflicting_clauses: List[Clause] = None,
) -> RefusalResponse:
    """
    Constructs a RefusalResponse with appropriate supervisor escalation next-steps.
    """
    next_step = "Refer the case to the Benefits Policy Supervisor for a formal policy ruling."
    return RefusalResponse(
        question=question,
        reason=reason,
        next_step=next_step,
        status=status,
        conflicting_clauses=conflicting_clauses or [],
    )
