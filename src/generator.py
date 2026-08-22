from dataclasses import dataclass
from typing import List
from src.models import Clause


@dataclass
class GroundedAnswer:
    """
    Represents a synthesized answer grounded strictly in approved policy evidence.
    """
    question: str
    answer_text: str
    cited_clause_ids: List[str]
    status: str = "ANSWERED"

    def format_cli(self) -> str:
        citations_str = ", ".join([f"[{cid}]" for cid in self.cited_clause_ids])
        return (
            "========================================\n"
            "       GROUNDED POLICY ASSISTANT        \n"
            "========================================\n\n"
            f"Question:\n> {self.question}\n\n"
            "ANSWER\n\n"
            f"{self.answer_text}\n\n"
            f"Citations: {citations_str}\n\n"
            f"STATUS: {self.status}"
        )


class GroundedGenerator:
    """
    Synthesizes grounded policy answers exclusively from approved policy clauses.
    Never invents unstated requirements, exceptions, deadlines, or amounts.
    """

    def generate(self, question: str, approved_clauses: List[Clause]) -> GroundedAnswer:
        """
        Generates a grounded answer with clause citations from approved clauses.
        """
        if not approved_clauses:
            return GroundedAnswer(
                question=question,
                answer_text="No approved policy evidence was available to construct an answer.",
                cited_clause_ids=[],
                status="REFUSED",
            )

        cited_ids = []
        answer_sentences = []

        for clause in approved_clauses:
            cited_ids.append(clause.id)
            # Format clean, grounded text directly from the clause content
            text_lines = [line.strip() for line in clause.text.splitlines() if line.strip() and not line.strip().startswith("#")]
            clause_body = " ".join(text_lines)
            
            # Append clause citation tag directly to the claim
            sentence = f"{clause_body} [{clause.id}]"
            answer_sentences.append(sentence)

        full_answer_text = "\n\n".join(answer_sentences)

        return GroundedAnswer(
            question=question,
            answer_text=full_answer_text,
            cited_clause_ids=cited_ids,
            status="ANSWERED",
        )
