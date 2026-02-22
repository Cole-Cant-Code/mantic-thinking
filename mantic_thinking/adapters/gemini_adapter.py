"""
Gemini Adapter for Mantic Tools

Converts Mantic tools to Google Gemini's native FunctionDeclaration format.
Compatible with Gemini 1.5 Pro, Flash, and future versions.

Usage:
    from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, execute_tool
    
    tools = get_gemini_tools()  # Returns Gemini-native format
    result = execute_tool("healthcare_phenotype_genotype", {...})
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    # adapters/ -> mantic_thinking/ -> repo root
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import inspect

from mantic_thinking.adapters.openai_adapter import (
    TOOL_MAP, get_openai_tools,
    get_tool_guidance, get_scaffold, get_domain_config, get_full_context,
)


def get_gemini_tools():
    """
    Return Google Gemini native tool format.
    
    Gemini uses FunctionDeclaration format within a Tool structure.
    
    Returns:
        list: Gemini tool definitions in the format:
        [
            {
                "function_declarations": [
                    {
                        "name": "tool_name",
                        "description": "...",
                        "parameters": {"type": "object", "properties": {...}}
                    }
                ]
            }
        ]
    """
    openai_tools = get_openai_tools()
    
    # Gemini uses function_declarations array within tool objects
    declarations = []
    for tool in openai_tools:
        func = tool["function"]
        declarations.append({
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"]
        })
    
    # Gemini expects a list with function_declarations
    return [{"function_declarations": declarations}]


def get_gemini_tools_flat():
    """
    Return flat list of function declarations (alternative format).
    
    Some Gemini SDK versions expect just the declarations array.
    
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
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments
        
    Returns:
        dict: Tool execution result
        
    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(TOOL_MAP.keys())}")

    # Filter arguments to only those expected by the function
    func = TOOL_MAP[tool_name]
    sig = inspect.signature(func)
    valid_params = set(sig.parameters.keys())
    filtered_args = {k: v for k, v in arguments.items() if k in valid_params}

    return func(**filtered_args)


def format_for_gemini(result, tool_name=None):
    """
    Format a Mantic result for Gemini's consumption.
    
    Creates a structured response suitable for Gemini function calling responses.
    
    Args:
        result: Raw tool result dict
        tool_name: Optional name of the tool that produced the result
        
    Returns:
        dict: Formatted result for Gemini
    """
    formatted = {
        "content": result,
        "tool_name": tool_name
    }
    
    # Add interpretation for Gemini
    is_friction = "alert" in result and "window_detected" not in result
    is_emergence = "window_detected" in result
    
    if is_friction:
        formatted["type"] = "friction"
        formatted["has_alert"] = result.get("alert") is not None
        formatted["interpretation"] = "Risk/divergence detection"
    elif is_emergence:
        formatted["type"] = "emergence"
        formatted["window_detected"] = result.get("window_detected", False)
        formatted["interpretation"] = "Opportunity/confluence detection"
    
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


def get_gemini_prompt_addon():
    """
    Get prompt context for Gemini to understand Mantic tools.
    
    Returns:
        str: Prompt addon
    """
    return """
## Using Mantic Early Warning Tools (17 Total)

You have access to 17 cross-domain detection tools using the Mantic Framework.

**Core Formula:** M = (sum(W * L * I)) * f(t) / k_n

### Tool Types

**FRICTION Tools (8):** Detect cross-layer conflicts (risks)
- Use when: Assessing risks, finding bottlenecks
- High M = danger
- Output: alerts, warnings

**CONFLUENCE Tools (8):** Detect alignment windows (opportunities)  
- Use when: Seeking optimal timing
- High M = opportunity
- Output: window_detected, recommendations

### Available Tools

Healthcare, Finance, Cybersecurity, Climate, Legal, Military, Social/Cultural, System Lock

Generic:
- `generic_detect` for caller-defined domains (3-6 layers).

Each domain has both a Friction tool (divergence detection) and Emergence tool (confluence detection).

### Response Format

All tools return:
- `m_score`: 0-1 intensity score
- `layer_attribution`: Which factors drove the result
- `alert` (friction) or `window_detected` (emergence): Detection result

Use function calling to invoke tools. All parameters are 0-1 floats (some support -1 to 1).
"""


