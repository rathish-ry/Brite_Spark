import argparse
import sys
from pathlib import Path
from typing import List
from src.models import Clause
from src.parser import parse_markdown_policy
from src.amendment_parser import parse_amendment_policy
from src.cli import list_clauses, show_clause, run_grounded_assistant
from src.interactive import run_interactive_session


def load_combined_corpus(
    policy_path: Path = Path("data/policy.md"),
    amendment_path: Path = Path("data/Amendment No. 2026-01.md"),
) -> List[Clause]:
    """
    Loads and parses original policy manual and Day 2 amendment into a combined clause list.
    """
    clauses: List[Clause] = []

    if policy_path.exists():
        with open(policy_path, "r", encoding="utf-8") as f:
            content = f.read()
        clauses.extend(parse_markdown_policy(content, source_file=str(policy_path)))

    if amendment_path.exists():
        with open(amendment_path, "r", encoding="utf-8") as f:
            amd_content = f.read()
        clauses.extend(parse_amendment_policy(amd_content, source_file=str(amendment_path)))

    if not clauses:
        raise FileNotFoundError(f"No policy or amendment files found at: {policy_path}")

    return clauses


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
        help="Display full details and original text for a specific clause (e.g. C003 or A2026-01-C01)",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        metavar="QUESTION",
        help="Run single grounded policy query against the manual",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Launch interactive caseworker CLI session",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of top retrieved clauses to consider (default: 5)",
    )

    args = parser.parse_args()
    policy_path = Path(args.policy_path)
    amendment_path = policy_path.parent / "Amendment No. 2026-01.md"

    try:
        clauses = load_combined_corpus(policy_path, amendment_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
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
        output = run_grounded_assistant(args.query, clauses, top_k=args.top_k)
        print(output)
    else:
        run_interactive_session(clauses, policy_path=str(policy_path))


if __name__ == "__main__":
    main()