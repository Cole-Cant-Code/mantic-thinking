"""
Finance: Confluence Alpha Engine

Detects asymmetric opportunity when technical setup, macro tailwind,
flow positioning, and risk compression achieve directional harmony.

Confluence Logic: Technical/Macro aligned + Flow against crowd + Risk OK

Optional Overrides (Bounded):
    threshold_override: Dict of threshold overrides
        e.g., {"alignment": 0.65, "flow_extreme": 0.55, "risk_ok": 0.55, "tech_macro_gap": 0.25}
    temporal_config: Dict for temporal kernel tuning (domain-restricted)
    
    NOTE: Domain weights (W) are IMMUTABLE.

Output:
    window_detected, setup_quality, conviction_score, m_score, overrides_applied
"""

import sys
import os

# Avoid mutating sys.path on import; only adjust for direct script execution.
if __name__ == "__main__":
    _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

import numpy as np
from core.safe_kernel import safe_mantic_kernel as mantic_kernel
from core.mantic_kernel import compute_temporal_kernel
from core.validators import (
    clamp_input, require_finite_inputs, format_attribution,
    clamp_threshold_override, validate_temporal_config,
    clamp_f_time, build_overrides_audit
)
from mantic.introspection import get_layer_visibility


WEIGHTS = [0.30, 0.30, 0.20, 0.20]
LAYER_NAMES = ['technical', 'macro', 'flow', 'risk']

DEFAULT_THRESHOLDS = {
    'alignment': 0.60,       # Technical/macro alignment threshold
    'flow_extreme': 0.50,    # Flow extreme threshold
    'risk_ok': 0.50,         # Risk OK threshold
    'tech_macro_gap': 0.20   # Technical/macro max gap
}

DOMAIN = "finance"


