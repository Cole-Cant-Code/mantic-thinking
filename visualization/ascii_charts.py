"""
ASCII visualization utilities for Mantic Tools.
Pure box-drawing characters. No emojis.
"""

import math
from typing import List, Dict, Tuple, Optional


def draw_m_gauge(M: float, S: float, width: int = 50) -> str:
    """
    Draw an M-score gauge with color bands.
    
    M: Mantic score (0.0 - 1.0+)
    S: Signal strength (weighted sum)
    """
    filled = int(M * width)
    filled = min(filled, width)  # Cap at width
    
    # Determine band
    if M < 0.3:
        band = "LOW"
        bar_char = "#"
    elif M < 0.7:
        band = "MODERATE"
        bar_char = "="
    else:
        band = "HIGH"
        bar_char = "@"
    
    bar = bar_char * filled + "-" * (width - filled)
    
    lines = [
        "",
        f"  M-SCORE: {M:.3f}  |  SIGNAL: {S:.3f}",
        f"  +{'-' * width}+",
        f"  |{bar}|",
        f"  +{'-' * width}+",
        f"  0.0{' ' * (width - 8)}1.0+",
        f"",
        f"  STATUS: {band} ({'+' if M > 0.7 else '~' if M > 0.3 else '-'})"
    ]
    
    return "\n".join(lines)


def draw_attribution_treemap(
    attribution: List[float],
    labels: List[str],
    width: int = 60,
    height: int = 12
) -> str:
    """
    Draw a treemap showing proportional layer contributions.
    """
    total = sum(attribution) if sum(attribution) > 0 else 1.0
    proportions = [a / total for a in attribution]
    
    # Sort by proportion descending
    indexed = sorted(enumerate(proportions), key=lambda x: x[1], reverse=True)
    
    lines = ["", "  LAYER CONTRIBUTION TREEMAP", "  " + "=" * width, ""]
    
    # Simple horizontal bar approach for terminal
    max_label_len = max(len(l) for l in labels) if labels else 10
    bar_width = width - max_label_len - 15  # Leave room for label, pct, value
    
    for idx, prop in indexed:
        label = labels[idx] if idx < len(labels) else f"Layer-{idx}"
        value = attribution[idx]
        pct = prop * 100
        
        filled = int(prop * bar_width)
        bar = "#" * filled + "." * (bar_width - filled)
        
        # Truncate label if needed
        label = label[:max_label_len].ljust(max_label_len)
        
        if value == 0.0:
            lines.append(f"  {label} [{bar}] {pct:5.1f}% (absent)")
        else:
            lines.append(f"  {label} [{bar}] {pct:5.1f}% ({value:.3f})")
    
    lines.extend(["", "  " + "=" * width])
    return "\n".join(lines)


def draw_domain_hierarchy() -> str:
    """
    Draw the complete tool suite hierarchy.
    """
    tree = """
    MANTIC TOOLS SUITE
    |
    +-- FRICTION (Divergence Detection)
    |   |
    |   +-- healthcare
    |   |   +-- phenotype_genotype_divergence
    |   |
    |   +-- finance
    |   |   +-- liquidity_solvent_insolvency_risk
    |   |
    |   +-- cyber
    |   |   +-- intrusion_breach_forecast
    |   |
    |   +-- climate
    |   |   +-- extreme_weather_cascades
    |   |
    |   +-- legal
    |   |   +-- contract_clause_divergence
    |   |
    |   +-- military
    |   |   +-- kill_chain_friction
    |   |
    |   +-- social
    |       +-- narrative_drift_detector
    |
    +-- EMERGENCE (Confluence Detection)
        |
        +-- healthcare
        |   +-- biomarker_wellness_confluence
        |
        +-- finance
        |   +-- alpha_confluence_detector
        |
        +-- cyber
        |   +-- security_posture_synergy
        |
        +-- climate
        |   +-- resilience_opportunity_mapper
        |
        +-- legal
        |   +-- regulatory_compliance_confluence
        |
        +-- military
        |   +-- force_projection_synergy
        |
        +-- social
            +-- consensus_formation_detector
"""
    return tree


def draw_cross_model_matrix(
    results: Dict[str, Dict[str, float]],
    domains: List[str] = None
) -> str:
    """
    Draw a matrix showing M-scores across models and domains.
    
    results: {model: {domain: M_score}}
    """
    if not domains:
        domains = list(next(iter(results.values())).keys())
    
    models = list(results.keys())
    
    # Column widths
    domain_width = max(len(d) for d in domains) + 2
    model_width = 10
    
    lines = ["", "  CROSS-MODEL AGREEMENT MATRIX", ""]
    
    # Header row
    header = "  " + "Domain".ljust(domain_width)
    for model in models:
        header += model[:8].center(model_width)
    lines.append(header)
    lines.append("  " + "-" * (domain_width + len(models) * model_width))
    
    # Data rows
    for domain in domains:
        row = "  " + domain.ljust(domain_width)
        scores = []
        for model in models:
            score = results.get(model, {}).get(domain, 0.0)
            scores.append(score)
            row += f"{score:0.2f}".center(model_width)
        
        # Add variance indicator
        variance = max(scores) - min(scores) if scores else 0
        if variance < 0.05:
            row += "  [ok]"
        elif variance < 0.15:
            row += "  [~]"
        else:
            row += "  [!]"
        
        lines.append(row)
    
    lines.append("")
    return "\n".join(lines)


