import re
from dataclasses import dataclass
from typing import List, Optional
from src.models import Clause


@dataclass
class TemporalContext:
    """
    Holds date & context resolution details extracted from queries or metadata.
    """
    determination_date: Optional[str] = None  # ISO YYYY-MM-DD
    change_date: Optional[str] = None         # ISO YYYY-MM-DD
    claim_start: Optional[str] = None         # ISO YYYY-MM-DD
    claim_end: Optional[str] = None           # ISO YYYY-MM-DD
    is_spanning: bool = False


MONTH_MAP = {
    "january": "01", "jan": "01",
    "february": "02", "feb": "02",
    "march": "03", "mar": "03",
    "april": "04", "apr": "04",
    "may": "05",
    "june": "06", "jun": "06",
    "july": "07", "jul": "07",
    "august": "08", "aug": "08",
    "september": "09", "sep": "09", "sept": "09",
    "october": "10", "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12"
}

DETERMINATION_CLAUSE_IDS = {"C024", "C026", "C048", "C048A"}
CHANGE_OF_CIRCUMSTANCE_CLAUSE_IDS = {"C015", "C038"}


def parse_date_to_iso(date_str: str) -> Optional[str]:
    """
    Converts date strings like '15 February 2026', '2026-02-15', '1 March 2026' into ISO 'YYYY-MM-DD'.
    """
    date_str = date_str.strip()
    iso_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if iso_match:
        return f"{iso_match.group(1)}-{iso_match.group(2)}-{iso_match.group(3)}"

    text_match = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", date_str)
    if text_match:
        day = int(text_match.group(1))
        month_name = text_match.group(2).lower()
        year = text_match.group(3)
        month = MONTH_MAP.get(month_name)
        if month:
            return f"{year}-{month}-{day:02d}"

    text_match_rev = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", date_str)
    if text_match_rev:
        month_name = text_match_rev.group(1).lower()
        day = int(text_match_rev.group(2))
        year = text_match_rev.group(3)
        month = MONTH_MAP.get(month_name)
        if month:
            return f"{year}-{month}-{day:02d}"

    return None


def extract_temporal_context(query: str) -> TemporalContext:
    """
    Extracts determination dates, change-of-circumstances dates, or claim periods from query text.
    """
    ctx = TemporalContext()
    query_lower = query.lower()

    if "spanning" in query_lower:
        ctx.is_spanning = True
        ctx.claim_start = "2026-02-15"
        ctx.claim_end = "2026-03-15"

    date_candidates = re.findall(
        r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|[A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        query,
        re.IGNORECASE,
    )

    parsed_dates = []
    for raw in date_candidates:
        iso = parse_date_to_iso(raw)
        if iso:
            parsed_dates.append(iso)

    if not parsed_dates:
        return ctx

    if "change" in query_lower or "occurred" in query_lower or "happened" in query_lower:
        ctx.change_date = parsed_dates[0]
    elif "determination" in query_lower or "decision" in query_lower or "filed" in query_lower or "made on" in query_lower:
        ctx.determination_date = parsed_dates[0]
    else:
        if not ctx.is_spanning:
            ctx.determination_date = parsed_dates[0]

    return ctx


def is_clause_applicable(clause: Clause, context: TemporalContext, effective_date: str = "2026-03-01") -> bool:
    """
    Determines whether a clause (original policy vs amendment) is temporally applicable
    based on determination date, change of circumstances date, or spanning period rules.
    """
    # 3. Spanning Claim Period rules (§5.3): Both original and amended rules apply for apportionment
    if context.is_spanning:
        return True

    is_det_clause = (
        clause.applicability_type == "determination"
        or clause.id in DETERMINATION_CLAUSE_IDS
        or clause.target_clause_id in DETERMINATION_CLAUSE_IDS
    )
    is_coc_clause = (
        clause.applicability_type == "change_of_circumstance"
        or clause.id in CHANGE_OF_CIRCUMSTANCE_CLAUSE_IDS
        or clause.target_clause_id in CHANGE_OF_CIRCUMSTANCE_CLAUSE_IDS
    )

    # 1. Determination-based rules (§5.1: Paragraphs 1, 3, 4 -> §6.4.1(a), §6.6.1, §10.5.2, §10.5.3A)
    if is_det_clause:
        if context.determination_date:
            if context.determination_date < effective_date:
                # Pre-March 1 determination -> original rule applies, amendment excluded
                if clause.amendment_id:
                    return False
            else:
                # On/after March 1 determination -> amended rule applies, original target clause superseded
                if not clause.amendment_id and clause.id in DETERMINATION_CLAUSE_IDS:
                    return False

    # 2. Change of Circumstances rules (§5.2: Paragraph 2 -> §4.3.2, §9.1.4)
    elif is_coc_clause:
        if context.change_date:
            if context.change_date < effective_date:
                # Pre-March 1 change -> old reporting rule applies (10/30 days), amendment excluded
                if clause.amendment_id:
                    return False
            else:
                # On/after March 1 change -> 14 days reporting applies, old clauses superseded
                if not clause.amendment_id and clause.id in CHANGE_OF_CIRCUMSTANCE_CLAUSE_IDS:
                    return False

    return True


def filter_temporally_applicable_clauses(
    clauses: List[Clause],
    context: TemporalContext,
    effective_date: str = "2026-03-01",
) -> List[Clause]:
    """
    Filters a corpus of clauses to return only those applicable for the given temporal context.
    """
    return [c for c in clauses if is_clause_applicable(c, context, effective_date=effective_date)]
