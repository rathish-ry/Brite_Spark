# Brite Spark 2026 — The Grounded Answer

A production-grade, zero-external-dependency command-line RAG (Retrieval-Augmented Generation) policy assistant built for **Brite Spark 2026 — Problem 1: The Grounded Answer**.

The assistant answers policy questions strictly using a supplied Markdown policy manual (`data/policy.md`), provides exact clause-level citations and source provenance (including line numbers and verbatim text), and explicitly refuses to answer when policy evidence is incomplete, ambiguous, missing, or contradictory.

---

## 🏗 Architecture Overview

```text
               ┌──────────────────────────────┐
               │    Caseworker Policy Query   │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │  Markdown Policy Manual      │
               │  Parser (Line Provenance)    │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │  Okapi BM25 Lexical Indexer  │
               │  & Retrieval Engine          │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │        EVIDENCE GATE         │
               │ ├── Confidence Threshold     │
               │ ├── Term Coverage            │
               │ ├── Rule-Language Audit      │
               │ ├── Apparent Gap Detector    │
               │ └── Contradiction Detector   │
               └──────────────┬───────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
    [ANSWERABLE]                     [REFUSAL / CONFLICT]
               │                             │
               ▼                             ▼
 ┌───────────────────────────┐ ┌───────────────────────────┐
 │ Grounded Generator        │ │ Refusal Response Builder  │
 │ ├── Fact Extraction       │ │ ├── Reason Specification  │
 │ └── Citation Binding      │ │ └── Supervisor Escalation │
 └─────────────┬─────────────┘ └─────────────┬─────────────┘
               │                             │
               ▼                             │
 ┌───────────────────────────┐               │
 │ Citation Validator        │               │
 │ └── Strict Citation Check │               │
 └─────────────┬─────────────┘               │
               │                             │
               └──────────────┬──────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │     CLI Output Presentation  │
               └──────────────────────────────┘
```

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.10 or higher

### Environment Setup
1. Clone or navigate to the repository directory:
   ```bash
   cd Brite_Spark
   ```
2. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Policy Manual Placement
Ensure the target Markdown policy manual is located at `data/policy.md`.

---

## 💻 CLI Usage Guide

### 1. Interactive Caseworker Mode (Default)
Launch the interactive caseworker workspace supporting live query loops, clause inspections, and evaluation runs:
```bash
python main.py
# or explicit flag:
python main.py --interactive
```

**Interactive Session Commands**:
- `/help` — View command options
- `/list` — List all extracted clause IDs and headings
- `/show <clause_id>` — View full clause text and source line numbers (e.g. `/show C003`)
- `/eval` — Execute the 10-question evaluation benchmark directly inside the session
- `/history` — View queries asked during the current session
- `/exit` — Exit caseworker CLI session

### 2. Single Question Execution
Query a specific policy question directly from the command line:
```bash
python main.py --query "How long do I have to appeal?"
# or short option:
python main.py -q "How long do I have to appeal?"
```

### 3. Policy Inspection Commands
- **List All Clauses**:
  ```bash
  python main.py --list-clauses
  # or short option:
  python main.py -l
  ```
- **Show Clause Provenance & Details**:
  ```bash
  python main.py --show-clause C003
  # or short option:
  python main.py -s C003
  ```

---

## 🧪 Evaluation & Audit Suites

### 1. Final Compliance Verification Audit
Executes a 10-point end-to-end challenge audit covering parser provenance, BM25 retrieval, evidence gate, refusal escalation, gap detection, contradiction detection, citation binding, performance benchmarks, and documentation completeness:
```bash
python scripts/final_verification.py
```

### 2. Submission Packaging Verification
Runs full submission verification (artifact checks, unit test suite, 10-question benchmark, system audit):
```bash
python scripts/package_submission.py
```

### 3. Ten-Question Benchmark Suite
Evaluates the system across 10 challenge queries spanning normal answerable queries (5), apparent gaps (2), contradiction (1), ambiguous query (1), and irrelevant query (1):
```bash
python tests/evaluate.py
```

### 4. Citation Accuracy Evaluation
Verifies presence, existence, support, and strictness of citations across all answerable queries:
```bash
python tests/evaluate_citations.py
```

### 5. Performance & Memory Benchmarking
Profiles parsing, indexing, retrieval, evidence gate, and end-to-end latencies alongside net RAM usage:
```bash
python tests/benchmark_performance.py
```

### 6. System Integrity Audit
Audits file structure, Python AST syntax, parsing integrity, evaluation dataset JSON, and code hygiene:
```bash
python tests/audit_system.py
```

