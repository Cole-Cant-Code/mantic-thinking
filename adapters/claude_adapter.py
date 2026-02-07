"""
Claude Adapter for Mantic Tools

Converts Mantic tools to Claude Computer Use format.
Optimized for Claude Code CLI integration.

Includes both Friction tools (7) and Emergence tools (7) = 14 total.
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import inspect

from adapters.openai_adapter import TOOL_MAP, get_openai_tools, get_tools_by_type


def get_claude_tools():
    """
    Return Claude Computer Use format for all 14 Mantic tools.
    
    Returns:
        list: Claude tool definitions
    """
    openai_tools = get_openai_tools()
    
    claude_tools = []
    for tool in openai_tools:
        func = tool["function"]
        tool_type = "friction" if func["description"].startswith("FRICTION:") else "emergence"
        
        claude_tool = {
            "name": func["name"],
            "description": func["description"],
            "input_schema": func["parameters"],
            # Claude-specific metadata
            "_claude_meta": {
                "tool_type": tool_type,
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
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments
        
    Returns:
        dict: Tool execution result with Claude-friendly formatting
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Filter arguments to only those expected by the function
    func = TOOL_MAP[tool_name]
    sig = inspect.signature(func)
    valid_params = set(sig.parameters.keys())
    filtered_args = {k: v for k, v in arguments.items() if k in valid_params}

    result = func(**filtered_args)
    
    # Determine if this is friction or emergence
    tool_def = next((t for t in get_claude_tools() if t["name"] == tool_name), None)
    tool_type = tool_def["_claude_meta"]["tool_type"] if tool_def else "unknown"
    
    # Add Claude-specific metadata to result
    return {
        **result,
        "_claude_meta": {
            "tool_used": tool_name,
            "tool_type": tool_type,
            "execution_successful": True,
            "requires_followup": (
                result.get("alert") is not None or 
                result.get("window_detected", False) is True
            )
        }
    }


def format_for_claude(result, tool_name=None):
    """
    Format a Mantic result for Claude's consumption.
    
    Creates a human-readable summary suitable for Claude to interpret
    and act upon.
    
    Args:
        result: Raw tool result dict
        tool_name: Optional name of the tool that produced the result
        
    Returns:
        str: Formatted summary
    """
    # Detect tool type from result structure
    is_friction = "alert" in result and "window_detected" not in result
    is_emergence = "window_detected" in result
    
    lines = []
    
    if tool_name:
        lines.append(f"## Mantic Analysis: {tool_name}")
    else:
        lines.append("## Mantic Analysis Result")
    
    # Friction tools output
    if is_friction:
        lines.append("\n**Type**: FRICTION (Divergence Detection)")
        
        if result.get("alert"):
            lines.append(f"\n⚠️  **ALERT**: {result['alert']}")
        else:
            lines.append("\n✅ No friction detected. Systems aligned within normal parameters.")
        
        # Domain-specific fields
        if "severity" in result:
            lines.append(f"**Severity**: {result['severity']:.2f}")
        if "confidence" in result:
            lines.append(f"**Confidence**: {result['confidence']}")
        if "decision" in result:
            lines.append(f"**Decision**: {result['decision'].upper()}")
        if "bottleneck" in result:
            lines.append(f"**Bottleneck**: {result['bottleneck']}")
        if "drift_direction" in result:
            lines.append(f"**Drift Direction**: {result['drift_direction']}")
        if "rupture_timing" in result:
            lines.append(f"**Rupture Timing**: {result['rupture_timing']}")
    
    # Emergence tools output
    elif is_emergence:
        lines.append("\n**Type**: CONFLUENCE (Alignment Detection)")
        
        if result.get("window_detected"):
            lines.append("\n🎯 **WINDOW DETECTED**: Favorable alignment across layers")
            if "window_type" in result:
                lines.append(f"**Type**: {result['window_type']}")
            elif "movement_potential" in result:
                lines.append(f"**Potential**: {result['movement_potential']}")
            elif "maneuver_type" in result:
                lines.append(f"**Maneuver**: {result['maneuver_type']}")
            elif "intervention_type" in result:
                lines.append(f"**Intervention**: {result['intervention_type']}")
        else:
            lines.append("\n⏳ No alignment window. Conditions not yet favorable.")
        
        # Domain-specific fields
        if "confidence" in result:
            lines.append(f"**Confidence**: {result['confidence']:.2f}")
        if "conviction_score" in result:
            lines.append(f"**Conviction**: {result['conviction_score']:.2f}")
        if "alignment_floor" in result:
            lines.append(f"**Alignment Floor**: {result['alignment_floor']:.2f}")
        if "catalyst_score" in result:
            lines.append(f"**Catalyst Score**: {result['catalyst_score']:.2f}")
    
    # M-score (always present)
    m_score = result.get("m_score", 0)
    lines.append(f"\n**M-Score**: {m_score:.3f}")
    
    # Recommendations
    if result.get("strategy_pivot"):
        lines.append(f"\n**Strategy Pivot**: {result['strategy_pivot']}")
    if result.get("alternative_suggestion"):
        lines.append(f"\n**Alternative**: {result['alternative_suggestion']}")
    if result.get("recommended_adjustment"):
        lines.append(f"\n**Adjustment**: {result['recommended_adjustment']}")
    if result.get("mismatch_explanation"):
        lines.append(f"\n**Explanation**: {result['mismatch_explanation']}")
    
    # Emergence-specific recommendations
    if result.get("recommended_action"):
        lines.append(f"\n**Recommended Action**: {result['recommended_action']}")
    if result.get("duration_estimate"):
        lines.append(f"**Duration**: {result['duration_estimate']}")
    if result.get("execution_window"):
        lines.append(f"**Execution Window**: {result['execution_window']}")
    
    # Layer attribution
    if result.get("layer_attribution"):
        lines.append("\n**Layer Contributions**:")
        for layer, pct in result["layer_attribution"].items():
            bar = "█" * int(pct * 20)
            lines.append(f"  - {layer}: {pct:.1%} {bar}")
    
    return "\n".join(lines)


def get_claude_prompt_addon():
    """
    Get additional prompt context for Claude to understand Mantic tools.
    
    Returns:
        str: Prompt addon explaining how to use Mantic tools
    """
    return """
