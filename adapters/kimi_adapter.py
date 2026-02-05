"""
Kimi Native Adapter for Mantic Tools

Provides native Kimi tool format for seamless integration with Kimi Code CLI.

Includes both Friction tools (7) and Emergence tools (7) = 14 total.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.openai_adapter import TOOL_MAP, get_openai_tools, get_tools_by_type


def get_kimi_tools():
    """
    Return Kimi native tool format for all 14 Mantic tools.
    
    Returns:
        list: Kimi tool definitions
    """
    # Start with OpenAI format as base
    openai_tools = get_openai_tools()
    
    kimi_tools = []
    for tool in openai_tools:
        func = tool["function"]
        tool_type = "friction" if func["description"].startswith("FRICTION:") else "emergence"
        
        kimi_tool = {
            "name": func["name"],
            "description": func["description"],
            "parameters": func["parameters"],
            # Kimi-specific metadata
            "_mantic_meta": {
                "version": "1.0.0",
                "domain": func["name"].split("_")[0] if "_" in func["name"] else "general",
                "tool_type": tool_type,
                "requires_clamping": True,
                "deterministic": True
            }
        }
        kimi_tools.append(kimi_tool)
    
    return kimi_tools


def execute(tool_name, params):
    """
    Execute a Mantic tool with given parameters.
    
    Args:
        tool_name: Name of the tool to execute
        params: Dict of parameters
    
    Returns:
        dict: Tool execution result
    
    Raises:
        ValueError: If tool_name is not recognized
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {tool_name}. Available: {list(TOOL_MAP.keys())}")
    
    # Execute the tool
    return TOOL_MAP[tool_name](**params)


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
        tool_type: "friction", "emergence", or "all"
    
    Returns:
        str: Formatted summary
    """
    tools = get_kimi_tools()
    
    if tool_type == "friction":
        tools = [t for t in tools if t["_mantic_meta"]["tool_type"] == "friction"]
        header = "FRICTION TOOLS (Divergence Detection)"
    elif tool_type == "emergence":
        tools = [t for t in tools if t["_mantic_meta"]["tool_type"] == "emergence"]
        header = "EMERGENCE TOOLS (Confluence Detection)"
    else:
        header = "MANTIC EARLY WARNING SYSTEM - ALL TOOLS"
    
    lines = [header, "=" * 50]
    
    for tool in tools:
        name = tool["name"]
        desc = tool["description"].replace("FRICTION: ", "").replace("CONFLUENCE: ", "")
        if len(desc) > 70:
            desc = desc[:67] + "..."
        lines.append(f"\n{name}")
        lines.append(f"  {desc}")
        params = tool["parameters"].get("required", [])
        if params:
            lines.append(f"  Required: {', '.join(params[:4])}{'...' if len(params) > 4 else ''}")
    
    return "\n".join(lines)


def validate_params(tool_name, params):
    """
    Validate parameters for a tool without executing.
    
    Args:
        tool_name: Name of the tool
        params: Dict of parameters to validate
        
    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    tools = get_kimi_tools()
    tool_def = next((t for t in tools if t["name"] == tool_name), None)
    
    if not tool_def:
        return {"valid": False, "errors": [f"Unknown tool: {tool_name}"]}
    
    errors = []
    schema = tool_def["parameters"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    
    # Check required params
    for param in required:
        if param not in params:
            errors.append(f"Missing required parameter: {param}")
    
    # Validate types and ranges
    for param, value in params.items():
        if param not in properties:
            errors.append(f"Unknown parameter: {param}")
            continue
            
        prop_def = properties[param]
        expected_type = prop_def.get("type")
        
        if expected_type == "number":
            if not isinstance(value, (int, float)):
                errors.append(f"{param}: expected number, got {type(value).__name__}")
            else:
                desc = prop_def.get("description", "")
                if "-1 to 1" in desc or "(-1" in desc:
                    if not -1 <= value <= 1:
                        errors.append(f"{param}: value {value} out of range [-1, 1]")
                elif "0-1" in desc or "0 to 1" in desc or "(0-1" in desc:
                    if not 0 <= value <= 1:
                        errors.append(f"{param}: value {value} out of range [0, 1]")
    
    return {"valid": len(errors) == 0, "errors": errors}


def compare_friction_emergence(domain, friction_params, emergence_params):
    """
    Compare friction and emergence results for the same domain.
    
    Args:
        domain: Domain name (healthcare, finance, cyber, climate, legal, military, social)
        friction_params: Params for friction tool
        emergence_params: Params for emergence tool
    
    Returns:
        dict: Comparison results
    """
    friction_map = {
        "healthcare": "healthcare_phenotype_genotype",
        "finance": "finance_regime_conflict",
        "cyber": "cyber_attribution_resolver",
        "climate": "climate_maladaptation",
        "legal": "legal_precedent_drift",
        "military": "military_friction_forecast",
        "social": "social_narrative_rupture"
    }
    
    emergence_map = {
        "healthcare": "healthcare_precision_therapeutic",
        "finance": "finance_confluence_alpha",
        "cyber": "cyber_adversary_overreach",
        "climate": "climate_resilience_multiplier",
        "legal": "legal_precedent_seeding",
        "military": "military_strategic_initiative",
        "social": "social_catalytic_alignment"
    }
    
    if domain not in friction_map:
        return {"error": f"Unknown domain: {domain}"}
    
    friction_result = execute(friction_map[domain], friction_params)
    emergence_result = execute(emergence_map[domain], emergence_params)
    
    return {
        "domain": domain,
        "friction": {
            "tool": friction_map[domain],
            "alert_present": friction_result.get("alert") is not None,
            "m_score": friction_result.get("m_score")
        },
        "emergence": {
            "tool": emergence_map[domain],
            "window_detected": emergence_result.get("window_detected", False),
            "m_score": emergence_result.get("m_score")
        },
        "interpretation": "High M in friction = risk. High M in emergence = opportunity."
    }


if __name__ == "__main__":
    # Test the adapter
    print("=== Kimi Adapter Test (14 Tools) ===\n")
    
    print(get_tool_summary("all"))
    
    print("\n--- Testing Friction vs Emergence ---")
    comparison = compare_friction_emergence(
        "healthcare",
        friction_params={"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
        emergence_params={"genomic_predisposition": 0.85, "environmental_readiness": 0.82,
                         "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90}
    )
    print(f"\nDomain: {comparison['domain']}")
    print(f"Friction Alert: {comparison['friction']['alert_present']}")
    print(f"Emergence Window: {comparison['emergence']['window_detected']}")
    print(f"\n{comparison['interpretation']}")
