"""Mantic Thinking — cross-domain anomaly and opportunity detection.

Public API re-exports so users can write::

    from mantic_thinking import mantic_kernel, compute_temporal_kernel
"""

from mantic_thinking.core.mantic_kernel import (
    mantic_kernel,
    compute_temporal_kernel,
    verify_kernel_integrity,
    KERNEL_VERSION,
    KERNEL_HASH,
)
from mantic_thinking.core.safe_kernel import safe_mantic_kernel
from mantic_thinking.core.validators import (
    clamp_input,
    normalize_weights,
    validate_layers,
)

__all__ = [
    # Core kernel
    "mantic_kernel",
    "safe_mantic_kernel",
    "compute_temporal_kernel",
    "verify_kernel_integrity",
    "KERNEL_VERSION",
    "KERNEL_HASH",
    # Validators
    "clamp_input",
    "normalize_weights",
    "validate_layers",
    # Subpackages (lazy access)
    "core",
    "tools",
    "adapters",
    "mantic",
    "configs",
    "schemas",
    "visualization",
]
