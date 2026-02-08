# Mantic Early Warning System - Universal Manifest

**name:** mantic-early-warning  
**version:** 1.3.0
**description:** Cross-domain anomaly and opportunity detection using 4-layer hierarchical analysis  
**author:** Mantic Framework  
**license:** Elastic License 2.0 (Source-Available) / Commercial licenses available  
**models:** [claude, kimi, gemini, codex, gpt-4o]

---

## Core Formula (IMMUTABLE)

```
M = (sum(W * L * I)) * f(t) / k_n
```

Where:
- **M**: Final mantic score (anomaly/opportunity intensity)
- **W**: Array of 4 weights (must sum to 1)
- **L**: Array of 4 layer values (0-1 range)
- **I**: Array of 4 interaction coefficients (0-1)
- **f(t)**: Temporal kernel value (default 1.0)
- **k_n**: Normalization constant (default 1.0)

**Layers:** [micro, meso, macro, meta] mapped to domain-specific inputs

---

## Temporal Kernels

Models can pre-compute `f_time` using `compute_temporal_kernel()` before calling any `detect()` tool.
This allows time-aware scoring — signals decay, grow, saturate, or oscillate depending on the mode.

### Usage

```python
from mantic_thinking.core.mantic_kernel import compute_temporal_kernel

# Compute temporal modifier, then pass to any tool
f_time = compute_temporal_kernel(t=5, n=1.0, alpha=0.1, kernel_type="exponential")
result = detect(..., f_time=f_time)
```

### Parameters

- **t**: Time delta (0 = now, positive = future, negative = past)
- **n**: Novelty — how unusual the pattern is (>0 amplifies, <0 attenuates)
- **alpha**: Sensitivity — how reactive to novelty over time
- **kernel_type**: Which temporal model to use

### Available Modes

| Mode | When to Use | Example Domain |
|------|-------------|----------------|
| `exponential` | Viral spread, cascade growth/decay | Social narrative rupture |
| `logistic` | Saturation, carrying capacity | Legal precedent drift |
| `s_curve` | Adoption curves, learning onset | Healthcare therapeutic windows |
| `power_law` | Heavy-tailed, long-memory dynamics | Climate maladaptation |
| `oscillatory` | Seasonal, cyclical patterns | Finance regime conflicts |
| `memory` | Decaying influence of past events | Military strategic initiative |
| `linear` | Simple linear decay | General purpose |

### Mode-Specific Parameters

- **s_curve**: `t0` — inflection point (default 0.0)
- **power_law**: `exponent` — power coefficient (default 1.0)
- **oscillatory**: `frequency` — oscillation frequency (default 1.0)
- **memory**: `memory_strength` — initial memory weight (default 1.0)

> **Warning:** The `exponential` mode with positive `n` and `alpha` produces **growth**, not decay.
> Use `n=-1` for decay behavior (matching old `decay_rate` parameter).

> **Note:** `power_law` requires `t >= -1`. Values below this are clamped.

---

## Tool Suites

The Mantic Framework provides **14 tools** across 7 domains, with two complementary detection modes:

