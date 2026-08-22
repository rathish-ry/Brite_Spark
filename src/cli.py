import sys
from typing import List, Optional
from src.models import Clause


def list_clauses(clauses: List[Clause]) -> None:
    """
    Prints a concise list of all parsed policy clauses.
    Format: [C001] Section — Heading
    """
    if not clauses:
        print("No clauses found in the policy manual.")
        return

    print("========================================")
    print("           POLICY CLAUSES LIST          ")
    print("========================================")
    for clause in clauses:
        print(f"[{clause.id}] {clause.section} — {clause.heading}")


def show_clause(clauses: List[Clause], clause_id: str) -> bool:
    """
    Finds and displays full details and exact text of a specific clause.
    Returns True if clause was found, False otherwise.
    """
    target_id = clause_id.strip().upper()
    clause: Optional[Clause] = None

    for c in clauses:
        if c.id.upper() == target_id:
            clause = c
            break

    if not clause:
        print(f"ERROR: Clause '{clause_id}' not found.", file=sys.stderr)
        return False

    print("========================================")
    print(f"[{clause.id}]")
    print(f"Section: {clause.section}")
    print(f"Heading: {clause.heading}")
    print(f"Source: {clause.source_file} lines {clause.source_start}-{clause.source_end}")
    print("========================================\n")
    print(clause.text)
    return True