## Using Mantic Early Warning Tools (14 Total)

You have access to 14 cross-domain detection tools based on the Mantic Framework:

**Core Formula**: M = (sum(W * L * I)) * f(t) / k_n

### Tool Types

**FRICTION Tools (7)**: Detect cross-layer conflicts and mismatches
- Use when: Assessing risks, detecting anomalies, finding bottlenecks
- High M-score indicates: Problems, divergences, risks
- Output: Alerts, warnings, risk ratings

**CONFLUENCE Tools (7)**: Detect alignment windows and opportunities
- Use when: Seeking optimal timing, alignment windows, high-leverage interventions
- High M-score indicates: Opportunities, favorable alignments, windows
- Output: Window detected, recommendations, timing guidance

### All Tools by Domain

**Healthcare**:
- friction: healthcare_phenotype_genotype (detect mismatches)
- emergence: healthcare_precision_therapeutic (find optimal treatment windows)

**Finance**:
- friction: finance_regime_conflict (detect market regime conflicts)
- emergence: finance_confluence_alpha (find high-conviction setups)

**Cyber**:
- friction: cyber_attribution_resolver (assess attribution confidence)
- emergence: cyber_adversary_overreach (find defensive advantage windows)

**Climate**:
- friction: climate_maladaptation (prevent harmful interventions)
- emergence: climate_resilience_multiplier (find multi-benefit solutions)

**Legal**:
- friction: legal_precedent_drift (detect judicial philosophy shifts)
- emergence: legal_precedent_seeding (find precedent-setting windows)

**Military**:
- friction: military_friction_forecast (identify operational bottlenecks)
- emergence: military_strategic_initiative (find decisive action windows)

**Social**:
- friction: social_narrative_rupture (detect narrative ruptures)
- emergence: social_catalytic_alignment (find movement-building windows)

### Interpretation Guide

- **M-Score**: 0-1 anomaly/intensity score (higher = more significant)
- **Friction**: High M + Alert present = Action needed to mitigate risk
- **Emergence**: High M + Window detected = Action needed to seize opportunity
- **Layer Attribution**: Shows which input factors are driving the result

Use Friction tools for risk assessment and Emergence tools for opportunity detection.
They are complementary - the same high M-score means opposite things depending on tool type.
"""


def get_summary_by_type(tool_type="all"):
    """
    Get a summary of tools organized by type.
    
    Args:
        tool_type: "friction", "emergence", or "all"
    
    Returns:
        str: Formatted summary
    """
    tools = get_claude_tools()
    
    if tool_type == "friction":
        tools = [t for t in tools if t["_claude_meta"]["tool_type"] == "friction"]
        header = "FRICTION TOOLS (Divergence/Risk Detection)"
    elif tool_type == "emergence":
        tools = [t for t in tools if t["_claude_meta"]["tool_type"] == "emergence"]
        header = "CONFLUENCE TOOLS (Alignment/Opportunity Detection)"
    else:
        header = "ALL MANTIC TOOLS"
    
    lines = [header, "=" * 50]
    
    for tool in tools:
        name = tool["name"]
        ttype = tool["_claude_meta"]["tool_type"].upper()
        desc = tool["description"].replace("FRICTION: ", "").replace("CONFLUENCE: ", "")
        if len(desc) > 60:
            desc = desc[:57] + "..."
        lines.append(f"\n[{ttype}] {name}")
        lines.append(f"  {desc}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test the adapter
    print("=== Claude Adapter Test (14 Tools) ===\n")
    
    print(get_summary_by_type("all"))
    
    print("\n--- Executing Friction Tool ---")
    result = execute_tool("healthcare_phenotype_genotype", {
        "phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8
    })
    print(format_for_claude(result, "healthcare_phenotype_genotype"))
    
    print("\n\n--- Executing Emergence Tool ---")
    result = execute_tool("healthcare_precision_therapeutic", {
        "genomic_predisposition": 0.85, "environmental_readiness": 0.82,
        "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90
    })
    print(format_for_claude(result, "healthcare_precision_therapeutic"))
