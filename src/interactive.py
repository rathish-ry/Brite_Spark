import sys
from typing import List
from src.models import Clause
from src.cli import list_clauses, show_clause, run_grounded_assistant


def print_help() -> None:
    print("\nAvailable Commands:")
    print("  /help            Show this help message")
    print("  /list            List all extracted policy clause IDs and headings")
    print("  /show <id>       View full text and source provenance of a clause (e.g. /show C003)")
    print("  /mode [type]     View or switch engine mode: /mode offline or /mode llm (default: auto)")
    print("  /eval            Run the evaluation benchmark suite")
    print("  /history         Show queries asked during this CLI session")
    print("  /exit or exit    Exit the caseworker CLI session\n")


def run_interactive_session(clauses: List[Clause], policy_path: str = "data/policy.md", initial_mode: str = "auto") -> None:
    """
    Launches an interactive command-line session tailored for caseworkers handling live policy inquiries.
    """
    current_mode = initial_mode
    print("========================================")
    print("   GROUNDED POLICY ASSISTANT — CASEWORKER CLI")
    print("========================================")
    print(f"Loaded Policy: {policy_path} ({len(clauses)} clauses)")
    print(f"Active Mode:   {current_mode.upper()} (type /mode to switch)")
    print("Type your question or /help for options.")

    session_history = []

    while True:
        try:
            print("\nQuestion:")
            user_input = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Caseworker CLI. Goodbye!")
            break

        if not user_input:
            continue

        cmd_lower = user_input.lower()

        if cmd_lower in ("/exit", "exit", "quit", "q"):
            print("\nExiting Caseworker CLI. Goodbye!")
            break

        elif cmd_lower in ("/help", "help"):
            print_help()

        elif cmd_lower in ("/list", "list"):
            list_clauses(clauses)

        elif cmd_lower.startswith("/show"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print("Usage: /show <CLAUSE_ID> (e.g. /show C003)")
            else:
                show_clause(clauses, parts[1])

        elif cmd_lower.startswith("/mode"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                target_mode = parts[1].strip().lower()
                if target_mode in ("offline", "llm", "auto"):
                    current_mode = target_mode
                    print(f"\n[MODE] Switched engine mode to: {current_mode.upper()}")
                else:
                    print("\nUsage: /mode offline | /mode llm | /mode auto")
            else:
                print(f"\nCurrent engine mode is: {current_mode.upper()}")
                print("To switch, type: /mode offline  OR  /mode llm")

        elif cmd_lower in ("/eval", "eval"):
            print("\nRunning Evaluation Benchmark Suite...\n")
            try:
                from tests.evaluate import run_evaluation
                run_evaluation(policy_path=policy_path)
            except Exception as e:
                print(f"ERROR running evaluation: {e}", file=sys.stderr)

        elif cmd_lower in ("/history", "history"):
            if not session_history:
                print("\nNo queries asked yet in this session.")
            else:
                print("\nSession Query History:")
                for idx, entry in enumerate(session_history, start=1):
                    print(f"  {idx}. \"{entry['question']}\"")

        else:
            output = run_grounded_assistant(user_input, clauses, mode=current_mode)
            print(f"\n{output}")
            session_history.append({"question": user_input})