def draw_temporal_cascade(
    times: List[float],
    kernel_values: List[float],
    width: int = 60,
    height: int = 15
) -> str:
    """
    Draw an ASCII line chart of temporal kernel values.
    """
    if not times or not kernel_values:
        return "No data to plot"
    
    lines = ["", "  TEMPORAL KERNEL EVOLUTION", ""]
    
    # Determine scale
    max_val = max(kernel_values) if max(kernel_values) > 0 else 1.0
    min_val = min(kernel_values)
    
    # Plot area
    plot_height = height - 4  # Leave room for axes
    
    # Create y-axis labels and grid
    y_labels = []
    grid_lines = []
    
    for i in range(plot_height):
        y_val = max_val * (1 - i / (plot_height - 1))
        y_labels.append(f"{y_val:.2f}")
        grid_lines.append(" " * width)
    
    # Map points to grid
    x_step = max(1, len(times) // width)
    sampled_indices = list(range(0, len(times), x_step))[:width]
    
    for col, idx in enumerate(sampled_indices):
        val = kernel_values[idx]
        row = int((1 - val / max_val) * (plot_height - 1)) if max_val > 0 else plot_height // 2
        row = max(0, min(plot_height - 1, row))
        
        # Place marker
        line = list(grid_lines[row])
        line[col] = "*"
        grid_lines[row] = "".join(line)
    
    # Assemble
    label_width = 6
    for i, (label, grid) in enumerate(zip(y_labels, grid_lines)):
        prefix = label.rjust(label_width) + " |"
        lines.append(f"  {prefix}{grid}")
    
    # X-axis
    lines.append(f"  {' ' * label_width} +{'-' * len(sampled_indices)}")
    
    # X labels (start, middle, end)
    t_start = times[0]
    t_end = times[-1]
    t_mid = times[len(times) // 2]
    
    x_label = f"  {' ' * label_width}  {t_start:.1f}"
    mid_pos = len(sampled_indices) // 2 - 3
    end_pos = len(sampled_indices) - 6
    x_label += " " * (mid_pos - len(x_label) + label_width + 2) + f"{t_mid:.1f}"
    x_label += " " * (end_pos - mid_pos - 3) + f"{t_end:.1f}"
    lines.append(x_label)
    
    lines.append("")
    return "\n".join(lines)


def draw_friction_emergence_balance(
    friction_scores: Dict[str, float],
    emergence_scores: Dict[str, float]
) -> str:
    """
    Draw a balance scale comparing friction vs emergence across domains.
    """
    domains = sorted(set(friction_scores.keys()) | set(emergence_scores.keys()))
    
    lines = [
        "",
        "  FRICTION / EMERGENCE BALANCE",
        "",
        "       FRICTION          EMERGENCE",
        "       ========          =========",
        ""
    ]
    
    for domain in domains:
        f = friction_scores.get(domain, 0.0)
        e = emergence_scores.get(domain, 0.0)
        
        # Bar representation
        f_bar = "#" * int(f * 20)
        e_bar = "=" * int(e * 20)
        
        # Pad to consistent width
        f_bar = f_bar.ljust(20)
        e_bar = e_bar.ljust(20)
        
        # Indicator
        if f > e + 0.3:
            indicator = "<<"
        elif e > f + 0.3:
            indicator = ">>"
        else:
            indicator = "~~"
        
        lines.append(f"  {domain[:12].ljust(12)} [{f_bar}] {indicator} [{e_bar}]")
    
    lines.extend([
        "",
        "  Legend: # = Risk weight   = = Opportunity weight",
        ""
    ])
    
    return "\n".join(lines)


def draw_kernel_comparison(
    t: float,
    n: float = 1.0,
    alpha: float = 0.1,
    width: int = 50
) -> str:
    """
    Compare all 7 kernel modes side by side.
    """
    from core.mantic_kernel import compute_temporal_kernel
    
    modes = [
        "exponential",
        "linear", 
        "logistic",
        "s_curve",
        "power_law",
        "oscillatory",
        "memory"
    ]
    
    lines = ["", "  KERNEL MODE COMPARISON", f"  t={t}, n={n}, alpha={alpha}", ""]
    
    max_label = max(len(m) for m in modes)
    
    for mode in modes:
        try:
            val = compute_temporal_kernel(t, n=n, alpha=alpha, kernel_type=mode)
        except:
            val = 0.0
        
        bar_len = int(val * width)
        bar = "#" * bar_len + "." * (width - bar_len)
        
        label = mode.ljust(max_label)
        lines.append(f"  {label} [{bar}] {val:.3f}")
    
    lines.append("")
    return "\n".join(lines)


# Demo output
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Sample data
    W = [0.25, 0.25, 0.25, 0.25]
    L = [0.8, 0.6, 0.4, 0.2]
    I = [1.0, 1.0, 1.0, 1.0]
    
    from core.mantic_kernel import mantic_kernel
    M, S, attr = mantic_kernel(W, L, I)
    
    print(draw_m_gauge(M, S))
    print()
    print(draw_attribution_treemap(attr, ["Genetic", "Clinical", "Behavior", "EHR"]))
    print()
    print(draw_kernel_comparison(t=10.0))
