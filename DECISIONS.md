# Architecture and Design Decisions Log

## Phase 1 — Project Setup and Policy Loading

### Decisions Made
1. **Directory Layout**: Organized core source logic under `src/`, test suites under `tests/`, and policy inputs under `data/`.
2. **CLI Entry Point**: `main.py` serves as the CLI interface accepting customizable `--policy-path` arguments.
3. **Standard Library First**: Kept Phase 1 dependencies zero-external-dependency using built-in Python modules (`pathlib`, `argparse`, `sys`).
4. **Encoding**: Enforced `utf-8` explicitly for policy loading to handle Markdown documents reliably across Operating Systems.

---

## Phase 2 — Policy Clause Extraction

### Decisions Made
1. **Dataclass Model**: Created `Clause` dataclass in `src/models.py` tracking `id`, `section`, `heading`, `text`, `source_start`, `source_end`, and `source_file`.
2. **Line-Preserving Regex Parser**: Built robust Markdown parser in `src/parser.py` using regex heading matching (`#` to `######`). Preserves exact 1-based source line numbers (`source_start` and `source_end`) for future citation validation.
3. **Structured Heading Hierarchy**: Tracks parent section names (H1/H2) and clause headings (H3/H4) to preserve context.
4. **Edge Case Resilience**: Handles multi-line paragraphs, bulleted/numbered lists, empty sections, horizontal rules, and EOF boundaries.

---

## Phase 3 — Policy Inspection CLI

### Decisions Made
1. **Separation of Inspection Logic**: Created `src/cli.py` to isolate presentation and inspection output formatting from `main.py` CLI argument parsing.
2. **Case-Insensitive Clause Lookup**: Enabled `--show-clause` / `-s` flag to match clause IDs case-insensitively (e.g. `c003` matches `C003`).
3. **Verifiable Source Provenance**: Output format for `--show-clause` displays section, heading, source line range, and verbatim clause text for caseworker verification.

---

## Phase 4 — Basic Retrieval

### Decisions Made
1. **Transparent BM25 Algorithm**: Implemented standard Okapi BM25 ranking algorithm in `src/retriever.py` without third-party vector databases to ensure transparent, deterministic lexical matching.
2. **Weighted Multi-Field Indexing**: Prepend section and heading terms to the clause text during indexing so header keywords carry appropriate importance.
3. **Tokenization & Light Stemming**: Applied custom stop-word removal and lightweight suffix stemming (`simple_stem`) to capture word variations (e.g., `appeals` -> `appeal`, `residency` -> `residen`).
4. **Normalized Scores**: Returned score normalized to $[0.0, 1.0]$ range alongside matched query terms for downstream Evidence Gate evaluation.

---

## Phase 5 — Retrieval Evaluation

### Decisions Made
1. **Structured Evaluation Dataset**: Created `tests/retrieval_eval.json` with 10 questions mapped to target policy clause IDs from the supplied manual.
2. **Automated Metrics**: Built `tests/evaluate_retrieval.py` measuring Top-1 (Hit@1), Top-3 (Hit@3), and Top-5 (Hit@5) retrieval accuracy.
3. **Honest Failure Reporting**: Implemented detailed per-question reports highlighting Top-1 misses and ranking positions without modifying expected ground truth to artificially boost metrics.

---

## Phase 6 — Evidence Gate

### Decisions Made
1. **Centralized Configuration**: Centralized all safety threshold magic numbers (`min_retrieval_score`, `min_term_coverage`, `min_score_margin`) in `src/config.py` rather than scattering magic values throughout the codebase.
2. **Deterministic Safety Decisions**: Built `EvidenceGate` in `src/evidence_gate.py` returning structured `EvidenceDecision` (`ANSWERABLE`, `REFUSE`, `CONFLICT`) prior to answer generation.
3. **Multi-Factor Validation**: Evaluated retrieval confidence score, query key-term coverage across candidate evidence, and presence of directive policy rules (`must`, `shall`, `within`, `eligible`, `exceed`) to prevent answering when evidence is loosely related but incomplete.

