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
