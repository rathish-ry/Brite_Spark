# Brite Spark 2026 — The Grounded Answer (Groq Edition)

A production-grade, date-aware command-line RAG (Retrieval-Augmented Generation) policy assistant built for **Brite Spark 2026 — Problem 1: The Grounded Answer** with Groq-powered natural language answer synthesis and date-aware policy amendment support (**Amendment No. 2026-01**).

The assistant answers policy questions strictly using the supplied policy manual (`data/policy.md`) and amendment manual (`data/Amendment No. 2026-01.md`), synthesizes grounded natural-language answers via Groq LLM, provides exact clause-level citations and source provenance (including line numbers, verbatim text, and transitional clauses), and explicitly refuses to answer when policy evidence is incomplete, ambiguous, missing, or contradictory.

---

## 🏗 Architecture Overview

```text
               ┌──────────────────────────────┐
               │    Caseworker Policy Query   │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │  Date & Context Resolution   │
               │  (Determination / Change /   │
               │   Spanning Period Extractor) │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │   Temporal Applicability     │
               │   (Filter Applicable Corpus) │
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
 │ Groq Grounded Generator   │ │ Refusal Response Builder  │
 │ ├── Fact Extraction       │ │ ├── Reason Specification  │
 │ ├── Natural Synthesis     │ │ └── Supervisor Escalation │
 │ └── Dual Citation Binding │ └─────────────┬─────────────┘
 └─────────────┬─────────────┘               │
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
- Groq API Key (Optional for offline fallback, recommended for live LLM synthesis)

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

### Groq API Configuration
Configure your Groq API key in environment variables or in `.env`:

**Windows PowerShell**:
```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
$env:GROQ_MODEL="llama-3.3-70b-versatile"
```

**Linux / macOS**:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
export GROQ_MODEL="llama-3.3-70b-versatile"
```

**Local `.env` File**:
Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 💻 CLI Usage Guide

### 1. Interactive Caseworker Mode (Default)
Launch the interactive caseworker workspace supporting live query loops, clause inspections, and evaluation runs:
```bash
python main.py
```

### 2. Single Question Execution
Query a specific policy question directly from the command line:
```bash
python main.py -q "What was the earnings disregard for a determination on 15 March 2026?"
```

**Sample Output**:
```text
========================================
       GROUNDED POLICY ASSISTANT        
========================================

Question:
> What was the earnings disregard for a determination on 15 March 2026?

ANSWER

The earnings disregard was $175 per month. The determination was made on 15 March 2026, which is on or after 1 March 2026, so the amended amount applies. [A2026-01-C02] [A2026-01-C08]

SOURCES

[A2026-01-C02] 1. Earnings disregard — Paragraph 1.1
Source: data/Amendment No. 2026-01.md lines 14-14

"**1.1** In §6.4.1(a), for "$120 per month" substitute "**$175 per month**"."

[A2026-01-C08] 5. Transitional provision — Paragraph 5.1
Source: data/Amendment No. 2026-01.md lines 47-47

"**5.1** The amendments made by paragraphs 1, 3 and 4 apply to any determination made on or after 1 March 2026, including a determination in respect of a period before that date."

STATUS: ANSWERED
```

---

## 🧪 Evaluation & Audit Suites

### 1. Day 2 Evaluation Benchmark Suite (18 Questions)
Runs the extended 18-question evaluation suite checking final answer correctness, citations, and status:
```bash
python tests/evaluate.py
```

### 2. Final Compliance Verification Audit
```bash
python scripts/final_verification.py
```

### 3. Submission Packaging Verification
```bash
python scripts/package_submission.py
```

### 4. Full Automated Unit Test Suite
```bash
python -m unittest discover -s tests
```

---

## 📊 Benchmark Results

| Metric / Audit Suite | Result | Status |
| :--- | :--- | :--- |
| **Unit Test Suite** | 68 / 68 Passed | **PASS** |
| **Day 2 Challenge Benchmark (18 Questions)** | 18 / 18 Passed | **PASS** |
| **Citation Accuracy Rate** | 100.0% | **PASS** |
| **End-to-End Query Latency** | < 15 ms | **PASS** |
| **Net RAM Memory Usage** | < 1 MB | **PASS** |
| **System Integrity Audit** | Operational | **PASS** |
| **Final Compliance Audit** | 100% Compliant | **PASS** |
