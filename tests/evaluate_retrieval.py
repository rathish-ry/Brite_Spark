import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parser import parse_markdown_policy
from src.retriever import BM25Retriever


def evaluate_retrieval(policy_path: str = "data/policy.md", eval_path: str = "tests/retrieval_eval.json"):
    policy_file = Path(policy_path)
    eval_file = Path(eval_path)

    if not policy_file.exists():
        print(f"ERROR: Policy manual not found at {policy_file}", file=sys.stderr)
        sys.exit(1)

    if not eval_file.exists():
        print(f"ERROR: Evaluation file not found at {eval_file}", file=sys.stderr)
        sys.exit(1)

    with open(policy_file, "r", encoding="utf-8") as f:
        policy_content = f.read()

    clauses = parse_markdown_policy(policy_content, source_file=str(policy_file))
    retriever = BM25Retriever(clauses)

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    total_cases = len(eval_cases)

    print("========================================")
    print("      RETRIEVAL EVALUATION REPORT       ")
    print("========================================\n")

    for case in eval_cases:
        case_id = case["id"]
        question = case["question"]
        expected_ids = set(case["expected_clause_ids"])

        results = retriever.retrieve(question, top_k=5)
        retrieved_ids = [res.clause.id for res in results]

        top1_found = bool(set(retrieved_ids[:1]) & expected_ids)
        top3_found = bool(set(retrieved_ids[:3]) & expected_ids)
        top5_found = bool(set(retrieved_ids[:5]) & expected_ids)

        if top1_found:
            top1_hits += 1
        if top3_found:
            top3_hits += 1
        if top5_found:
            top5_hits += 1

        status_str = "PASS" if top1_found else ("PASS (Top-3/5)" if top5_found else "FAIL")
        print(f"[{case_id:02d}] Status: {status_str}")
        print(f"     Question: \"{question}\"")
        print(f"     Expected: {sorted(list(expected_ids))}")
        print(f"     Retrieved (Top-5): {retrieved_ids}")
        if not top1_found:
            print(f"     Note: Top-1 match missed. Expected {expected_ids}, got {retrieved_ids[:1]}")
        print()

    top1_acc = (top1_hits / total_cases) * 100 if total_cases > 0 else 0
    top3_acc = (top3_hits / total_cases) * 100 if total_cases > 0 else 0
    top5_acc = (top5_hits / total_cases) * 100 if total_cases > 0 else 0

    print("========================================")
    print("           SUMMARY METRICS              ")
    print("========================================")
    print(f"Total Test Cases : {total_cases}")
    print(f"Top-1 Accuracy   : {top1_hits}/{total_cases} ({top1_acc:.1f}%)")
    print(f"Top-3 Accuracy   : {top3_hits}/{total_cases} ({top3_acc:.1f}%)")
    print(f"Top-5 Accuracy   : {top5_hits}/{total_cases} ({top5_acc:.1f}%)")
    print("========================================")


if __name__ == "__main__":
    evaluate_retrieval()
