# Mantic Early Warning System

Cross-domain anomaly and opportunity detection using 4-layer hierarchical analysis. 
Compatible with Claude, Kimi, Codex, and GPT-4o.

**14 tools total:** 7 Friction (divergence detection) + 7 Emergence (confluence detection)

## Core Formula (Immutable)

```
M = (sum(W * L * I)) * f(t) / k_n
```

## Tool Suites

### Friction Tools (Divergence Detection)
Detects when layers diverge: `if abs(L1 - L2) > 0.5: alert()`

| Tool | Domain | Description |
|------|--------|-------------|
| `healthcare_phenotype_genotype` | Healthcare | Phenotype-genotype mismatch |
| `finance_regime_conflict` | Finance | Market regime conflicts |
| `cyber_attribution_resolver` | Cyber | Attribution uncertainty |
| `climate_maladaptation` | Climate | Maladaptation prevention |
| `legal_precedent_drift` | Legal | Precedent drift alert |
| `military_friction_forecast` | Military | Operational friction |
| `social_narrative_rupture` | Social | Narrative rupture detection |

### Emergence Tools (Confluence Detection)
Detects when layers align: `if min(L) > 0.6: window_detected()`

| Tool | Domain | Description |
|------|--------|-------------|
| `healthcare_precision_therapeutic` | Healthcare | Optimal treatment windows |
| `finance_confluence_alpha` | Finance | High-conviction setups |
| `cyber_adversary_overreach` | Cyber | Defensive advantage windows |
| `climate_resilience_multiplier` | Climate | Multi-benefit interventions |
| `legal_precedent_seeding` | Legal | Precedent-setting windows |
| `military_strategic_initiative` | Military | Decisive action windows |
| `social_catalytic_alignment` | Social | Movement-building windows |

## Installation

```bash
cd mantic-tools
pip install -r requirements.txt
```

## Quick Start

### Native Python

```python
# Friction tool (detect risk)
from tools.friction.healthcare_phenotype_genotype import detect as detect_friction
result = detect_friction(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
print(f"Alert: {result['alert']}")  # Warning about mismatch

# Emergence tool (detect opportunity)
from tools.emergence.healthcare_precision_therapeutic import detect as detect_emergence
result = detect_emergence(genomic_predisposition=0.85, environmental_readiness=0.82,
                          phenotypic_timing=0.88, psychosocial_engagement=0.90)
print(f"Window: {result['window_detected']}")  # True - optimal timing
```

### For Kimi Code CLI

```python
from adapters.kimi_adapter import get_kimi_tools, execute, compare_friction_emergence

# Get all 14 tools
tools = get_kimi_tools()

# Compare friction vs emergence for same domain
comparison = compare_friction_emergence(
    "healthcare",
    friction_params={"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
    emergence_params={"genomic_predisposition": 0.85, "environmental_readiness": 0.82,
                     "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90}
)
# High M in friction = risk. High M in emergence = opportunity.
```

### For Claude Code CLI

```python
from adapters.claude_adapter import get_claude_tools, execute_tool, format_for_claude

# Get 14 tools in Computer Use format
tools = get_claude_tools()

# Execute and format for Claude
result = execute_tool("finance_confluence_alpha", {
    "technical_setup": 0.85, "macro_tailwind": 0.80,
    "flow_positioning": 0.75, "risk_compression": 0.70
})
print(format_for_claude(result, "finance_confluence_alpha"))
```

### For Codex / OpenAI

```python
from adapters.openai_adapter import get_openai_tools, execute_tool, get_tools_by_type

# Get all 14 tools
tools = get_openai_tools()

# Or filter by type
friction = get_tools_by_type("friction")   # 7 tools
emergence = get_tools_by_type("emergence") # 7 tools

result = execute_tool("cyber_adversary_overreach", {
    "threat_intel_stretch": 0.90, "geopolitical_pressure": 0.85,
    "operational_hardening": 0.80, "tool_reuse_fatigue": 0.88
})
```

## Architecture

```
mantic-tools/
├── SKILL.md                    # Universal manifest
├── README.md                   # This file
├── schemas/
│   ├── openapi.json           # OpenAPI spec
│   └── kimi-tools.json        # Kimi native format
├── core/
│   ├── mantic_kernel.py       # IMMUTABLE core formula
│   └── validators.py          # Input validation
├── tools/
│   ├── friction/              # 7 divergence detection tools
│   └── emergence/             # 7 confluence detection tools
├── adapters/                  # Model-specific adapters (Claude/Kimi/OpenAI)
├── configs/                   # Domain configurations & framework docs
│   ├── mantic_tech_spec.md    # Technical specification
│   ├── mantic_explicit_framework.md  # Framework protocol
│   ├── mantic_health.md       # Healthcare domain config
│   ├── mantic_finance.md      # Finance domain config
│   └── ...                    # (8 domain configs total)
└── tests/                     # Cross-model validation
```

## Running Tests

```bash
# Quick sanity check
python -c "from adapters.openai_adapter import get_openai_tools; print(len(get_openai_tools()), 'tools ready')"

# Run all tests
python -m pytest tests/test_cross_model.py -v

# Test individual tool
python tools/emergence/healthcare_precision_therapeutic.py
```

## Key Principle: Same M-Score, Opposite Meaning

| M-Score | Friction (Risk) | Emergence (Opportunity) |
|---------|-----------------|------------------------|
| 0.1-0.3 | Low risk ✓ | Low opportunity (wait) |
| 0.4-0.6 | Moderate friction ⚠️ | Favorable window |
| 0.7-0.9 | High risk 🚨 | Optimal window 🎯 |

The M-score measures **intensity**. Friction tools interpret high intensity as danger. Emergence tools interpret high intensity as opportunity.

## Configuration Files

The `configs/` directory contains framework documentation and domain-specific configurations:

- **Framework docs**: Technical specification, explicit framework mode, reasoning guidelines
- **Domain configs**: Healthcare, Finance, Cybersecurity, Climate, Legal, Social, Command, Current Affairs

These provide layer mappings and cross-domain coupling patterns for implementing domain-specific tools.

## Design Principles

1. **Immutable Core**: `mantic_kernel.py` must not be modified
2. **Deterministic**: Same inputs always return same outputs
3. **No External APIs**: Pure Python + NumPy only
4. **Cross-Model Compatible**: Works with Claude, Kimi, Codex, GPT-4o
5. **Complementary Suites**: Friction for risks, Emergence for opportunities
6. **Simple Logic**: Each tool <100 lines, threshold-based

## License

MIT License

## Version

1.0.0 - Complete suite with 14 cross-model compatible tools
