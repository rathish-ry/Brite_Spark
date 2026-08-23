from dataclasses import dataclass
from typing import List, Optional
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


def find_transitional_clause(clause: Clause, all_clauses: List[Clause]) -> Optional[Clause]:
    """
    Finds the relevant transitional provision clause (§5.1, §5.2, §5.3) for an amendment clause.
    """
    if not clause.amendment_id:
        return None

    if clause.applicability_type == "determination":
        # Governed by Paragraph 5.1
        for c in all_clauses:
            if c.amendment_id and ("paragraph 5.1" in c.heading.lower() or "**5.1**" in c.text):
                return c
    elif clause.applicability_type == "change_of_circumstance":
        # Governed by Paragraph 5.2
        for c in all_clauses:
            if c.amendment_id and ("paragraph 5.2" in c.heading.lower() or "**5.2**" in c.text):
                return c

    return None


class GroundedGenerator:
    """
    Synthesizes grounded policy answers exclusively from approved policy clauses
    and validates clause-level citations (including amendment rule and transitional clause binding).
    """

    def generate(self, question: str, approved_clauses: List[Clause], full_corpus: Optional[List[Clause]] = None) -> GroundedAnswer:
        """
        Generates a grounded answer with clause citations and verifiable sources block.
        Cites both the rule clause and transitional applicability clause when answering amendment queries.
        """
        if not approved_clauses:
            return GroundedAnswer(
                question=question,
                answer_text="No approved policy evidence was available to construct an answer.",
                sources_text="None",
                cited_clause_ids=[],
                status="REFUSED",
            )

        final_clauses: List[Clause] = list(approved_clauses)
        corpus_to_search = full_corpus or approved_clauses

        # Attach relevant transitional provision clauses for amendment rules
        added_transitional_ids = set()
        for clause in list(approved_clauses):
            if clause.amendment_id and clause.applicability_type in ("determination", "change_of_circumstance"):
                trans_clause = find_transitional_clause(clause, corpus_to_search)
                if trans_clause and trans_clause.id not in [c.id for c in final_clauses]:
                    final_clauses.append(trans_clause)
                    added_transitional_ids.add(trans_clause.id)

        answer_sentences = []
        for clause in final_clauses:
            text_lines = [line.strip() for line in clause.text.splitlines() if line.strip() and not line.strip().startswith("#")]
            clause_body = " ".join(text_lines)
            sentence = f"{clause_body} [{clause.id}]"
            answer_sentences.append(sentence)

        full_answer_text = "\n\n".join(answer_sentences)

        # Validate citations
        val_res = validate_citations(full_answer_text, final_clauses)
        if not val_res.is_valid:
            return GroundedAnswer(
                question=question,
                answer_text=f"Answer generation failed citation validation: {val_res.error_message}",
                sources_text="None",
                cited_clause_ids=[],
                status="REFUSED",
            )

        sources_block = format_sources_block(final_clauses)

        return GroundedAnswer(
            question=question,
            answer_text=full_answer_text,
            sources_text=sources_block,
            cited_clause_ids=val_res.cited_ids,
            status="ANSWERED",
        )
