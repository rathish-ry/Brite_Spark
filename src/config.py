from dataclasses import dataclass


@dataclass
class EvidenceGateConfig:
    """
    Centralized configuration parameters for Evidence Gate validation.
    """
    min_retrieval_score: float = 0.25      # Minimum top BM25 normalized score required
    min_term_coverage: float = 0.35        # Minimum query key-term coverage in evidence text
    min_score_margin: float = 0.05         # Score margin indicating top candidate separation
    top_k_eval: int = 5                    # Number of top retrieved clauses to evaluate