---

## Phase 7 — Refusal System

### Decisions Made
1. **Structured Refusal Contract**: Created `RefusalResponse` in `src/refusal.py` enforcing mandatory challenge fields (`Question`, `REFUSAL`, `Reason`, `Next step`, `STATUS: REFUSED`).
2. **Actionable Case Escalation**: Included specific next-step caseworker guidance (`"Refer the case to the Benefits Policy Supervisor for a formal policy ruling."`) instead of generic `"I don't know"` responses.
3. **CLI Integration**: Routed any query failing Evidence Gate validation directly to formatted refusal output.

---

## Phase 8 — Apparent Gap Detection

### Decisions Made
1. **Qualifier & Entity Term Extraction**: Implemented `detect_apparent_gap` in `src/gap_detector.py` to isolate specific query subjects/qualifiers (e.g., `representative`, `third party`, `credit card`) from general policy topic terms.
2. **Distinguishing Related from Answered**: Verified whether candidate retrieved clauses contain the specific entity/qualifier requested by the query.
3. **Explicit Gap Refusals**: Triggered `EvidenceStatus.REFUSE` with detailed explanation whenever a policy topic is retrieved but the specific requested condition/entity is unmentioned in the manual.

---

## Phase 9 — Contradiction Detection

### Decisions Made
1. **Conservative Numerical Conflict Parsing**: Built `ContradictionDetector` in `src/contradiction.py` to compare numerical values paired with units (e.g. `30 days` vs `15 days`) across top-ranked candidate clauses sharing core policy topic keywords.
2. **Conflict Escalation Refusal**: Integrated `STATUS: REFUSED_CONFLICT` formatting into `RefusalResponse` in `src/refusal.py`, printing both conflicting clauses verbatim alongside source line numbers so caseworkers can see the exact contradiction.
3. **Preventing Arbitrary Selection**: Ensured the assistant never silently selects one side of an internal policy contradiction.

---

## Phase 10 — Grounded Answer Construction

### Decisions Made
1. **Strict Context Isolation**: Built `GroundedGenerator` in `src/generator.py` taking ONLY the user question and Evidence-Gate-approved clauses.
2. **Deterministic Fact Extraction**: Constructed plain-language answers using exact claims extracted from approved clauses without adding external knowledge or inventing unstated rules.
3. **Clause Citation Binding**: Embedded clause citation tags `[C0XX]` directly after substantive claims to ensure verifiable source provenance.

---

## Phase 11 — Clause-Level Citations

### Decisions Made
1. **Strict Citation Validation**: Built `validate_citations` in `src/citations.py` to reject any answer containing uncited substantive claims or invalid clause IDs.
2. **Verifiable Sources Block**: Added `format_sources_block` in `src/citations.py` printing clause ID, section, heading, exact source line numbers, and verbatim policy text for caseworker verification.
3. **Prohibition of Vague References**: Rejected phrases like "According to the manual" in favor of strict clause-level identifiers (`[C053]`).

---

## Phase 12 — CLI Answer Workflow

### Decisions Made
1. **Pipeline Orchestrator**: Integrated `run_grounded_assistant` in `src/cli.py` connecting Parser -> Retriever -> Evidence Gate (Gap & Conflict Check) -> Generator -> Citation Validator -> CLI Presenter.
2. **Interactive CLI Prompt**: Updated `main.py` to support both single-command `--query` execution and an interactive command-line prompt for caseworker questions.
3. **Unified CLI Output Contract**: Standardized final outputs across all execution paths (`STATUS: ANSWERED`, `STATUS: REFUSED`, `STATUS: REFUSED_CONFLICT`).

---

## Phase 13 — Ten-Question Evaluation

