import argparse
import sys
from pathlib import Path
from src.parser import parse_markdown_policy
from src.cli import list_clauses, show_clause, run_grounded_assistant
from src.interactive import run_interactive_session


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
        output = run_grounded_assistant(args.query, clauses, top_k=args.top_k)
        print(output)
    else:
        run_interactive_session(clauses, policy_path=str(policy_path))


if __name__ == "__main__":
    main()