### 7. Unit Test Suite
Runs all 49 automated unit tests:
```bash
python -m unittest discover -s tests
```

---

## 📊 Benchmark Results

| Metric / Audit Suite | Result | Target Threshold | Status |
| :--- | :--- | :--- | :--- |
| **Unit Test Suite** | 49 / 49 Passed | 100% Pass | **PASS** |
| **10-Question Challenge Benchmark** | 10 / 10 Passed | 100% Pass | **PASS** |
| **Citation Accuracy Rate** | 100.0% | 100% Accuracy | **PASS** |
| **End-to-End Query Latency** | 12.15 ms | < 500 ms | **PASS** |
| **Net RAM Memory Usage** | 0.29 MB | < 100 MB | **PASS** |
| **System Integrity Audit** | Operational | Zero Errors | **PASS** |
| **Final Compliance Audit** | 100% Compliant | Ready for Production | **PASS** |

---

## 📁 Repository Directory Structure

```text
Brite_Spark/
├── data/
│   └── policy.md                     # Markdown Policy Manual Input
├── scripts/
│   ├── final_verification.py         # 10-Point Challenge Compliance Audit Script
│   └── package_submission.py         # Submission Packaging Verification Script
├── src/
│   ├── __init__.py                   # Core Package Initializer
│   ├── citations.py                  # Strict Citation Validator & Sources Block Formatter
│   ├── cli.py                        # Inspection CLI & Grounded Pipeline Orchestration
│   ├── config.py                     # Centralized Safety Configuration & Thresholds
│   ├── contradiction.py              # Policy Contradiction & Numerical Conflict Detector
│   ├── evidence_gate.py              # Safety Validation Gate Engine
│   ├── gap_detector.py               # Apparent Policy Gap Detector
│   ├── generator.py                  # Grounded Answer Synthesizer & Citation Binding
│   ├── interactive.py                # Interactive Caseworker CLI Workspace
│   ├── models.py                     # Core Data Models (Clause, EvidenceDecision, etc.)
│   ├── parser.py                     # Line-Preserving Regex Markdown Parser
│   ├── refusal.py                    # Structured Refusal Engine & Escalation Builder
│   └── retriever.py                  # Okapi BM25 Lexical Retriever & Indexer
├── tests/
│   ├── .gitkeep                      # Git Directory Anchor
│   ├── audit_system.py               # System Integrity & Health Audit Script
│   ├── benchmark_performance.py      # Latency & Memory Footprint Profiling Script
│   ├── evaluate.py                   # 10-Question Challenge Benchmark Runner
│   ├── evaluate_citations.py         # Citation Accuracy Evaluator Script
│   ├── evaluate_retrieval.py         # Retrieval Metrics (Hit@1, Hit@3, Hit@5) Runner
│   ├── evaluation.json               # 10-Question Challenge Benchmark Dataset
│   ├── retrieval_eval.json           # Retrieval Evaluation Ground-Truth Dataset
│   ├── test_audit.py                 # System Audit Unit Tests
│   ├── test_citation_eval.py         # Citation Evaluator Unit Tests
│   ├── test_citations.py            # Citation Validation Unit Tests
│   ├── test_cli.py                  # Inspection CLI Unit Tests
│   ├── test_contradiction.py        # Contradiction Detection Unit Tests
│   ├── test_evidence_gate.py         # Evidence Gate Unit Tests
│   ├── test_final_verification.py   # Final Verification Unit Tests
│   ├── test_gap_detector.py         # Apparent Gap Detection Unit Tests
│   ├── test_generator.py            # Answer Generator Unit Tests
│   ├── test_interactive.py          # Interactive CLI Unit Tests
│   ├── test_package.py              # Submission Packaging Unit Tests
│   ├── test_parser.py               # Markdown Parser Unit Tests
│   ├── test_performance.py          # Performance Latency Unit Tests
│   ├── test_refusal.py              # Refusal Response Unit Tests
│   ├── test_retriever.py            # BM25 Retriever Unit Tests
│   └── test_workflow.py             # End-to-End Workflow Integration Unit Tests
├── .gitignore                        # Git File Exclusion Rules
├── main.py                           # Application CLI Entrypoint
├── requirements.txt                  # Python Project Dependencies
├── README.md                         # Project Guide & Documentation
├── DECISIONS.md                      # Architecture & Design Decisions Log (Phases 1-20)
└── AI-USAGE.md                       # Developer Execution & Tool Reference Log (Phases 1-20)
```