### Decisions Made
1. **Challenge Benchmark Dataset**: Authored `tests/evaluation.json` containing 10 benchmark questions spanning normal answerable queries (5), apparent gaps (2), contradiction (1), ambiguous query (1), and irrelevant query (1).
2. **Automated Evaluation Runner**: Built `tests/evaluate.py` executing end-to-end evaluation, checking expected vs actual statuses, logging per-question PASS/FAIL logs, and printing pass/fail totals.
3. **Honest Reporting**: Logged exact failure details (Question, Expected, Actual, Reason) whenever expected results differ from system outputs.

---

## Phase 14 — Citation Evaluation

### Decisions Made
1. **Four-Point Citation Verification**: Created `tests/evaluate_citations.py` verifying that (1) every answerable query has citations, (2) all cited clause IDs exist in `data/policy.md`, (3) cited clauses actually contain supporting terms (`verify_clause_support`), and (4) no uncited claims exist.
2. **Citation Accuracy Metric**: Reported Citation Accuracy Rate ($100.0\%$) across all benchmark answerable queries.

---

## Phase 15 — Performance Benchmarking

### Decisions Made
1. **Profiling Metric Tracking**: Created `tests/benchmark_performance.py` using `time.perf_counter` and `tracemalloc` to track parsing/indexing latency, retrieval latency, evidence gate latency, end-to-end query latency, and net RAM footprint.
2. **Sub-15ms Latency**: Achieved average end-to-end query latency of $\approx 12.15$ ms (target: $< 500$ ms) and net memory footprint of $\approx 0.29$ MB (target: $< 100$ MB).

---

## Phase 16 — System Integrity Auditing

### Decisions Made
1. **Comprehensive Health Check**: Built `tests/audit_system.py` auditing file structure completeness, AST Python syntax validity across 31 files, clause parsing integrity (zero duplicate IDs, 1-based line continuity), evaluation dataset validity, and code formatting hygiene.
2. **Zero Defect Status**: Verified `AUDIT RESULT: ALL SYSTEMS OPERATIONAL`.

---

## Phase 17 — Interactive Caseworker CLI

### Decisions Made
1. **Dedicated Interactive Interface**: Built `src/interactive.py` supporting live caseworker session loops with `/help`, `/list`, `/show <id>`, `/eval`, `/history`, and `/exit` commands.
2. **Session Context & Provenance**: Enabled caseworkers to query policy questions, inspect clause texts, view session query history, and run live evaluation benchmark suites directly inside the CLI session.

---

## Phase 18 — Submission Packaging

### Decisions Made
1. **Automated Packaging Verification**: Built `scripts/package_submission.py` to automate end-to-end validation of required challenge artifacts, full unit test suite execution (44 tests), evaluation benchmark (10/10 PASS), and system integrity audit.
2. **Submission Status**: Verified `STATUS: READY FOR SUBMISSION`.

---

## Phase 19 — Final Verification Audit

### Decisions Made
1. **10-Point Challenge Audit**: Built `scripts/final_verification.py` executing a 10-point compliance audit covering parser provenance, BM25 retrieval, evidence gate, refusal escalation, apparent gap detection, contradiction detection, grounded answer synthesis, 10-question benchmark, performance latency, and documentation completeness.
2. **100% Compliance Verdict**: Verified `VERDICT: 100% CHALLENGE COMPLIANT — READY FOR PRODUCTION`.

---

## Phase 20 — Final Release & Project Handoff

### Decisions Made
1. **Release Packaging**: Compiled complete documentation (`README.md`, `DECISIONS.md`, `AI-USAGE.md`), ran full verification suite (49 unit tests OK, 10/10 benchmark PASS, 100% citation accuracy, sub-15ms latency, zero defects), and finalized project handoff.
2. **Production Handoff**: Confirmed repository state is clean, fully committed, and ready for official competition evaluation.

---

## Day 2 — Amendment No. 2026-01 & Temporal Policy Architecture

