# Brite Spark 2026 — The Grounded Answer

A command-line RAG (Retrieval-Augmented Generation) policy assistant that answers policy questions strictly from a supplied Markdown policy manual with clause-level citations and safe refusal mechanisms.

## Quickstart (Phase 1)

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

### Run
To verify policy manual loading:
```bash
python main.py
```

To specify a custom policy manual path:
```bash
python main.py --policy-path path/to/custom_policy.md
```
