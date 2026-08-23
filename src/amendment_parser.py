import re
from typing import List
from src.models import Clause


def parse_amendment_policy(content: str, source_file: str = "data/Amendment No. 2026-01.md") -> List[Clause]:
    """
    Parses an Amendment Markdown document into a list of Clause objects
    annotated with temporal metadata, amendment ID, applicability type, and target clause mappings.
    Splits sections and numbered paragraphs (**1.1**, **2.1**, **5.1**, etc.).
    """
    lines = content.splitlines()
    clauses: List[Clause] = []

    amendment_id = "A2026-01"
    effective_date = "2026-03-01"

    current_section = "Amendment No. 2026-01"
    current_heading = "Overview"
    current_text_lines: List[str] = []
    current_start_line: int | None = None
    current_end_line: int | None = None
    clause_counter = 1

    def flush_clause():
        nonlocal clause_counter, current_text_lines, current_start_line, current_end_line
        if current_text_lines and current_start_line is not None and current_end_line is not None:
            raw_lines = current_text_lines
            first_idx = 0
            while first_idx < len(raw_lines) and not raw_lines[first_idx].strip():
                first_idx += 1
            last_idx = len(raw_lines) - 1
            while last_idx >= 0 and not raw_lines[last_idx].strip():
                last_idx -= 1

            if first_idx <= last_idx:
                trimmed = raw_lines[first_idx : last_idx + 1]
                actual_start = current_start_line + first_idx
                actual_end = current_start_line + last_idx
                clause_text = "\n".join(trimmed).strip()

                if clause_text and clause_text != "---" and not clause_text.startswith("*End of"):
                    clause_id = f"{amendment_id}-C{clause_counter:02d}"
                    clause = Clause(
                        id=clause_id,
                        section=current_section,
                        heading=current_heading,
                        text=clause_text,
                        source_start=actual_start,
                        source_end=actual_end,
                        source_file=source_file,
                        amendment_id=amendment_id,
                        effective_date=effective_date,
                    )

                    heading_lower = current_heading.lower()
                    sec_lower = current_section.lower()

                    # Exact rule mappings by paragraph heading / section
                    if "paragraph 1.1" in heading_lower or clause_text.startswith("**1.1**"):
                        clause.target_clause_id = "C024"
                        clause.amendment_type = "substitution"
                        clause.applicability_type = "determination"
                    elif "paragraph 2.1" in heading_lower or clause_text.startswith("**2.1**"):
                        clause.target_clause_id = "C015"
                        clause.amendment_type = "substitution"
                        clause.applicability_type = "change_of_circumstance"
                    elif "paragraph 2.2" in heading_lower or clause_text.startswith("**2.2**"):
                        clause.target_clause_id = "C038"
                        clause.amendment_type = "substitution"
                        clause.applicability_type = "change_of_circumstance"
                    elif "paragraph 3.1" in heading_lower or clause_text.startswith("**3.1**"):
                        clause.target_clause_id = "C026"
                        clause.amendment_type = "substitution"
                        clause.applicability_type = "determination"
                    elif "paragraph 4.1" in heading_lower or clause_text.startswith("**4.1**"):
                        clause.target_clause_id = "C048"
                        clause.amendment_type = "substitution"
                        clause.applicability_type = "determination"
                    elif "paragraph 4.2" in heading_lower or clause_text.startswith("**4.2**") or "10.5.3a" in clause_text.lower():
                        clause.target_clause_id = "C048A"
                        clause.amendment_type = "insertion"
                        clause.applicability_type = "determination"
                    elif "transitional" in sec_lower or "transitional" in heading_lower or any(clause_text.startswith(f"**5.{i}**") for i in range(1, 10)):
                        clause.amendment_type = "transitional"
                        clause.applicability_type = "transitional"
                    else:
                        clause.amendment_type = "general"
                        clause.applicability_type = "general"

                    clauses.append(clause)
                    clause_counter += 1

        current_text_lines = []
        current_start_line = None
        current_end_line = None

    heading_regex = re.compile(r"^(#{1,6})\s+(.*)$")
    para_regex = re.compile(r"^\*\*([0-9]+\.[0-9]+[A-Za-z]?)\*\*\s*(.*)$")

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        h_match = heading_regex.match(stripped)
        p_match = para_regex.match(stripped)

        if h_match:
            flush_clause()
            level = len(h_match.group(1))
            h_text = h_match.group(2).strip()
            if level <= 2:
                current_section = h_text
                current_heading = h_text
            else:
                current_heading = h_text
        elif p_match:
            flush_clause()
            para_num = p_match.group(1)
            current_heading = f"Paragraph {para_num}"
            if current_start_line is None:
                current_start_line = line_idx
            current_end_line = line_idx
            current_text_lines.append(line)
        else:
            if stripped == "---":
                flush_clause()
                continue

            if current_start_line is None:
                current_start_line = line_idx
            current_end_line = line_idx
            current_text_lines.append(line)

    flush_clause()
    return clauses
