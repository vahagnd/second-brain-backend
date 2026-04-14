"""Vector math utilities for semantic search."""

import numpy as np


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Parameters
    ----------
    a : list[float]
        First vector.
    b : list[float]
        Second vector.

    Returns
    -------
    float
        Cosine similarity score between -1 and 1.
    """
    a_array = np.array(a)
    b_array = np.array(b)

    dot_product = np.dot(a_array, b_array)
    norm_a = np.linalg.norm(a_array)
    norm_b = np.linalg.norm(b_array)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))
