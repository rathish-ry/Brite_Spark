import json
import sys
import time
import tracemalloc
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parser import parse_markdown_policy
from src.retriever import BM25Retriever
from src.evidence_gate import EvidenceGate
from src.cli import run_grounded_assistant


def run_performance_benchmark(policy_path: str = "data/policy.md", eval_path: str = "tests/evaluation.json"):
    policy_file = Path(policy_path)
    eval_file = Path(eval_path)

    if not policy_file.exists() or not eval_file.exists():
        print(f"ERROR: Missing input file(s) ({policy_file}, {eval_file})", file=sys.stderr)
        sys.exit(1)

    file_size_kb = policy_file.stat().st_size / 1024.0

    # Start memory tracing
    tracemalloc.start()
    mem_initial_bytes, _ = tracemalloc.get_traced_memory()
    mem_initial_mb = mem_initial_bytes / (1024.0 * 1024.0)

    # 1. Parsing & Indexing Benchmark
    t0 = time.perf_counter()
    with open(policy_file, "r", encoding="utf-8") as f:
        policy_content = f.read()

    clauses = parse_markdown_policy(policy_content, source_file=str(policy_file))
    retriever = BM25Retriever(clauses)
    t1 = time.perf_counter()

    indexing_time_ms = (t1 - t0) * 1000.0

    _, mem_post_index_bytes = tracemalloc.get_traced_memory()
    mem_post_index_mb = mem_post_index_bytes / (1024.0 * 1024.0)
    net_memory_mb = max(0.01, mem_post_index_mb - mem_initial_mb)

    # Load query evaluation cases
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    questions = [case["question"] for case in eval_cases]
    gate = EvidenceGate()

    retrieval_latencies = []
    gate_latencies = []
    e2e_latencies = []

    # Benchmark query execution across all benchmark questions
    for q in questions:
        # Retrieval Latency
        t_start = time.perf_counter()
        results = retriever.retrieve(q, top_k=5)
        t_ret = time.perf_counter()
        retrieval_latencies.append((t_ret - t_start) * 1000.0)

        # Evidence Gate Latency
        t_gate_start = time.perf_counter()
        gate.evaluate(q, results)
        t_gate_end = time.perf_counter()
        gate_latencies.append((t_gate_end - t_gate_start) * 1000.0)

        # End-to-End Latency
        t_e2e_start = time.perf_counter()
        run_grounded_assistant(q, clauses)
        t_e2e_end = time.perf_counter()
        e2e_latencies.append((t_e2e_end - t_e2e_start) * 1000.0)

    tracemalloc.stop()

    avg_retrieval_ms = sum(retrieval_latencies) / len(retrieval_latencies)
    avg_gate_ms = sum(gate_latencies) / len(gate_latencies)
    avg_e2e_ms = sum(e2e_latencies) / len(e2e_latencies)

    status_pass = (avg_e2e_ms < 500.0) and (net_memory_mb < 100.0)
    status_str = "PASS (Target: < 500ms latency, < 100MB RAM)" if status_pass else "FAIL (Exceeded targets)"

    print("========================================")
    print("    PERFORMANCE BENCHMARK REPORT        ")
    print("========================================\n")
    print(f"Policy Manual Clause Count: {len(clauses)} clauses")
    print(f"Total File Size: {file_size_kb:.1f} KB\n")
    print("LATENCY BENCHMARKS:")
    print(f"- Parsing & Indexing Time: {indexing_time_ms:.2f} ms")
    print(f"- Average Retrieval Latency: {avg_retrieval_ms:.2f} ms")
    print(f"- Average Evidence Gate Latency: {avg_gate_ms:.2f} ms")
    print(f"- Average End-to-End Query Latency: {avg_e2e_ms:.2f} ms\n")
    print("MEMORY FOOTPRINT:")
    print(f"- Initial Memory: {mem_initial_mb:.2f} MB")
    print(f"- Post-Indexing Memory: {mem_post_index_mb:.2f} MB")
    print(f"- Net Memory Usage: {net_memory_mb:.2f} MB\n")
    print(f"STATUS: {status_str}")


if __name__ == "__main__":
    run_performance_benchmark()