def explain_result(tool_name, result):
    """
    [v1.2.0] Get human-friendly explanation of tool result.
    
    Returns reasoning guidance based on layer visibility, helping LLMs
    and humans understand which hierarchical layer drove the detection.
    
    Args:
        tool_name: Name of the tool
        result: Tool result dict (must include 'layer_visibility')
    
    Returns:
        Dict with explanation or None if layer_visibility not available
    """
    layer_vis = result.get("layer_visibility")
    if not layer_vis:
        return None
    
    dominant = layer_vis.get("dominant")
    rationale = layer_vis.get("rationale")
    
    hints = {
        "Micro": [
            "Trust immediate signals but check for noise/outliers",
            "Individual-level factors are primary driver",
            "Short-term volatility expected"
        ],
        "Meso": [
            "Local context matters most - verify environmental factors",
            "Pattern is contextual/domain-specific",
            "Medium-term patterns dominant"
        ],
        "Macro": [
            "Systemic trend; slower to change but more persistent",
            "Check institutional/contextual constraints",
            "Structural level pattern"
        ],
        "Meta": [
            "Long-term adaptation signal",
            "Consider if baseline has shifted",
            "May indicate regime change"
        ]
    }
    
    return {
        "tool": tool_name,
        "m_score": result.get("m_score"),
        "dominant_layer": dominant,
        "layer_rationale": rationale,
        "reasoning_hints": hints.get(dominant, []),
        "_api_version": "1.2.0"
    }


def get_gemini_tool_guidance(tool_names=None):
    """
    Get tool calibration guidance formatted for Gemini system prompt.

    Loads per-tool YAML guidance (selection criteria, parameter calibration,
    interaction tuning, interpretation) for system prompt injection.

    Args:
        tool_names: List of tool names, or None for all tools.

    Returns:
        str: Formatted guidance text.
    """
    return get_tool_guidance(tool_names)


def get_gemini_context(domain=None):
    """
    Get complete LLM context for Gemini in correct load order.

    Chains: Scaffold → Domain Config (optional) → Tool Guidance.

    Args:
        domain: Optional domain name (healthcare, finance, cyber, etc.).

    Returns:
        str: Complete context for system prompt injection.
    """
    return get_full_context(domain)


if __name__ == "__main__":
    # Test the adapter
    print("=== Gemini Adapter Test (17 Tools) ===\n")

    tools = get_gemini_tools()
    declarations = tools[0]["function_declarations"]
    print(f"Total function declarations: {len(declarations)}")
    
    friction = [d for d in declarations if "FRICTION" in d["description"]]
    emergence = [d for d in declarations if "CONFLUENCE" in d["description"]]
    print(f"  Friction: {len(friction)}")
    print(f"  Emergence: {len(emergence)}")
    
    print("\n--- Testing Friction Tool ---")
    result = execute_tool("healthcare_phenotype_genotype", {
        "phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8
    })
    print(f"Alert: {result['alert']}")
    print(f"M-Score: {result['m_score']:.3f}")
    
    print("\n--- Testing Emergence Tool ---")
    result = execute_tool("finance_confluence_alpha", {
        "technical_setup": 0.85, "macro_tailwind": 0.80,
        "flow_positioning": 0.75, "risk_compression": 0.70
    })
    print(f"Window: {result['window_detected']}")
    print(f"M-Score: {result['m_score']:.3f}")
    
    print("\n--- Cross-Model Parity Check ---")
    from mantic_thinking.adapters.openai_adapter import execute_tool as openai_execute
    from mantic_thinking.adapters.kimi_adapter import execute as kimi_execute
    from mantic_thinking.adapters.claude_adapter import execute_tool as claude_execute
    
    params = {"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8}
    
    gemini_r = execute_tool("healthcare_phenotype_genotype", params)
    openai_r = openai_execute("healthcare_phenotype_genotype", params)
    kimi_r = kimi_execute("healthcare_phenotype_genotype", params)
    claude_r = claude_execute("healthcare_phenotype_genotype", params)
    
    assert gemini_r["m_score"] == openai_r["m_score"] == kimi_r["m_score"] == claude_r["m_score"]
    print(f"✓ All 4 adapters return identical M-score: {gemini_r['m_score']:.3f}")
