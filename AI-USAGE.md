# AI Usage Log

## Overview
This document tracks tool usage, documentation assistance, and reference research throughout the development of the Grounded Policy Assistant.

## Phase 1 — Project Setup and Policy Loading
- **Tools & References Used**: Python standard library documentation (`pathlib`, `argparse`), Markdown specification guides, and Git version control standards.
- **Developer Execution**: Initialized repository structure (`data/`, `src/`, `tests/`), created project scaffold, written file loading logic in `main.py`, structured sample policy manual `data/policy.md`, and authored project documentation (`README.md`, `DECISIONS.md`).

## Phase 2 — Policy Clause Extraction
- **Tools & References Used**: Python `re` module regex documentation, Python `dataclasses` reference guide, and `unittest` framework documentation.
- **Developer Execution**: Designed `Clause` data model (`src/models.py`), implemented line-preserving Markdown parser (`src/parser.py`), authored unit test suite (`tests/test_parser.py`), and verified parsing output.
