"""
Gemini Adapter for Mantic Tools

Exposes ONE detection tool where the LLM supplies layer names, weights,
and values. Google Gemini FunctionDeclaration format.
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


def get_gemini_tools():
    """
    Return Google Gemini native tool format.

    Returns:
        list: Gemini tool definitions with function_declarations
    """
    openai_tools = get_openai_tools()

    declarations = []
    for tool in openai_tools:
        func = tool["function"]
        declarations.append({
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"]
        })

    return [{"function_declarations": declarations}]


def get_gemini_tools_flat():
    """
    Return flat list of function declarations.

    Returns:
        list: Flat list of function declaration dicts
    """
    openai_tools = get_openai_tools()
    return [
        {
            "name": tool["function"]["name"],
            "description": tool["function"]["description"],
            "parameters": tool["function"]["parameters"]
        }
        for tool in openai_tools
    ]


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
    return _execute(tool_name, arguments)


def format_for_gemini(result, tool_name=None):
    """
    Format a Mantic result for Gemini's consumption.

    Args:
        result: Raw tool result dict
        tool_name: Optional name of the tool

    Returns:
        dict: Formatted result
    """
    is_friction = "alert" in result and "window_detected" not in result
    is_emergence = "window_detected" in result

    formatted = {
        "content": result,
        "tool_name": tool_name
    }

    if is_friction:
        formatted["type"] = "friction"
        formatted["has_alert"] = result.get("alert") is not None
    elif is_emergence:
        formatted["type"] = "emergence"
        formatted["window_detected"] = result.get("window_detected", False)

    return formatted


def get_tool_by_name(tool_name):
    """
    Get a single tool definition by name.

    Args:
        tool_name: Name of the tool

    Returns:
        dict: Gemini function declaration format
    """
    tools = get_gemini_tools_flat()
    for tool in tools:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Tool not found: {tool_name}")


def explain_result(tool_name, result):
    """Get human-friendly explanation of tool result."""
    from mantic_thinking.adapters.openai_adapter import explain_result as _explain
    return _explain(tool_name, result)


def get_gemini_tool_guidance(tool_names=None):
    """Get tool calibration guidance formatted for Gemini system prompt."""
    return get_tool_guidance(tool_names)


def get_gemini_context(domain=None):
    """Get complete LLM context for Gemini."""
    return get_full_context(domain)


def get_gemini_prompt_addon():
    """
    Get prompt context for Gemini to understand Mantic.

    Returns:
        str: Prompt addon
    """
    return """
## Using Mantic Detection

You have access to one detection tool: `detect`.

**Core Formula:** M = (sum(W * L * I)) * f(t) / k_n

You define:
- **layer_names**: 3-6 layers that capture the dimensions of the situation
- **weights**: How much each layer matters (sum to 1.0)
- **layer_values**: Your assessment of each layer (0-1)
- **mode**: "friction" (risk/divergence) or "emergence" (opportunity/alignment)

The kernel handles the math. You handle the reasoning.

High M-score in friction = danger. High M-score in emergence = opportunity.
Same score, opposite meaning -- always check which mode produced it.
"""


if __name__ == "__main__":
    print("=== Gemini Adapter ===\n")

    tools = get_gemini_tools()
    declarations = tools[0]["function_declarations"]
    print(f"Function declarations: {len(declarations)}")
    for d in declarations:
        print(f"  - {d['name']}")

    print("\n--- Testing detect ---")
    result = execute_tool("detect", {
        "domain_name": "test_finance",
        "layer_names": ["technical", "macro", "flow", "risk"],
        "weights": [0.35, 0.30, 0.20, 0.15],
        "layer_values": [0.85, 0.80, 0.75, 0.70],
        "mode": "emergence"
    })
    print(f"Window: {result.get('window_detected')}")
    print(f"M-Score: {result['m_score']:.3f}")
