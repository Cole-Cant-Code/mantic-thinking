"""
Claude Adapter for Mantic Tools

Exposes ONE detection tool where the LLM supplies layer names, weights,
and values. Claude tool-use format with metadata.
"""

import sys
import os
import inspect

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

from mantic_thinking.adapters.openai_adapter import (
    TOOL_MAP, get_openai_tools, get_presets,
    get_tool_guidance, get_scaffold, get_domain_config, get_full_context,
)


def get_claude_tools():
    """
    Return Claude tool-use format for Mantic detection.

    Returns:
        list: Claude tool definitions
    """
    openai_tools = get_openai_tools()

    claude_tools = []
    for tool in openai_tools:
        func = tool["function"]
        claude_tool = {
            "name": func["name"],
            "description": func["description"],
            "input_schema": func["parameters"],
            "_claude_meta": {
                "tool_type": "detect",
                "requires_confirmation": False,
                "idempotent": True,
                "safe_to_retry": True,
                "estimated_duration_ms": 50
            }
        }
        claude_tools.append(claude_tool)

    return claude_tools


def execute_tool(tool_name, arguments):
    """
    Execute a Mantic tool with given arguments.

    For 'detect', routes to generic_detect. Legacy tool names still work.

    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments

    Returns:
        dict: Tool execution result
    """
    from mantic_thinking.adapters.openai_adapter import execute_tool as _execute
    result = _execute(tool_name, arguments)

    return {
        **result,
        "_claude_meta": {
            "tool_used": tool_name,
            "execution_successful": True,
        }
    }


def format_for_claude(result, tool_name=None):
    """
    Format a Mantic result for Claude's consumption.

    Args:
        result: Raw tool result dict
        tool_name: Optional name of the tool

    Returns:
        str: Formatted summary
    """
    is_friction = "alert" in result and "window_detected" not in result
    is_emergence = "window_detected" in result

    lines = []

    if tool_name:
        lines.append(f"## Mantic Analysis: {tool_name}")
    else:
        lines.append("## Mantic Analysis Result")

    if is_friction:
        lines.append("\n**Type**: FRICTION (Divergence Detection)")
        if result.get("alert"):
            lines.append(f"\n**ALERT**: {result['alert']}")
        else:
            lines.append("\nNo friction detected. Systems aligned within normal parameters.")
        if "severity" in result:
            lines.append(f"**Severity**: {result['severity']:.2f}")

    elif is_emergence:
        lines.append("\n**Type**: EMERGENCE (Alignment Detection)")
        if result.get("window_detected"):
            lines.append("\n**WINDOW DETECTED**: Favorable alignment across layers")
            if "window_type" in result:
                lines.append(f"**Type**: {result['window_type']}")
        else:
            lines.append("\nNo alignment window. Conditions not yet favorable.")
        if "confidence" in result:
            lines.append(f"**Confidence**: {result['confidence']:.2f}")

    m_score = result.get("m_score", 0)
    lines.append(f"\n**M-Score**: {m_score:.3f}")

    if result.get("recommended_action"):
        lines.append(f"\n**Recommended Action**: {result['recommended_action']}")

    if result.get("layer_attribution"):
        lines.append("\n**Layer Contributions**:")
        for layer, pct in result["layer_attribution"].items():
            bar = "#" * int(pct * 20)
            lines.append(f"  - {layer}: {pct:.1%} {bar}")

    return "\n".join(lines)


def explain_result(tool_name, result):
    """Get human-friendly explanation of tool result."""
    from mantic_thinking.adapters.openai_adapter import explain_result as _explain
    return _explain(tool_name, result)


def get_claude_tool_guidance(tool_names=None):
    """Get tool calibration guidance formatted for Claude system prompt."""
    return get_tool_guidance(tool_names)


def get_claude_context(domain=None):
    """Get complete LLM context for Claude."""
    return get_full_context(domain)


if __name__ == "__main__":
    print("=== Claude Adapter ===\n")

    tools = get_claude_tools()
    print(f"Tools: {len(tools)}")
    for t in tools:
        print(f"  - {t['name']}")

    print("\n--- Testing detect ---")
    result = execute_tool("detect", {
        "domain_name": "test_healthcare",
        "layer_names": ["phenotypic", "genomic", "environmental", "psychosocial"],
        "weights": [0.35, 0.30, 0.20, 0.15],
        "layer_values": [0.3, 0.9, 0.4, 0.8],
        "mode": "friction"
    })
    print(format_for_claude(result, "detect"))
