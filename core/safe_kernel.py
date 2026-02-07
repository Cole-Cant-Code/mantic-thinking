"""
Safe wrapper for the immutable Mantic kernel.

Adds guardrails without modifying core/mantic_kernel.py.
"""

from core.mantic_kernel import mantic_kernel


def safe_mantic_kernel(W, L, I, f_time=1.0, k_n=1.0):
    """
    Validate inputs and delegate to the immutable core kernel.

    Raises:
        ValueError: if k_n is not positive.
    """
    if k_n <= 0:
        raise ValueError(f"Normalization constant k_n must be positive, got {k_n}")
    return mantic_kernel(W, L, I, f_time=f_time, k_n=k_n)
