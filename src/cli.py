import sys
from typing import List, Optional
from src.models import Clause, EvidenceStatus
from src.retriever import BM25Retriever
from src.evidence_gate import EvidenceGate
from src.generator import GroundedGenerator
from src.refusal import build_refusal_response


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


def run_grounded_assistant(query: str, clauses: List[Clause], top_k: int = 5) -> str:
    """
    Executes the end-to-end grounded assistant pipeline:
    Question -> Retriever -> Evidence Gate (with Contradiction & Gap checks) -> Generator -> Citation Validation -> CLI Output.
    """
    retriever = BM25Retriever(clauses)
    results = retriever.retrieve(query, top_k=top_k)

    gate = EvidenceGate()
    decision = gate.evaluate(query, results)

    if decision.status != EvidenceStatus.ANSWERABLE:
        refusal = build_refusal_response(
            question=query,
            reason=decision.reason,
            status=decision.status.value,
            conflicting_clauses=decision.supported_clauses if decision.status == EvidenceStatus.CONFLICT else [],
        )
        return refusal.format_cli()

    generator = GroundedGenerator()
    answer = generator.generate(query, decision.supported_clauses)
    return answer.format_cli()