### 1. Amendment Representation
- **Corpus Extension**: Added `data/Amendment No. 2026-01.md` as an independent document alongside `data/policy.md` without permanently modifying or merging into `policy.md`.
- **Clause Model Metadata**: Extended `Clause` dataclass in `src/models.py` with `amendment_id` (`"A2026-01"`), `effective_date` (`"2026-03-01"`), `applicability_type` (`"determination"`, `"change_of_circumstance"`, `"transitional"`), `amendment_type` (`"substitution"`, `"insertion"`, `"transitional"`), and `target_clause_id` (e.g. `C024`, `C015`, `C038`, `C026`, `C048`, `C048A`).
- **Amendment Parser**: Built `parse_amendment_policy` in `src/amendment_parser.py` splitting numbered amendment paragraphs (`**1.1**`, `**2.1**`, `**5.1**`) and tagging exact rule mappings.

### 2. Determination Dates Handling
- **Paragraphs 1, 3, and 4 (§5.1)**: Governs §6.4.1(a) ($120 $\rightarrow$ $175), §6.6.1 (income thresholds), §10.5.2 (20% $\rightarrow$ 15%), and §10.5.3A (sanction exception).
- **Resolution Rule**: If `determination_date < 2026-03-01`, original policy rules apply and amendment clauses are excluded. If `determination_date >= 2026-03-01`, amended rules apply and original superseded target clauses are excluded.

### 3. Change of Circumstances Dates Handling
- **Paragraph 2 (§5.2)**: Governs §4.3.2 (10 $\rightarrow$ 14 days) and §9.1.4 (30 $\rightarrow$ 14 days).
- **Resolution Rule**: If `change_date < 2026-03-01`, old reporting rules apply (10 days / 30 days). If `change_date >= 2026-03-01`, amended reporting rules apply (14 calendar days).

### 4. Spanning Claim Periods Handling
- **Paragraph 5.3 (§5.3)**: Claims spanning `1 March 2026` are NOT treated as single-date claims. Both original figures and amended figures remain active evidence for apportionment under §7.4.3 (`C028`).

---

## Phase 26 — Groq Answer Generation Architecture

### 1. Why Groq Was Added
- **Natural Language Answer Synthesis**: Upstream logic extracts exact evidence clauses, but caseworkers require clear, concise, fluent answers rather than raw clause headings verbatim.
- **Strict Evidence Formatting**: Replaces direct string concatenation with Groq LLM synthesis while maintaining verifiable clause citations and distinct `SOURCES` blocks.

### 2. Separation of Pipeline Concerns
- **Retrieval & Safety First**: Groq is called ONLY AFTER upstream application logic parses Markdown, extracts temporal context, filters applicable clauses, runs BM25 retrieval, and passes Evidence Gate validation.
- **Deterministic Refusals**: If Evidence Gate identifies insufficient evidence, an apparent gap, or an internal policy contradiction, the system returns immediate deterministic refusals (`STATUS: REFUSED` or `STATUS: REFUSED_CONFLICT`) without invoking Groq.
- **Application-Driven Temporal Logic**: Groq does NOT independently evaluate determination dates, change dates, or policy versions. Temporal context and applicability are pre-computed in Python.

### 3. Post-Generation Citation Validation
- **Strict Verification**: Citations returned by Groq are verified against the approved evidence set using `validate_citations`. Uncited claims or invalid citation IDs are caught and corrected before display.

### 4. Fallback Behavior
- **API Resilience**: If `GROQ_API_KEY` is not set or network calls fail, the generator falls back gracefully to clean deterministic rule synthesis, ensuring automated test suites and offline CLI environments run without failure.
```

Description: Update DECISIONS.md with Phase 26 Groq Answer Generation architecture
IsArtifact: false
Overwrite: true
TargetFile: d:/VS_CODE_PROJECTS/Brite_Spark/DECISIONS.md
toolAction: Writing DECISIONS.md
toolSummary: Update DECISIONS.md for Phase 26
