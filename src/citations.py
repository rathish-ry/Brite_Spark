import re
from dataclasses import dataclass
from typing import List, Set, Tuple
from src.models import Clause


@dataclass
class CitationValidationResult:
    """
    Represents the result of validating clause-level citations in a generated answer.
    """
    is_valid: bool
    cited_ids: List[str]
    error_message: str = ""


def extract_citation_tags(text: str) -> List[str]:
    """
    Extracts clause citation tags matching pattern [C001], [C021], etc.
    """
    pattern = re.compile(r"\[(C\d{3})\]", re.IGNORECASE)
    return [match.upper() for match in pattern.findall(text)]


def validate_citations(answer_text: str, approved_clauses: List[Clause]) -> CitationValidationResult:
    """
    Strictly validates that every substantive claim in the answer is cited
    and that all cited clause IDs exist in the approved evidence list.
    """
    if not answer_text.strip():
        return CitationValidationResult(is_valid=False, cited_ids=[], error_message="Answer text is empty.")

    valid_approved_ids: Set[str] = {c.id.upper() for c in approved_clauses}
    extracted_ids = extract_citation_tags(answer_text)

    if not extracted_ids:
        return CitationValidationResult(
            is_valid=False,
            cited_ids=[],
            error_message="Answer contains substantive claims without clause citations (e.g. [C001]).",
        )

    # Check for invalid clause IDs
    for cid in extracted_ids:
        if cid not in valid_approved_ids:
            return CitationValidationResult(
                is_valid=False,
                cited_ids=extracted_ids,
                error_message=f"Answer cites unapproved or non-existent clause ID [{cid}].",
            )

    # Verify that every substantive claim block/paragraph has at least one citation tag
    paragraphs = [p.strip() for p in answer_text.split("\n\n") if p.strip()]
    for p in paragraphs:
        if not extract_citation_tags(p):
            return CitationValidationResult(
                is_valid=False,
                cited_ids=extracted_ids,
                error_message=f"Uncited substantive claim detected: '{p}'",
            )

    return CitationValidationResult(
        is_valid=True,
        cited_ids=list(set(extracted_ids)),
        error_message="",
    )


def format_sources_block(approved_clauses: List[Clause]) -> str:
    """
    Formats the detailed, verifiable source section for caseworker inspection.
    """
    blocks = []
    for c in approved_clauses:
        block = (
            f"[{c.id}] {c.section} — {c.heading}\n"
            f"Source: {c.source_file} lines {c.source_start}-{c.source_end}\n\n"
            f"\"{c.text}\""
        )
        blocks.append(block)
    return "\n\n".join(blocks)
