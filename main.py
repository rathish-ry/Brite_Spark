import argparse
import sys
from pathlib import Path
from src.parser import parse_markdown_policy


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

    args = parser.parse_args()
    policy_path = Path(args.policy_path)

    print("========================================")
    print("       GROUNDED POLICY ASSISTANT        ")
    print("========================================")
    print(f"Loading policy manual from: {policy_path}")

    try:
        content = load_policy(policy_path)
        lines = content.splitlines()
        clauses = parse_markdown_policy(content, source_file=str(policy_path))
        
        print(f"SUCCESS: Policy loaded and parsed successfully.")
        print(f"Total Lines: {len(lines)}")
        print(f"Total Characters: {len(content)}")
        print(f"Extracted Clauses: {len(clauses)}\n")
        
        for clause in clauses:
            print(clause.summary())

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("\nPlease ensure the policy manual is placed at 'data/policy.md' or specify using --policy-path.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error loading policy: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()