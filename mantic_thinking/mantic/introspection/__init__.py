"""
Mantic Framework Layer Introspection

Provides layer visibility for architectural reasoning.

Version: 2.2.0

NOTE: Layer mappings are interpretive aids for reasoning about tool outputs.
They expose the hierarchy encoded in tool weights, helping LLMs and humans
understand which layers drive detections. They do not affect M-score calculation.
"""

from .hierarchy import get_layer_visibility, LAYER_DEFINITIONS

__all__ = ["get_layer_visibility", "LAYER_DEFINITIONS"]
__version__ = "2.2.0"
