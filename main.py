import argparse
import sys
from pathlib import Path
from src.parser import parse_markdown_policy
from src.cli import list_clauses, show_clause
from src.retriever import BM25Retriever
from src.evidence_gate import EvidenceGate
from src.models import EvidenceStatus
from src.refusal import build_refusal_response


def load_policy(file_path: Path) -> str:
    """
    Loads the policy manual from the given file path.
    Raises FileNotFoundError if the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Policy manual not found at path: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    parser = argparse.ArgumentParser(
        description="Brite Spark 2026 — Grounded Answer Policy Assistant"
    )
    parser.add_argument(
        "--policy-path",
        type=str,
        default="data/policy.md",
        help="Path to the policy manual Markdown file (default: data/policy.md)",
    )
    parser.add_argument(
        "--list-clauses",
        "-l",
        action="store_true",
        help="List all extracted policy clause IDs, sections, and headings",
    )
    parser.add_argument(
        "--show-clause",
        "-s",
        type=str,
        metavar="CLAUSE_ID",
        help="Display full details and original text for a specific clause (e.g. C003)",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        metavar="QUESTION",
        help="Evaluate question safety and search policy clauses",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of top retrieved clauses to return (default: 5)",
    )

    args = parser.parse_args()
    policy_path = Path(args.policy_path)

    try:
        content = load_policy(policy_path)
        clauses = parse_markdown_policy(content, source_file=str(policy_path))
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nPlease ensure the policy manual is placed at 'data/policy.md' or specify using --policy-path.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error loading policy: {e}", file=sys.stderr)
        sys.exit(1)

    if args.list_clauses:
        list_clauses(clauses)
    elif args.show_clause:
        found = show_clause(clauses, args.show_clause)
        if not found:
            sys.exit(1)
    elif args.query:
        retriever = BM25Retriever(clauses)
        results = retriever.retrieve(args.query, top_k=args.top_k)

        gate = EvidenceGate()
        decision = gate.evaluate(args.query, results)

        if decision.status != EvidenceStatus.ANSWERABLE:
            refusal = build_refusal_response(
                question=args.query,
                reason=decision.reason,
                status=decision.status.value,
                conflicting_clauses=decision.supported_clauses if decision.status == EvidenceStatus.CONFLICT else [],
            )
            print(refusal.format_cli())
        else:
            print("========================================")
            print("       GROUNDED POLICY ASSISTANT        ")
            print("========================================")
            print(f"Question:\n> {args.query}\n")
            print("EVIDENCE GATE: ANSWERABLE")
            print(f"Confidence Score: {decision.top_score:.4f}")
            print(f"Term Coverage: {decision.term_coverage:.2%}\n")
            print("Retrieved Grounding Evidence:")
            for idx, res in enumerate(results, start=1):
                c = res.clause
                print(f"Rank {idx}: [{c.id}] {c.section} — {c.heading}")
                print(f"Source: {c.source_file} lines {c.source_start}-{c.source_end}")
                print(f"Text Snippet:\n  {c.text[:200]}...\n")
            print("STATUS: ANSWERABLE")
    else:
        print("========================================")
        print("       GROUNDED POLICY ASSISTANT        ")
        print("========================================")
        print(f"Loaded policy manual: {policy_path}")
        print(f"Extracted Clauses: {len(clauses)}\n")
        print("Use --query \"QUESTION\" (-q) to test assistant.")
        print("Use --list-clauses (-l) to inspect all clause IDs.")
        print("Use --show-clause CLAUSE_ID (-s C001) to view clause details.")


if __name__ == "__main__":
    main()