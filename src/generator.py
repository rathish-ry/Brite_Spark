from dataclasses import dataclass
from typing import List
from src.models import Clause
from src.citations import validate_citations, format_sources_block


@dataclass
class GroundedAnswer:
    """
    Represents a synthesized answer grounded strictly in approved policy evidence with verifiable citations.
    """
    question: str
    answer_text: str
    sources_text: str
    cited_clause_ids: List[str]
    status: str = "ANSWERED"

    def format_cli(self) -> str:
        return (
            "========================================\n"
            "       GROUNDED POLICY ASSISTANT        \n"
            "========================================\n\n"
            f"Question:\n> {self.question}\n\n"
            "ANSWER\n\n"
            f"{self.answer_text}\n\n"
            "SOURCES\n\n"
            f"{self.sources_text}\n\n"
            f"STATUS: {self.status}"
        )


class GroundedGenerator:
    """
    Synthesizes grounded policy answers exclusively from approved policy clauses
    and validates clause-level citations.
    """

    def generate(self, question: str, approved_clauses: List[Clause]) -> GroundedAnswer:
        """
        Generates a grounded answer with clause citations and verifiable sources block.
        """
        if not approved_clauses:
            return GroundedAnswer(
                question=question,
                answer_text="No approved policy evidence was available to construct an answer.",
                sources_text="None",
                cited_clause_ids=[],
                status="REFUSED",
            )

        cited_ids = []
        answer_sentences = []

        for clause in approved_clauses:
            cited_ids.append(clause.id)
            text_lines = [line.strip() for line in clause.text.splitlines() if line.strip() and not line.strip().startswith("#")]
            clause_body = " ".join(text_lines)
            sentence = f"{clause_body} [{clause.id}]"
            answer_sentences.append(sentence)

        full_answer_text = "\n\n".join(answer_sentences)

        # Validate citations
        val_res = validate_citations(full_answer_text, approved_clauses)
        if not val_res.is_valid:
            return GroundedAnswer(
                question=question,
                answer_text=f"Answer generation failed citation validation: {val_res.error_message}",
                sources_text="None",
                cited_clause_ids=[],
                status="REFUSED",
            )

        sources_block = format_sources_block(approved_clauses)

        return GroundedAnswer(
            question=question,
            answer_text=full_answer_text,
            sources_text=sources_block,
            cited_clause_ids=val_res.cited_ids,
            status="ANSWERED",
        )