### Friction Suite (7 tools)
**Logic:** Detects divergences and risks (per-tool thresholds; see each tool's DEFAULT_THRESHOLDS)
**Use:** Risk assessment, anomaly detection, bottleneck identification  
**Output:** Alerts, warnings, risk ratings

### Emergence Suite (7 tools)
**Logic:** Detects alignments and opportunities (per-tool thresholds; see each tool's DEFAULT_THRESHOLDS)
**Use:** Optimal timing, high-leverage interventions, window detection  
**Output:** Window detected, recommendations, timing guidance

---

## Friction Tools (Divergence Detection)

### 1. healthcare_phenotype_genotype
**Name:** Healthcare: Phenotype-Genotype Mismatch Detector  
**Description:** Detects when genomic risk doesn't match phenotypic presentation, indicating environmental buffering or psychosocial resilience

**Input Layers:**
| Layer | Description | Type | Required |
|-------|-------------|------|----------|
| phenotypic | Current symptoms/vitals (0-1) | float | yes |
| genomic | Genetic risk score (0-1) | float | yes |
| environmental | Exposure load (0-1) | float | yes |
| psychosocial | Stress/resilience (0-1) | float | yes |

**Output:**
```json
{
  "alert": "string - detection message",
  "severity": "float 0-1",
  "buffering_layer": "string - which layer is buffering",
  "m_score": "float - final mantic score",
  "spatial_component": "float - S value",
  "layer_attribution": "object - percentage contribution per layer"
}
```

**Trigger Threshold:** 0.4

---

### 2. finance_regime_conflict
**Name:** Finance: Regime Conflict Monitor  
**Description:** Spots when technical price action contradicts fundamentals, flow, or risk signals

**Input Layers:**
| Layer | Description | Type | Range |
|-------|-------------|------|-------|
| technical | Price action signals | float | 0-1 |
| macro | Fundamental indicators | float | 0-1 |
| flow | Capital flow direction | float | [-1, 1] |
| risk | Risk appetite metrics | float | 0-1 |

**Output:**
```json
{
  "alert": "string",
  "conflict_type": "string - type of regime conflict",
  "confidence": "float 0-1",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

### 3. cyber_attribution_resolver
**Name:** Cybersecurity: Attribution Uncertainty Resolver  
**Description:** Scores confidence when technical sophistication doesn't align with geopolitical context

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| technical | Technical sophistication indicators | float |
| threat_intel | Threat intelligence confidence | float |
| operational_impact | Severity of operational impact | float |
| geopolitical | Geopolitical context alignment | float |

**Output:**
```json
{
  "alert": "string",
  "confidence": "string - high/medium/low",
  "mismatch_explanation": "string",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

### 4. climate_maladaptation
**Name:** Climate: Maladaptation Preventer  
**Description:** Blocks solutions that solve immediate micro problems but create macro/meta harms

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| atmospheric | Atmospheric condition metrics | float |
| ecological | Ecosystem health indicators | float |
| infrastructure | Infrastructure resilience | float |
| policy | Policy coherence score | float |

**Output:**
```json
{
  "alert": "string",
  "decision": "string - proceed/caution/block",
  "alternative_suggestion": "string",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

### 5. legal_precedent_drift
**Name:** Legal: Precedent Drift Alert  
**Description:** Warns when judicial philosophy shifts threaten current precedent-based strategies

**Input Layers:**
| Layer | Description | Type | Range |
|-------|-------------|------|-------|
| black_letter | Statutory text alignment | float | 0-1 |
| precedent | Precedent consistency | float | 0-1 |
| operational | Practical implementation | float | 0-1 |
| socio_political | Social/political context | float | [-1, 1] |

**Output:**
```json
{
  "alert": "string",
  "drift_direction": "string - left/right/fragmenting",
  "strategy_pivot": "string - recommended strategy adjustment",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

### 6. military_friction_forecast
**Name:** Military: Friction Forecast Engine  
**Description:** Identifies where tactical plans hit logistics or political constraints

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| maneuver | Tactical maneuver feasibility | float |
| intelligence | Intelligence confidence | float |
| sustainment | Logistics sustainability | float |
| political | Political authorization level | float |

**Output:**
```json
{
  "alert": "string",
  "bottleneck": "string - which layer is the constraint",
  "risk_rating": "string - high/medium/low",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

### 7. social_narrative_rupture
**Name:** Social/Cultural: Narrative Rupture Detector  
**Description:** Catches virality that outpaces institutional sense-making capacity

**Input Layers:**
| Layer | Description | Type | Range |
|-------|-------------|------|-------|
| individual | Individual sentiment velocity | float | 0-1 |
| network | Network propagation speed | float | 0-1 |
| institutional | Institutional response lag | float | 0-1 |
| cultural | Cultural archetype alignment | float | [-1, 1] |

**Output:**
```json
{
  "alert": "string",
  "rupture_timing": "string - imminent/ongoing/contained",
  "recommended_adjustment": "string",
  "m_score": "float",
  "spatial_component": "float",
  "layer_attribution": "object"
}
```

---

## Emergence Tools (Confluence Detection)

### 1. healthcare_precision_therapeutic
**Name:** Healthcare: Precision Therapeutic Window  
**Description:** Identifies rare alignment of genomic predisposition, environmental readiness, phenotypic timing, and psychosocial engagement for maximum treatment efficacy

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| genomic_predisposition | Genetic readiness for treatment (0-1) | float |
| environmental_readiness | Exposure/toxin levels favorable (0-1) | float |
| phenotypic_timing | Disease progression stage optimal (0-1) | float |
| psychosocial_engagement | Patient motivation/support high (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "window_type": "string - OPTIMAL/FAVORABLE",
  "confidence": "float 0-1",
  "m_score": "float",
  "alignment_floor": "float - minimum layer value",
  "limiting_factor": "string - weakest layer",
  "recommended_action": "string",
  "duration_estimate": "string"
}
```

**Confluence Threshold:** 0.65 (all layers must exceed)

---

### 2. finance_confluence_alpha
**Name:** Finance: Confluence Alpha Engine  
**Description:** Detects asymmetric opportunity when technical setup, macro tailwind, flow positioning, and risk compression achieve directional harmony

**Input Layers:**
| Layer | Description | Type | Range |
|-------|-------------|------|-------|
| technical_setup | Technical indicators favorable | float | 0-1 |
| macro_tailwind | Fundamental/macro support | float | 0-1 |
| flow_positioning | Crowd positioning (extreme = signal) | float | [-1, 1] |
| risk_compression | Risk appetite favorable | float | 0-1 |

**Output:**
```json
{
  "window_detected": "boolean",
  "setup_quality": "string - HIGH/MODERATE_CONVICTION",
  "conviction_score": "float 0-1",
  "edge_source": "string",
  "recommended_action": "string",
  "stop_loss": "string",
  "m_score": "float"
}
```

---

### 3. cyber_adversary_overreach
**Name:** Cybersecurity: Adversary Overreach Detector  
**Description:** Identifies defensive advantage windows when attacker TTPs are stretched, geopolitically pressured, and operationally fatigued

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| threat_intel_stretch | Attacker TTPs overextended/visible (0-1) | float |
| geopolitical_pressure | External pressure on attacker (0-1) | float |
| operational_hardening | Defender readiness/hardening (0-1) | float |
| tool_reuse_fatigue | Attacker tool reuse/indicators (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "attacker_state": "string - RESILIENT/STRESSED/OVEREXTENDED",
  "defender_advantage": "string - LOW/MODERATE/HIGH/CRITICAL",
  "attacker_strain_score": "float 0-1",
  "recommended_action": "string",
  "duration_estimate": "string",
  "counter_attack_viability": "string",
  "m_score": "float"
}
```

---

### 4. climate_resilience_multiplier
**Name:** Climate: Resilience Multiplier  
**Description:** Surfaces interventions with positive cross-domain coupling solving multiple layer problems simultaneously

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| atmospheric_benefit | Atmospheric/climate benefit (0-1) | float |
| ecological_benefit | Ecosystem benefit (0-1) | float |
| infrastructure_benefit | Infrastructure resilience benefit (0-1) | float |
| policy_alignment | Policy coherence/support (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "intervention_type": "string - MULTIPLIER/HIGH_MULTIPLIER",
  "cross_domain_coupling": "float 0-1",
  "benefit_layers_above_70": "integer 0-4",
  "example_intervention": "string",
  "funding_priority": "string",
  "m_score": "float"
}
```

---

### 5. legal_precedent_seeding
**Name:** Legal: Precedent Seeding Optimizer  
**Description:** Spots windows when socio-political climate, institutional capacity, statutory ambiguity, and circuit splits align for favorable case law establishment

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| socio_political_climate | Receptiveness to legal change (0-1) | float |
| institutional_capacity | Courts/resources to handle case (0-1) | float |
| statutory_ambiguity | Statutory text ambiguity/openness (0-1) | float |
| circuit_split | Degree of circuit split (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "precedent_opportunity": "string - LOW/MODERATE/HIGH/EXCEPTIONAL",
  "ripeness_score": "float 0-1",
  "circuit_split_exploitable": "boolean",
  "strategy": "string",
  "forum_recommendation": "string",
  "timeline": "string",
  "m_score": "float"
}
```

---

### 6. military_strategic_initiative
**Name:** Military: Strategic Initiative Window  
**Description:** Identifies decisive action opportunities when intelligence ambiguity, positional advantage, logistic readiness, and political authorization synchronize

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| enemy_ambiguity | Intelligence gaps favoring surprise (0-1) | float |
| positional_advantage | Geographical/tactical position (0-1) | float |
| logistic_readiness | Sustainment capability ready (0-1) | float |
| authorization_clarity | Political authority clear (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "maneuver_type": "string - DEFENSIVE_POSTURE/TACTICAL_INITIATIVE/OFFENSIVE_OPERATION/DECISIVE_ACTION",
  "initiative_score": "float 0-1",
  "advantage": "string",
  "recommended_action": "string",
  "execution_window": "string",
  "risk_assessment": "string",
  "m_score": "float"
}
```

---

### 7. social_catalytic_alignment
**Name:** Social/Cultural: Catalytic Alignment Detector  
**Description:** Spots transformative potential when individual readiness, network bridges, policy windows, and paradigm momentum converge

**Input Layers:**
| Layer | Description | Type |
|-------|-------------|------|
| individual_readiness | Population psychological readiness (0-1) | float |
| network_bridges | Cross-cutting network connections (0-1) | float |
| policy_window | Policy opportunity open (0-1) | float |
| paradigm_momentum | Cultural paradigm shift underway (0-1) | float |

**Output:**
```json
{
  "window_detected": "boolean",
  "movement_potential": "string - LOW/MODERATE/HIGH/TRANSFORMATIVE",
  "catalyst_score": "float 0-1",
  "transformative_potential": "float 0-1",
  "critical_mass_risk": "string",
  "recommended_action": "string",
  "mobilization_urgency": "string",
  "m_score": "float"
}
```

---

## Execution Model

**Type:** Python function call  
**Entry Point:** `mantic_thinking/tools/{suite}/{tool_id}.py::detect`  
**Language:** Python 3.8+  
**Dependencies:** numpy

### Function Signature
```python
def detect(layer1, layer2, layer3, layer4, f_time=1.0) -> dict:
    """
    Execute mantic detection for the specific domain.
    
    Args:
        layer1-4: Domain-specific float values (0-1, some support -1 to 1)
        f_time: Temporal kernel multiplier (default 1.0)
    
    Returns:
        dict with m_score, spatial_component, layer_attribution, 
        and domain-specific fields
    """
```

---

## Model-Specific Usage

### For Claude (Computer Use)
```python
# Read SKILL.md to discover tools
# Import via mantic_thinking/adapters/claude_adapter.py
from mantic_thinking.adapters.claude_adapter import get_claude_tools, execute_tool

tools = get_claude_tools()  # Returns 14 tools in Computer Use format

# Friction tool (risk detection)
result = execute_tool("healthcare_phenotype_genotype", {
    "phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8
})

# Emergence tool (opportunity detection)
result = execute_tool("healthcare_precision_therapeutic", {
    "genomic_predisposition": 0.85, "environmental_readiness": 0.82,
    "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90
})
```

### For Kimi (Native Tools)
```python
# Import via mantic_thinking/adapters/kimi_adapter.py
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools, execute, compare_friction_emergence

tools = get_kimi_tools()  # Returns 14 tools in Kimi native format

# Compare friction vs emergence for same domain
comparison = compare_friction_emergence(
    "healthcare",
    friction_params={"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
    emergence_params={"genomic_predisposition": 0.85, "environmental_readiness": 0.82,
                     "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90}
)
# High M in friction = risk. High M in emergence = opportunity.
```

### For Gemini (Function Declaration)
```python
# Import via mantic_thinking/adapters/gemini_adapter.py
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, execute_tool

# Get tools in Gemini FunctionDeclaration format
tools = get_gemini_tools()  # Returns [{"function_declarations": [...]}]

# Or get flat list
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools_flat
declarations = get_gemini_tools_flat()

# Execute tool
result = execute_tool("climate_resilience_multiplier", {
    "atmospheric_benefit": 0.75, "ecological_benefit": 0.80,
    "infrastructure_benefit": 0.78, "policy_alignment": 0.82
})
```

### For Codex/OpenAI (Function Calling)
```python
# Import via mantic_thinking/adapters/openai_adapter.py
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool, get_tools_by_type

# Get all 14 tools
all_tools = get_openai_tools()

# Or filter by type
friction_tools = get_tools_by_type("friction")  # 7 tools
emergence_tools = get_tools_by_type("emergence")  # 7 tools

result = execute_tool("cyber_attribution_resolver", {...})  # Friction
result = execute_tool("cyber_adversary_overreach", {...})   # Emergence
```

### For Ollama (Local/Cloud Models)
```python
# Import via mantic_thinking/adapters/openai_adapter.py (Ollama is OpenAI-compatible)
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool
import openai

# Point at Ollama's OpenAI-compatible endpoint
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # required but ignored
)

tools = get_openai_tools()

# Works with any Ollama model that supports tools:
# - minimax-m2.1:cloud
# - gpt-oss:20b-cloud  
# - glm-4.7:cloud
# - llama3.1, qwen2.5, etc.

result = execute_tool("social_catalytic_alignment", {
    "individual_readiness": 0.82, "network_bridges": 0.85,
    "policy_window": 0.80, "paradigm_momentum": 0.88
})
```

---

## Input Validation Rules

1. **Clamping:** All inputs clamped to valid range (0-1 or -1 to 1)
2. **NaN Handling:** Missing data triggers weight redistribution among available layers
3. **Weight Normalization:** Weights always sum to 1.0 after any adjustment
4. **Deterministic:** No randomness - same inputs always produce same outputs

---

## Response Schema

All tools return a standardized response:

```json
{
  "m_score": "float - final intensity score",
  "spatial_component": "float - raw S value",
  "layer_attribution": {
    "layer1": "float - percentage contribution",
    "layer2": "float - percentage contribution",
    "layer3": "float - percentage contribution",
    "layer4": "float - percentage contribution"
  },
  "...": "domain-specific fields"
}
```

### Friction Tools Additional Fields
```json
{
  "alert": "string - detection message (null if no alert)"
}
```

### Emergence Tools Additional Fields
```json
{
  "window_detected": "boolean - true if favorable alignment detected",
  "recommended_action": "string - what to do with this window"
}
```

### Layer Visibility (v1.2.0+)
All tools now include layer visibility to aid reasoning:

```json
{
  "layer_visibility": {
    "dominant": "Micro|Meso|Macro|Meta",
    "weights_by_layer": {
      "Micro": "float - aggregated weight",
      "Meso": "float - aggregated weight",
      "Macro": "float - aggregated weight", 
      "Meta": "float - aggregated weight"
    },
    "rationale": "string - why this layer dominates",
    "_note": "Interpretive aid; does not affect M-score"
  }
}
```

**Using Layer Visibility:**
- **Micro-dominant**: Trust immediate signals, check for noise/outliers
- **Meso-dominant**: Verify local context and environmental factors
- **Macro-dominant**: Systemic trend; slower but persistent
- **Meta-dominant**: Long-term adaptation; check baseline drift

Get explanations via adapters:
```python
from mantic_thinking.adapters.kimi_adapter import explain_result

result = execute("healthcare_phenotype_genotype", {...})
explanation = explain_result("healthcare_phenotype_genotype", result)
# Returns reasoning hints based on dominant layer
```

### Layer Coupling (v1.2.3+)
All tools now include layer coupling to reveal agreement and tension between layers:

```json
{
  "layer_coupling": {
    "coherence": 0.43,
    "layers": {
      "technical": {"agreement": 0.5, "tension_with": {"macro": 0.3, "risk": 0.4}},
      "macro": {"agreement": 0.57, "tension_with": {"technical": 0.3}},
      "flow": {"agreement": 0.63},
      "risk": {"agreement": 0.63, "tension_with": {"technical": 0.4}}
    }
  }
}
```

**Fields:**
- `coherence` (0-1): Overall agreement. 1 = all layers agree, 0 = total disagreement.
- `layers.<name>.agreement` (0-1): How much this layer agrees with all other layers.
- `layers.<name>.tension_with`: Only present when pairwise agreement < 0.5. Names the conflicting layer and its agreement score.

**Using Layer Coupling for Reasoning:**
- High coherence on an emergence window = the window is real (all layers confirm)
- Low coherence on a friction alert + tension pairs = identifies exactly where the conflict is
- No `tension_with` for a layer = that layer agrees with all others

**Note:** `layer_coupling` does not affect the M-score. Like `layer_visibility`, it is a read-only reasoning hint.

---

## Interpretation Guide

### Same M-Score, Opposite Meaning

| M-Score | Friction Tool Meaning | Emergence Tool Meaning |
|---------|----------------------|------------------------|
| 0.1-0.3 | Low risk, systems aligned | Low opportunity, wait |
| 0.4-0.6 | Moderate friction detected | Favorable window forming |
| 0.7-0.9 | High risk, urgent action needed | Optimal window, act now |

**Key Principle:** The M-score measures intensity. Friction tools interpret high intensity as danger. Emergence tools interpret high intensity as opportunity.

> **Temporal scaling:** When `f_time > 1.0`, `m_score` can exceed `1.0`. The table above assumes `f_time = 1.0` (default) and `k_n = 1.0`. Interpret scores above `1.0` as amplified intensity: the signal is strengthening over time.

---

## Testing

Run cross-model validation:
```bash
cd mantic-thinking
python -m pytest tests/test_cross_model.py -v
```

Expected: All 14 tools pass with 3 test cases each.

Quick sanity check:
```bash
python -c "from mantic_thinking.adapters.openai_adapter import get_openai_tools; print(len(get_openai_tools()), 'tools available')"
```
