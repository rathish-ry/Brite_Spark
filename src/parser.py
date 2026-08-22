import re
from typing import List
from src.models import Clause


def parse_markdown_policy(content: str, source_file: str = "data/policy.md") -> List[Clause]:
    """
    Parses a Markdown policy document into a list of structured Clause objects.
    Preserves line numbers (1-indexed) for precise citation verification.
    """
    lines = content.splitlines()
    clauses: List[Clause] = []
    
    current_section = "General"
    current_heading = "Overview"
    
    current_text_lines: List[str] = []
    current_start_line: int | None = None
    current_end_line: int | None = None
    
    clause_counter = 1

    def flush_current_clause():
        nonlocal clause_counter, current_text_lines, current_start_line, current_end_line
        if current_text_lines and current_start_line is not None and current_end_line is not None:
            # Strip empty lines from start and end while keeping accurate line numbers
            raw_lines = current_text_lines
            
            # Find first non-empty relative line
            first_idx = 0
            while first_idx < len(raw_lines) and not raw_lines[first_idx].strip():
                first_idx += 1
                
            # Find last non-empty relative line
            last_idx = len(raw_lines) - 1
            while last_idx >= 0 and not raw_lines[last_idx].strip():
                last_idx -= 1
                
            if first_idx <= last_idx:
                trimmed_lines = raw_lines[first_idx : last_idx + 1]
                actual_start = current_start_line + first_idx
                actual_end = current_start_line + last_idx
                
                clause_text = "\n".join(trimmed_lines).strip()
                # Ignore empty separators or horizontal rules alone
                if clause_text and clause_text != "---":
                    clause_id = f"C{clause_counter:03d}"
                    clause = Clause(
                        id=clause_id,
                        section=current_section,
                        heading=current_heading,
                        text=clause_text,
                        source_start=actual_start,
                        source_end=actual_end,
                        source_file=source_file,
                    )
                    clauses.append(clause)
                    clause_counter += 1

        current_text_lines = []
        current_start_line = None
        current_end_line = None

    heading_regex = re.compile(r"^(#{1,6})\s+(.*)$")

    for line_idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        match = heading_regex.match(stripped)

        if match:
            # We hit a heading: flush previous clause
            flush_current_clause()

            level = len(match.group(1))
            heading_text = match.group(2).strip()

            if level == 1:
                # Top-level document title or major section
                current_section = heading_text
                current_heading = heading_text
            elif level == 2:
                # Major section
                current_section = heading_text
                current_heading = heading_text
            else:
                # Subsection or clause-level heading (H3, H4, etc.)
                current_heading = heading_text
        else:
            # Normal text line (paragraph, list, blockquote, hr, blank line)
            if stripped == "---":
                # Horizontal rule separator - flush clause
                flush_current_clause()
                continue

            if current_start_line is None:
                current_start_line = line_idx

            current_end_line = line_idx
            current_text_lines.append(line)

    # Flush any remaining clause at end of file
    flush_current_clause()

    return clauses
