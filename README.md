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

### Run Policy Inspection CLI
- **View Policy Summary**:
  ```bash
  python main.py
  ```
- **List All Clause IDs and Headings**:
  ```bash
  python main.py --list-clauses
  # or short option:
  python main.py -l
  ```
- **Show Specific Clause Details and Original Text**:
  ```bash
  python main.py --show-clause C003
  # or short option:
  python main.py -s C003
  ```

### Run Tests
```bash
python -m unittest discover -s tests
```
