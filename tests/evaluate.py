import json
import re
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import load_combined_corpus
from src.cli import run_grounded_assistant
from src.citations import extract_citation_tags
from src.models import EvidenceStatus


def normalize_status(status_enum: EvidenceStatus) -> str:
    """
    Normalizes internal EvidenceStatus enum to evaluation contract status.
    """
    if status_enum == EvidenceStatus.ANSWERABLE:
        return "ANSWERED"
    elif status_enum == EvidenceStatus.CONFLICT:
        return "REFUSED_CONFLICT"
    else:
        return "REFUSED"


def parse_cli_output(output: str) -> tuple[str, str, list[str]]:
    """
    Parses CLI output to extract actual_status, actual_answer, and actual_citations.
    """
    status = "REFUSED"
    if "STATUS: ANSWERED" in output:
        status = "ANSWERED"
    elif "STATUS: REFUSED_CONFLICT" in output:
        status = "REFUSED_CONFLICT"

    answer_match = re.search(r"ANSWER\n\n(.*?)(?=\n\nSOURCES|\n\nSTATUS)", output, re.DOTALL)
    actual_answer = answer_match.group(1).strip() if answer_match else ""
    actual_citations = extract_citation_tags(output)

    return status, actual_answer, actual_citations


def run_evaluation(
    policy_path: str = "data/policy.md",
    amendment_path: str = "data/Amendment No. 2026-01.md",
    eval_path: str = "tests/evaluation.json",
):
    policy_file = Path(policy_path)
    amendment_file = Path(amendment_path)
    eval_file = Path(eval_path)

    if not policy_file.exists():
        print(f"ERROR: Policy file not found at {policy_file}", file=sys.stderr)
        sys.exit(1)

    if not eval_file.exists():
        print(f"ERROR: Evaluation file not found at {eval_file}", file=sys.stderr)
        sys.exit(1)

    clauses = load_combined_corpus(policy_file, amendment_file)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    total = len(eval_cases)
    print(f"Brite Spark Evaluation Benchmark Suite — {total} Questions\n")

    passed_count = 0
    failed_count = 0
    failures = []

    for case in eval_cases:
        case_id = case["id"]
        question = case["question"]
        expected_status = case["expected"]
        expected_contains = case.get("expected_answer_contains", "")
        expected_cits = case.get("expected_citations", [])

        output = run_grounded_assistant(question, clauses)
        actual_status, actual_answer, actual_citations = parse_cli_output(output)

        is_status_pass = (actual_status == expected_status)
        is_answer_pass = True
        is_cit_pass = True

        if expected_status == "ANSWERED":
            if expected_contains and expected_contains.lower() not in actual_answer.lower():
                is_answer_pass = False

            if actual_answer.startswith("**1.1** In §") or actual_answer.startswith("**2.1** In §"):
                is_answer_pass = False

            for cit in expected_cits:
                if cit not in actual_citations:
                    is_cit_pass = False

        is_pass = is_status_pass and is_answer_pass and is_cit_pass

        if is_pass:
            passed_count += 1
            print(f"{case_id:02d} PASS")
        else:
            failed_count += 1
            print(f"{case_id:02d} FAIL")
            failures.append({
                "id": case_id,
                "question": question,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_contains": expected_contains,
                "actual_answer": actual_answer,
                "expected_citations": expected_cits,
                "actual_citations": actual_citations,
            })

    total = len(eval_cases)
    print("\n--------------------------------")
    print(f"Passed: {passed_count}/{total}")
    print(f"Failed: {failed_count}/{total}")
    print("--------------------------------")

    if failures:
        print("\nFAILURE DETAILS:\n")
        for fail in failures:
            print(f"Question {fail['id']:02d}: \"{fail['question']}\"")
            print(f"  Expected Status   : {fail['expected_status']}")
            print(f"  Actual Status     : {fail['actual_status']}")
            print(f"  Expected Contains : {fail['expected_contains']}")
            print(f"  Actual Answer     : {fail['actual_answer']}")
            print(f"  Expected Citations: {fail['expected_citations']}")
            print(f"  Actual Citations  : {fail['actual_citations']}\n")


if __name__ == "__main__":
    run_evaluation()
