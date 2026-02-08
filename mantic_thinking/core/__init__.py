"""
Mantic Early Warning System - Core Module

This module contains the immutable mantic kernel formula and validation utilities.
"""

from .mantic_kernel import mantic_kernel
from .validators import clamp_input, normalize_weights, validate_layers

__all__ = ["mantic_kernel", "clamp_input", "normalize_weights", "validate_layers"]
