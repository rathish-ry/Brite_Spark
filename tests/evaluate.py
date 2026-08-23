import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import load_combined_corpus
from src.retriever import BM25Retriever
from src.evidence_gate import EvidenceGate
from src.models import EvidenceStatus
from src.temporal import extract_temporal_context, filter_temporally_applicable_clauses


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
    gate = EvidenceGate()

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    passed_count = 0
    failed_count = 0
    failures = []

    print("Brite Spark Day 2 Evaluation Benchmark Suite\n")

    for case in eval_cases:
        case_id = case["id"]
        question = case["question"]
        expected = case["expected"]

        ctx = extract_temporal_context(question)
        app_clauses = filter_temporally_applicable_clauses(clauses, ctx)

        retriever = BM25Retriever(app_clauses)
        results = retriever.retrieve(question, top_k=5)
        decision = gate.evaluate(question, results)
        actual = normalize_status(decision.status)

        is_pass = (actual == expected)

        if is_pass:
            passed_count += 1
            print(f"{case_id:02d} PASS")
        else:
            failed_count += 1
            print(f"{case_id:02d} FAIL")
            failures.append({
                "id": case_id,
                "question": question,
                "expected": expected,
                "actual": actual,
                "reason": decision.reason,
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
            print(f"  Expected : {fail['expected']}")
            print(f"  Actual   : {fail['actual']}")
            print(f"  Reason   : {fail['reason']}\n")


if __name__ == "__main__":
    run_evaluation()
