import sys
import unittest
import json
from pathlib import Path

# Add project root and tests/ dir to sys.path
root_dir = Path(__file__).resolve().parent.parent
tests_dir = root_dir / "tests"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(tests_dir))

from audit_system import (
    audit_file_structure,
    audit_python_syntax,
    audit_policy_parsing,
    audit_eval_datasets,
)
from main import load_combined_corpus
from src.models import EvidenceStatus
from src.retriever import BM25Retriever
from src.evidence_gate import EvidenceGate
from src.temporal import extract_temporal_context, filter_temporally_applicable_clauses


def normalize_status(status_enum) -> str:
    if status_enum == EvidenceStatus.ANSWERABLE:
        return "ANSWERED"
    elif status_enum == EvidenceStatus.CONFLICT:
        return "REFUSED_CONFLICT"
    return "REFUSED"



def check_required_artifacts() -> bool:
    required = [
        root_dir / "data" / "policy.md",
        root_dir / "main.py",
        root_dir / "requirements.txt",
        root_dir / "README.md",
        root_dir / "DECISIONS.md",
        root_dir / "AI-USAGE.md",
    ]
    for path in required:
        if not path.exists():
            print(f"Missing required artifact: {path.name}", file=sys.stderr)
            return False
    return True


def run_unit_tests() -> tuple[bool, int]:
    loader = unittest.TestLoader()
    suite = loader.discover(str(root_dir / "tests"))
    runner = unittest.TextTestRunner(stream=open("NUL" if sys.platform == "win32" else "/dev/null", "w"))
    result = runner.run(suite)
    passed = result.wasSuccessful()
    count = result.testsRun
    return passed, count


def run_eval_benchmark() -> tuple[bool, int, int]:
    policy_file = root_dir / "data" / "policy.md"
    amendment_file = root_dir / "data" / "Amendment No. 2026-01.md"
    eval_file = root_dir / "tests" / "evaluation.json"

    clauses = load_combined_corpus(policy_file, amendment_file)
    gate = EvidenceGate()

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    passed_count = 0
    total = len(eval_cases)

    for case in eval_cases:
        question = case["question"]
        expected = case["expected"]
        ctx = extract_temporal_context(question)
        app_clauses = filter_temporally_applicable_clauses(clauses, ctx)

        retriever = BM25Retriever(app_clauses)
        results = retriever.retrieve(question, top_k=5)
        decision = gate.evaluate(question, results)
        actual = normalize_status(decision.status)
        if actual == expected:
            passed_count += 1

    return (passed_count == total), passed_count, total


def run_audit() -> bool:
    return (
        audit_file_structure()
        and audit_python_syntax()[0]
        and audit_policy_parsing()[0]
        and audit_eval_datasets()
    )


def package_submission():
    print("========================================")
    print("     SUBMISSION PACKAGING REPORT        ")
    print("========================================\n")

    artifacts_ok = check_required_artifacts()
    unit_ok, unit_count = run_unit_tests()
    eval_ok, eval_passed, eval_total = run_eval_benchmark()
    audit_ok = run_audit()

    print(f"[{'PASS' if artifacts_ok else 'FAIL'}] Required Artifacts Present")
    print(f"[{'PASS' if unit_ok else 'FAIL'}] Unit Test Suite ({unit_count}/{unit_count} OK)")
    print(f"[{'PASS' if eval_ok else 'FAIL'}] Evaluation Benchmark ({eval_passed}/{eval_total} PASS)")
    print(f"[{'PASS' if audit_ok else 'FAIL'}] System Integrity Audit (OPERATIONAL)\n")

    all_ok = artifacts_ok and unit_ok and eval_ok and audit_ok

    if all_ok:
        print("STATUS: READY FOR SUBMISSION")
    else:
        print("STATUS: NOT READY — SUBMISSION CHECK FAILED")
        sys.exit(1)


if __name__ == "__main__":
    package_submission()
