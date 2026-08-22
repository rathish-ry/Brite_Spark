import argparse
import sys
from pathlib import Path
from src.parser import parse_markdown_policy
from src.cli import list_clauses, show_clause


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
    else:
        print("========================================")
        print("       GROUNDED POLICY ASSISTANT        ")
        print("========================================")
        print(f"Loaded policy manual: {policy_path}")
        print(f"Extracted Clauses: {len(clauses)}\n")
        print("Use --list-clauses (-l) to inspect all clause IDs.")
        print("Use --show-clause CLAUSE_ID (-s C001) to view clause details.")


if __name__ == "__main__":
    main()