def detect(technical_setup, macro_tailwind, flow_positioning, risk_compression,
           f_time=1.0, threshold_override=None, temporal_config=None):
    """Detect asymmetric opportunity when directional harmony achieved."""
    
    # INPUT VALIDATION
    require_finite_inputs({
        "technical_setup": technical_setup,
        "macro_tailwind": macro_tailwind,
        "flow_positioning": flow_positioning,
        "risk_compression": risk_compression,
    })

    # OVERRIDES PROCESSING
    threshold_info = {}
    active_thresholds = DEFAULT_THRESHOLDS.copy()
    ignored_threshold_keys = []
    
    if threshold_override and isinstance(threshold_override, dict):
        for key, requested in threshold_override.items():
            if key in DEFAULT_THRESHOLDS:
                clamped_val, was_clamped, info = clamp_threshold_override(
                    requested, DEFAULT_THRESHOLDS[key]
                )
                active_thresholds[key] = clamped_val
                threshold_info[key] = info
            else:
                ignored_threshold_keys.append(key)
    
    temporal_validated, temporal_rejected, temporal_clamped = None, {}, {}
    temporal_applied = None
    if temporal_config and isinstance(temporal_config, dict):
        temporal_validated, temporal_rejected, temporal_clamped = validate_temporal_config(
            temporal_config, domain=DOMAIN
        )
        if "kernel_type" not in temporal_validated:
            if "kernel_type" not in temporal_rejected:
                temporal_rejected["kernel_type"] = {
                    "requested": temporal_config.get("kernel_type"),
                    "reason": "kernel_type required and must be allowed for domain"
                }
        if "t" not in temporal_validated:
            if "t" not in temporal_rejected:
                temporal_rejected["t"] = {
                    "requested": temporal_config.get("t"),
                    "reason": "t required for temporal_config"
                }
        if "kernel_type" in temporal_validated and "t" in temporal_validated:
            f_time = compute_temporal_kernel(**temporal_validated)
            temporal_applied = temporal_validated
    
    f_time_clamped, _, f_time_info = clamp_f_time(f_time)
    
    # CORE DETECTION
    L_raw = [
        clamp_input(technical_setup, name="technical_setup"),
        clamp_input(macro_tailwind, name="macro_tailwind"),
        clamp_input(flow_positioning, min_val=-1, max_val=1, name="flow_positioning"),
        clamp_input(risk_compression, name="risk_compression")
    ]
    
    L_normalized = [
        L_raw[0],
        L_raw[1],
        (L_raw[2] + 1) / 2,  # Convert -1,1 to 0,1
        L_raw[3]
    ]
    
    # Interaction terms (respecting original logic)
    flow_boost = abs(L_raw[2]) * 0.2
    I = [min(1.0, 0.9 + flow_boost), 1.0, min(1.0, 0.9 + flow_boost * 1.5), 1.0]
    
    M, S, attr = mantic_kernel(WEIGHTS, L_normalized, I, f_time_clamped)
    
    alignment_threshold = active_thresholds['alignment']
    flow_extreme_threshold = active_thresholds['flow_extreme']
    risk_ok_threshold = active_thresholds['risk_ok']
    tech_macro_gap_max = active_thresholds['tech_macro_gap']
    
    technical_macro_gap = abs(L_raw[0] - L_raw[1])
    technical_macro_aligned = technical_macro_gap < tech_macro_gap_max and L_raw[0] > alignment_threshold
    flow_favorable = abs(L_raw[2]) > flow_extreme_threshold
    flow_direction = "long" if L_raw[2] < 0 else "short"
    risk_ok = L_raw[3] > risk_ok_threshold
    # Flow can be contrarian (negative) and still favorable; require non-flow layers > 0.5
    all_favorable = min(L_raw[0], L_raw[1], L_raw[3]) > 0.5
    
    window_detected = False
    setup_quality = None
    conviction_score = 0.0
    edge_source = None
    recommended_action = None
    stop_loss = None
    risk_reward = None
    
    if technical_macro_aligned and flow_favorable and risk_ok and all_favorable:
        window_detected = True
        
        base_conviction = (L_raw[0] + L_raw[1]) / 2
        flow_boost_factor = 1 + abs(L_raw[2]) * 0.2
        conviction_score = min(base_conviction * flow_boost_factor, 1.0)
        
        if conviction_score > 0.85 and min(L_raw[0], L_raw[1]) > 0.75:
            setup_quality = "HIGH_CONVICTION"
            edge_source = "Strong Technical/Macro harmony + Extreme flow against crowd"
            recommended_action = f"Enter full position size ({flow_direction})"
            stop_loss = "Technical setup invalidation or flow extreme mean reversion"
            risk_reward = "Asymmetric favorable (3:1 or better)"
        else:
            setup_quality = "MODERATE_CONVICTION"
            edge_source = "Technical/Macro aligned with flow tailwind"
            recommended_action = f"Enter half position size ({flow_direction})"
            stop_loss = "Technical support/resistance break"
            risk_reward = "Favorable (2:1)"
    
    # Build audit
    threshold_clamped_any = any(
        info.get("was_clamped", False) 
        for info in threshold_info.values()
    ) if threshold_info else False
    
    threshold_audit_info = None
    if threshold_info:
        threshold_audit_info = {
            "overrides": {
                key: {
                    "requested": info.get("requested"),
                    "used": info.get("used"),
                    "was_clamped": info.get("was_clamped", False)
                }
                for key, info in threshold_info.items()
            },
            "was_clamped": threshold_clamped_any,
            "ignored_keys": ignored_threshold_keys if ignored_threshold_keys else None
        }
    
    overrides_applied = build_overrides_audit(
        threshold_overrides=threshold_override if threshold_override else None,
        temporal_config=temporal_config if temporal_config else None,
        threshold_info=threshold_audit_info,
        temporal_validated=temporal_applied,
        temporal_rejected=temporal_rejected if temporal_rejected else None,
        temporal_clamped=temporal_clamped if temporal_clamped else None,
        f_time_info=f_time_info
    )
    
    _weights_dict = dict(zip(LAYER_NAMES, WEIGHTS))
    _layer_values_dict = dict(zip(LAYER_NAMES, L_normalized))
    layer_visibility = get_layer_visibility("finance_confluence_alpha", _weights_dict, _layer_values_dict)
    
    if window_detected:
        return {
            "window_detected": True,
            "setup_quality": setup_quality,
            "conviction_score": float(conviction_score),
            "edge_source": edge_source,
            "recommended_action": recommended_action,
            "stop_loss": stop_loss,
            "risk_reward": risk_reward,
            "m_score": float(M),
            "spatial_component": float(S),
            "layer_attribution": format_attribution(attr, LAYER_NAMES),
            "thresholds": active_thresholds,
            "overrides_applied": overrides_applied,
            "flow_raw": float(L_raw[2]),
            "technical_macro_gap": float(technical_macro_gap),
            "position_direction": flow_direction,
            "layer_visibility": layer_visibility
        }
    
    missing = []
    if not technical_macro_aligned:
        missing.append("Technical/Macro divergence")
    if not flow_favorable:
        missing.append("Flow not extreme enough")
    if not risk_ok:
        missing.append("Risk environment unfavorable")
    
    return {
        "window_detected": False,
        "status": "Confluence not achieved",
        "reason": "; ".join(missing) if missing else "Layers below threshold",
        "m_score": float(M),
        "spatial_component": float(S),
        "layer_attribution": format_attribution(attr, LAYER_NAMES),
        "thresholds": active_thresholds,
        "overrides_applied": overrides_applied,
        "technical_macro_aligned": technical_macro_aligned,
        "flow_favorable": flow_favorable,
        "risk_ok": risk_ok,
        "layer_visibility": layer_visibility
    }


if __name__ == "__main__":
    print("=== Finance Confluence Alpha Engine ===\n")
    
    print("Test 1: High conviction (crowd short, technical/macro bullish)")
    result = detect(
        technical_setup=0.85,
        macro_tailwind=0.80,
        flow_positioning=0.75,
        risk_compression=0.70
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Quality: {result.get('setup_quality', 'N/A')}\n")
    
    print("Test 2: Moderate conviction")
    result = detect(
        technical_setup=0.70,
        macro_tailwind=0.65,
        flow_positioning=-0.60,
        risk_compression=0.60
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Quality: {result.get('setup_quality', 'N/A')}\n")
    
    print("Test 3: No confluence")
    result = detect(
        technical_setup=0.75,
        macro_tailwind=0.70,
        flow_positioning=-0.20,
        risk_compression=0.65
    )
    print(f"  Window Detected: {result['window_detected']}")
    print(f"  Reason: {result.get('reason', 'N/A')}")
