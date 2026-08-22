import math
import re
from dataclasses import dataclass
from typing import List, Dict, Set
from src.models import Clause

# Standard English stop words to filter out uninformative terms during retrieval
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


def simple_stem(word: str) -> str:
    """
    Applies a lightweight, deterministic suffix stemming rule to improve word matching.
    """
    word = word.lower()
    if len(word) <= 3:
        return word
    
    # Common suffix stemming
    suffixes = ["ing", "edly", "able", "ment", "ness", "s", "ed", "es", "ly"]
    for suf in suffixes:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[:-len(suf)]
    return word


def tokenize(text: str) -> List[str]:
    """
    Tokenizes input text into normalized, stemmed term tokens.
    """
    words = re.findall(r"\b\w+\b", text.lower())
    tokens = [
        simple_stem(w)
        for w in words
        if w not in STOP_WORDS and not w.isdigit() and len(w) > 1
    ]
    return tokens


@dataclass
class RetrievalResult:
    """
    Represents a ranked retrieval result with relevance score and matched query terms.
    """
    clause: Clause
    score: float
    matched_terms: List[str]

    def summary(self) -> str:
        return f"[{self.clause.id}] Score: {self.score:.4f} | {self.clause.section} — {self.clause.heading}"


class BM25Retriever:
    """
    Lexical retriever implementing the Okapi BM25 ranking algorithm.
    Configured specifically for clause-level policy text.
    """

    def __init__(self, clauses: List[Clause], k1: float = 1.5, b: float = 0.75):
        self.clauses = clauses
        self.k1 = k1
        self.b = b

        self.doc_tokens: List[List[str]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

        if clauses:
            self._index()

    def _index(self) -> None:
        N = len(self.clauses)
        total_len = 0

        for clause in self.clauses:
            # Weight heading and section words slightly higher by prepending them
            text_to_index = f"{clause.section} {clause.heading} {clause.heading} {clause.text}"
            tokens = tokenize(text_to_index)
            
            self.doc_tokens.append(tokens)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len

            # Track unique term document frequencies
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_doc_len = total_len / N if N > 0 else 1.0

        # Precompute Lucene/Okapi BM25 IDF scores
        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (N - df + 0.5) / (df + 0.5))

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Ranks indexed clauses against the query and returns top_k RetrievalResult objects.
        """
        if not self.clauses or not query.strip():
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        raw_scores: List[float] = [0.0] * len(self.clauses)
        matched_terms_per_doc: List[List[str]] = [[] for _ in self.clauses]

        for q_token in query_tokens:
            if q_token not in self.idf:
                continue

            token_idf = self.idf[q_token]

            for idx, doc_toks in enumerate(self.doc_tokens):
                tf = doc_toks.count(q_token)
                if tf > 0:
                    matched_terms_per_doc[idx].append(q_token)
                    doc_len = self.doc_lengths[idx]
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                    raw_scores[idx] += token_idf * (numerator / denominator)

        # Collect non-zero matching clauses
        query_max_idf = sum(self.idf[t] for t in set(query_tokens) if t in self.idf)
        if query_max_idf <= 0:
            return []

        results: List[RetrievalResult] = []
        for idx, raw_score in enumerate(raw_scores):
            if raw_score > 0:
                # Normalize raw BM25 score against maximum possible query IDF sum
                norm_score = min(1.0, raw_score / query_max_idf)
                results.append(
                    RetrievalResult(
                        clause=self.clauses[idx],
                        score=round(norm_score, 4),
                        matched_terms=list(set(matched_terms_per_doc[idx])),
                    )
                )

        # Sort descending by score
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
