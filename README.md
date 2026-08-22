# Brite Spark 2026 — The Grounded Answer

A command-line RAG (Retrieval-Augmented Generation) policy assistant that answers policy questions strictly from a supplied Markdown policy manual with clause-level citations and safe refusal mechanisms.

## Quickstart

### Requirements
- Python 3.10+

### Setup
1. Clone or navigate to the repository directory.
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Place Policy Manual
Ensure the policy manual Markdown file is placed at `data/policy.md`.

### CLI Usage

- **Policy Question Execution**:
  ```bash
  python main.py --query "How long do I have to appeal?"
  # or short option:
  python main.py -q "How long do I have to appeal?"
  ```

- **List All Clause IDs and Headings**:
  ```bash
  python main.py --list-clauses
  # or short option:
  python main.py -l
  ```

- **Show Specific Clause Details**:
  ```bash
  python main.py --show-clause C003
  # or short option:
  python main.py -s C003
  ```

### Run Evaluation Suites
- **Retrieval Evaluation (Hit@1, Hit@3, Hit@5)**:
  ```bash
  python tests/evaluate_retrieval.py
  ```

- **Unit Test Suite**:
  ```bash
  python -m unittest discover -s tests
  ```
