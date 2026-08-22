from dataclasses import dataclass


@dataclass
class RefusalResponse:
    """
    Encapsulates a structured policy refusal when the manual cannot answer a question safely.
    """
    question: str
    reason: str
    next_step: str = "Refer the case to the appropriate policy supervisor."
    status: str = "REFUSED"

    def format_cli(self) -> str:
        """
        Formats the refusal output for CLI presentation according to challenge requirements.
        """
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


def build_refusal_response(question: str, reason: str, status: str = "REFUSED") -> RefusalResponse:
    """
    Constructs a RefusalResponse with appropriate supervisor escalation next-steps.
    """
    next_step = "Refer the case to the Benefits Policy Supervisor for a formal policy ruling."
    return RefusalResponse(
        question=question,
        reason=reason,
        next_step=next_step,
        status=status,
    )
