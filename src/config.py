import os
from dataclasses import dataclass


@dataclass
class EvidenceGateConfig:
    """
    Centralized configuration parameters for Evidence Gate validation.
    """
    min_retrieval_score: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.25"))
    min_term_coverage: float = float(os.getenv("MIN_SUPPORT_SCORE", "0.35"))
    min_score_margin: float = 0.05
    top_k_eval: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
