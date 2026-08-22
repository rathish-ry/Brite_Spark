# AI Usage Log

## Overview
This document tracks tool usage, documentation assistance, and reference research throughout the development of the Grounded Policy Assistant.

## Phase 1 — Project Setup and Policy Loading
- **Tools & References Used**: Python standard library documentation (`pathlib`, `argparse`), Markdown specification guides, and Git version control standards.
- **Developer Execution**: Initialized repository structure (`data/`, `src/`, `tests/`), created project scaffold, written file loading logic in `main.py`, structured sample policy manual `data/policy.md`, and authored project documentation (`README.md`, `DECISIONS.md`).

## Phase 2 — Policy Clause Extraction
- **Tools & References Used**: Python `re` module regex documentation, Python `dataclasses` reference guide, and `unittest` framework documentation.
- **Developer Execution**: Designed `Clause` data model (`src/models.py`), implemented line-preserving Markdown parser (`src/parser.py`), authored unit test suite (`tests/test_parser.py`), and verified parsing output.

## Phase 3 — Policy Inspection CLI
- **Tools & References Used**: Python `argparse` documentation, `sys` stderr redirection patterns for testing CLI outputs.
- **Developer Execution**: Implemented CLI inspection module (`src/cli.py`), wired `--list-clauses` and `--show-clause` flags in `main.py`, created unit tests (`tests/test_cli.py`), and verified CLI outputs.

## Phase 4 — Basic Retrieval
- **Tools & References Used**: Okapi BM25 ranking algorithm documentation, Information Retrieval literature (IDF formulas), Python math module documentation.
- **Developer Execution**: Built `BM25Retriever` class (`src/retriever.py`), implemented multi-field indexing, tokenization with stop-word filtering and stemming, wired `--query` / `-q` CLI flag in `main.py`, authored test suite (`tests/test_retriever.py`), and verified retrieval scoring.

## Phase 5 — Retrieval Evaluation
- **Tools & References Used**: Information Retrieval metric standards (Hit@1, Hit@3, Hit@5), JSON dataset standards.
- **Developer Execution**: Authored evaluation dataset (`tests/retrieval_eval.json`), built evaluation runner script (`tests/evaluate_retrieval.py`), calculated Top-1, Top-3, and Top-5 retrieval accuracy, and logged honest metric reporting.

## Phase 6 — Evidence Gate
- **Tools & References Used**: Safety alignment standards, rule-based gate design patterns, enum status models.
- **Developer Execution**: Designed centralized configuration (`src/config.py`), implemented `EvidenceGate` (`src/evidence_gate.py`) returning `EvidenceDecision`, added term-coverage and directive-language validation, authored unit tests (`tests/test_evidence_gate.py`), and integrated gate into CLI workflow.

## Phase 7 — Refusal System
- **Tools & References Used**: Policy escalation protocols, structured CLI output guidelines.
- **Developer Execution**: Implemented `RefusalResponse` (`src/refusal.py`), created escalation next-step builder, authored unit tests (`tests/test_refusal.py`), and integrated refusal output path into `main.py`.

## Phase 8 — Apparent Gap Detection
- **Tools & References Used**: Entity extraction heuristics, gap analysis algorithms in RAG.
- **Developer Execution**: Built `detect_apparent_gap` (`src/gap_detector.py`), distinguished topic terms from entity qualifiers, integrated gap checks into `EvidenceGate`, authored unit tests (`tests/test_gap_detector.py`), and verified apparent gap refusal responses.

## Phase 9 — Contradiction Detection
- **Tools & References Used**: Numerical regex parsing, policy conflict resolution standards.
- **Developer Execution**: Implemented `ContradictionDetector` (`src/contradiction.py`), extracted numerical constraints and units, integrated conflict checks into `EvidenceGate`, added `REFUSED_CONFLICT` CLI formatting, authored unit tests (`tests/test_contradiction.py`), and verified conflict refusal output.

## Phase 10 — Grounded Answer Construction
- **Tools & References Used**: Citation binding patterns, grounded synthesis guidelines.
- **Developer Execution**: Built `GroundedGenerator` (`src/generator.py`), implemented `GroundedAnswer` model, bound clause citations to extracted claim statements, authored unit tests (`tests/test_generator.py`), and integrated generator into `main.py`.

## Phase 11 — Clause-Level Citations
- **Tools & References Used**: Regex tag parsing, citation validation standards.
- **Developer Execution**: Created `validate_citations` and `format_sources_block` (`src/citations.py`), enforced inline citation checking `[C0XX]`, added verifiable source blocks, authored unit tests (`tests/test_citations.py`), and updated `GroundedGenerator`.

## Phase 12 — CLI Answer Workflow
- **Tools & References Used**: Orchestration design patterns, CLI UX standards.
- **Developer Execution**: Integrated `run_grounded_assistant` pipeline (`src/cli.py`), updated `main.py` with interactive prompt and single-query options, authored workflow unit tests (`tests/test_workflow.py`), and verified full answerable and refusal workflows.

## Phase 13 — Ten-Question Evaluation
- **Tools & References Used**: Automated benchmark testing, JSON evaluation standards.
- **Developer Execution**: Created benchmark dataset (`tests/evaluation.json`) covering 5 answerable, 2 apparent gap, 1 contradiction, 1 ambiguous, and 1 irrelevant questions, built evaluation script (`tests/evaluate.py`), logged PASS/FAIL per-question results, and verified zero-failure execution.

## Phase 14 — Citation Evaluation
- **Tools & References Used**: Citation validation algorithms, information grounding metrics.
- **Developer Execution**: Built `tests/evaluate_citations.py`, verified presence, existence, support, and strictness of citations across all answerable questions, created unit tests (`tests/test_citation_eval.py`), and reported 100.0% citation accuracy.
```

Description: Update AI-USAGE.md for Phase 14 Citation Evaluation
IsArtifact: false
Overwrite: true
TargetFile: d:/VS_CODE_PROJECTS/Brite_Spark/AI-USAGE.md
toolAction: Writing AI-USAGE.md
toolSummary: Update AI-USAGE.md for Phase 14
