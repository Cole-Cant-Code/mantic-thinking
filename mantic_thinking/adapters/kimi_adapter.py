"""
Kimi Native Adapter for Mantic Tools

Exposes ONE detection tool where the LLM supplies layer names, weights,
and values. Kimi native format.
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from mantic_thinking.adapters.openai_adapter import (
    TOOL_MAP, get_openai_tools, get_presets,
    get_tool_guidance, get_scaffold, get_domain_config, get_full_context,
)
from mantic_thinking.tools import generic_detect


def get_kimi_tools():
    """
    Return Kimi native tool format for Mantic detection.

    Returns:
        list: Kimi tool definitions
    """
    openai_tools = get_openai_tools()

    kimi_tools = []
    for tool in openai_tools:
        func = tool["function"]
        kimi_tool = {
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"],
            "_mantic_meta": {
                "version": "2.2.0",
                "tool_type": "detect",
                "requires_clamping": True,
                "deterministic": True
            }
        }
        kimi_tools.append(kimi_tool)

    return kimi_tools


def execute(tool_name, params):
    """
    Execute a Mantic tool with given parameters.

    For 'detect', routes to generic_detect. Legacy tool names still work.

    Args:
        tool_name: Name of the tool to execute
        params: Dict of parameters

    Returns:
        dict: Tool execution result
    """
    from mantic_thinking.adapters.openai_adapter import execute_tool
    return execute_tool(tool_name, params)


def batch_execute(tools_with_params):
    """
    Execute multiple tools in batch.

    Args:
        tools_with_params: List of dicts with 'tool' and 'params' keys

    Returns:
        list: Results in same order as input
    """
    results = []
    for item in tools_with_params:
        try:
            result = execute(item["tool"], item["params"])
            results.append({"success": True, "result": result, "tool": item["tool"]})
        except Exception as e:
            results.append({"success": False, "error": str(e), "tool": item["tool"]})
    return results


def get_tool_summary(tool_type="all"):
    """
    Get a concise summary of available tools.

    Args:
        tool_type: Ignored (single detect tool). Kept for compatibility.

    Returns:
        str: Formatted summary
    """
    tools = get_kimi_tools()
    lines = ["MANTIC DETECTION ENGINE", "=" * 50]
    for tool in tools:
        lines.append(f"\n{tool['name']}")
        lines.append(f"  {tool['description'][:70]}...")
    return "\n".join(lines)


def validate_params(tool_name, params):
    """
    Validate parameters for the detect tool.

    Args:
        tool_name: Name of the tool
        params: Dict of parameters to validate

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    if tool_name != "detect":
        errors.append(f"Use 'detect' tool. Legacy name '{tool_name}' accepted for backward compat only.")

    required = ["domain_name", "layer_names", "weights", "layer_values", "mode"]
    for param in required:
        if param not in params:
            errors.append(f"Missing required parameter: {param}")

    if "mode" in params and params["mode"] not in ("friction", "emergence"):
        errors.append(f"mode must be 'friction' or 'emergence', got '{params['mode']}'")

    return {"valid": len(errors) == 0, "errors": errors}


def compare_friction_emergence(domain_name, layer_names, weights, layer_values):
    """
    Compare friction and emergence results for the same inputs.

    The LLM supplies its own layer names, weights, and values.
    Both modes run on the same inputs for direct comparison.

    Args:
        domain_name: Domain label
        layer_names: Layer name strings
        weights: Layer weights
        layer_values: Layer input values

    Returns:
        dict: Comparison results
    """
    friction_result = generic_detect.detect(
        domain_name=domain_name,
        layer_names=layer_names,
        weights=weights,
        layer_values=layer_values,
        mode="friction"
    )
    emergence_result = generic_detect.detect(
        domain_name=domain_name,
        layer_names=layer_names,
        weights=weights,
        layer_values=layer_values,
        mode="emergence"
    )

    return {
        "domain": domain_name,
        "friction": {
            "alert_present": friction_result.get("alert") is not None,
            "m_score": friction_result.get("m_score")
        },
        "emergence": {
            "window_detected": emergence_result.get("window_detected", False),
            "m_score": emergence_result.get("m_score")
        },
        "interpretation": "Same M-score, opposite meaning. High M in friction = risk. High M in emergence = opportunity."
    }


def explain_result(tool_name, result):
    """Get human-friendly explanation of tool result."""
    from mantic_thinking.adapters.openai_adapter import explain_result as _explain
    return _explain(tool_name, result)


def get_kimi_tool_guidance(tool_names=None):
    """Get tool calibration guidance formatted for Kimi system prompt."""
    return get_tool_guidance(tool_names)


def get_kimi_context(domain=None):
    """Get complete LLM context for Kimi."""
    return get_full_context(domain)


if __name__ == "__main__":
    print("=== Kimi Adapter ===\n")

    print(get_tool_summary("all"))

    print("\n--- Testing friction vs emergence ---")
    comparison = compare_friction_emergence(
        "healthcare",
        ["phenotypic", "genomic", "environmental", "psychosocial"],
        [0.35, 0.30, 0.20, 0.15],
        [0.3, 0.9, 0.4, 0.8]
    )
    print(f"Friction Alert: {comparison['friction']['alert_present']}")
    print(f"Emergence Window: {comparison['emergence']['window_detected']}")
