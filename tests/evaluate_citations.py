import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parser import parse_markdown_policy
from src.cli import run_grounded_assistant
from src.citations import extract_citation_tags, validate_citations
from src.retriever import tokenize


def verify_clause_support(answer_text: str, cited_clause) -> bool:
    """
    Verifies that the cited clause actually contains keywords/tokens supporting the answer text.
    """
    answer_tokens = set(tokenize(answer_text))
    clause_tokens = set(tokenize(f"{cited_clause.section} {cited_clause.heading} {cited_clause.text}"))
    
    # Check if there is significant term overlap between claim and cited clause
    shared = answer_tokens & clause_tokens
    return len(shared) >= 2


def run_citation_evaluation(policy_path: str = "data/policy.md", eval_path: str = "tests/evaluation.json"):
    policy_file = Path(policy_path)
    eval_file = Path(eval_path)

    if not policy_file.exists() or not eval_file.exists():
        print(f"ERROR: Missing input file(s) ({policy_file}, {eval_file})", file=sys.stderr)
        sys.exit(1)

    with open(policy_file, "r", encoding="utf-8") as f:
        policy_content = f.read()

    clauses = parse_markdown_policy(policy_content, source_file=str(policy_file))
    clause_map = {c.id.upper(): c for c in clauses}

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_cases = json.load(f)

    answerable_cases = [case for case in eval_cases if case.get("expected") == "ANSWERED"]

    total_answerable = len(answerable_cases)
    valid_citations = 0
    invalid_citations = 0
    failure_details = []

    for case in answerable_cases:
        qid = case["id"]
        question = case["question"]

        raw_output = run_grounded_assistant(question, clauses)

        # Extract answer text block from CLI format
        if "ANSWER\n\n" in raw_output and "\n\nSOURCES\n\n" in raw_output:
            answer_text = raw_output.split("ANSWER\n\n")[1].split("\n\nSOURCES\n\n")[0].strip()
        else:
            invalid_citations += 1
            failure_details.append(f"Query {qid}: Missing ANSWER section in response.")
            continue

        cited_ids = extract_citation_tags(answer_text)
        if not cited_ids:
            invalid_citations += 1
            failure_details.append(f"Query {qid}: Answer contains no inline citation tags [C0XX].")
            continue

        # Validate that all cited IDs exist in policy manual
        all_ids_exist = all(cid in clause_map for cid in cited_ids)
        if not all_ids_exist:
            invalid_citations += 1
            failure_details.append(f"Query {qid}: Cites clause ID not found in policy manual.")
            continue

        # Verify that cited clauses actually support the answer content
        all_clauses_support = all(
            verify_clause_support(answer_text, clause_map[cid]) for cid in cited_ids
        )
        if not all_clauses_support:
            invalid_citations += 1
            failure_details.append(f"Query {qid}: Cited clause text does not support answer claims.")
            continue

        # Strict validation check
        approved_clauses = [clause_map[cid] for cid in cited_ids]
        val_res = validate_citations(answer_text, approved_clauses)
        if not val_res.is_valid:
            invalid_citations += 1
            failure_details.append(f"Query {qid}: Failed strict citation validation: {val_res.error_message}")
            continue

        valid_citations += 1

    accuracy_rate = (valid_citations / total_answerable * 100.0) if total_answerable > 0 else 100.0

    print("Citation Evaluation Report\n")
    print(f"Total Answerable Queries: {total_answerable}")
    print(f"Valid Citations: {valid_citations}")
    print(f"Invalid/Missing Citations: {invalid_citations}")
    print(f"Citation Accuracy Rate: {accuracy_rate:.1f}%")

    if failure_details:
        print("\nFAILURE DETAILS:\n")
        for detail in failure_details:
            print(f"- {detail}")


if __name__ == "__main__":
    run_citation_evaluation()
