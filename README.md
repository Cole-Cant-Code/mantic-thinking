# Mantic Early Warning & Emergence Detection System

Cross-domain anomaly and opportunity detection using 4-layer hierarchical analysis.
Compatible with Claude, Kimi, Gemini, OpenAI, and Ollama.

**14 tools total:** 7 Friction (divergence detection) + 7 Emergence (confluence detection)

## Why Mantic

Mantic is a scoring engine designed to be paired with an LLM. The framework does the math. The LLM does the reasoning. The human can watch, sit back, or guide.

The formula is deliberately simple — four numbers multiplied, summed, scaled. A PhD would overthink it. A hobbyist would get stuck parameterizing it. But an LLM can take a messy real-world situation, map it to four inputs, read the structured output, and narrate what's happening and why — instantly, across any domain.

That's the point. The framework handles the part humans are bad at (consistent multi-signal scoring across domains) and the LLM handles the part math is bad at (contextual interpretation, ambiguity, explaining *why* a score matters in plain language).

### How It Works in Practice

You describe a situation. The LLM maps it to four layer values (0–1 each), calls a tool, and reads back:
- **M-score**: How intense is this signal?
- **Alert/window**: Did it cross a threshold?
- **Layer attribution**: Which input drove the score?
- **Layer visibility**: Which hierarchical level (Micro/Meso/Macro/Meta) is dominant, and why?

The LLM doesn't replace the math — the math is what keeps reasoning from drifting and what makes predictive work possible. But the LLM is what translates the situation into inputs, then interprets the structured output as a reasoning scaffold. The same friction score of 0.58 means "these signals disagree with each other" — the LLM's job is to explain *which* signals, *why* that matters, and *what to do about it* in context.

### Why an LLM Is Required

How the four layers are structured, how interactions propagate between them, how the weights and thresholds are tuned — all of it depends on the use case, the domain, and the timing. There is no universal configuration. A healthcare scenario structures Micro/Meso/Macro/Meta differently than a finance scenario, and a fast-moving crisis structures them differently than a slow policy drift.

The only tool that can navigate this quickly — mapping a situation to layers, choosing sensible parameters, interpreting the output, and explaining it in context — is an LLM. A human can do it, but slowly. A rules engine can't do it at all. The formula's simplicity is what makes this possible: there are only four layers and three values per layer. That's a small enough surface for an LLM to reason over in real time, but flexible enough to represent nearly anything.

And when an LLM is forced to reason through this structure — to match patterns it has never matched before across unfamiliar domains — it becomes fundamentally more useful. Everything is a pattern. Humans have only ever been able to identify the most obvious of them. A framework that makes an LLM look deeper, across layers and scales it wouldn't normally connect, surfaces the rest.

Running Mantic without an LLM gives you numbers. Running it with one gives you answers.

### What It Does

- Flags risk when signals diverge (Friction tools)
- Flags opportunity when signals align (Emergence tools)
- Exposes which layer drove the signal (layer_visibility)
- Provides structured reasoning cues an LLM can narrate directly

### Beyond the 14 Built-in Tools

The shipped tools — healthcare, finance, cyber, climate, legal, military, social — are reference points. Traditional starting spots. They formalize common domains with pre-set weights and thresholds so you can get results immediately.

But the framework is the four layers and the formula. That's it. An LLM can apply the same structure to anything that has signals at different scales: childbirth, household dynamics, MMA fight analysis, concert tour economics, virtual game economies, college admissions, supply chain disruption — whatever shows up.

The LLM decides what Micro/Meso/Macro/Meta mean for the situation, maps signals to values, and reasons through the output. No new tool needed. No new code.

| Domain | Micro | Meso | Macro | Meta |
|--------|-------|------|-------|------|
| MMA Fight Analysis | Strike accuracy | Round control | Career trajectory | Rule/culture shifts |
| Household Dynamics | Individual mood | Family routines | Financial stability | Generational patterns |
| Childbirth | Vitals/contractions | Care team coordination | Hospital capacity | Maternal health policy |
| Concert Tour Economics | Ticket sales | Local business impact | Industry revenue | Cultural adoption |
| Virtual Game Economies | Player transactions | Guild economies | Platform revenue | Gaming culture shifts |

The existing tools are examples of how to formalize that process when you want consistency and thresholds for a specific domain. When you don't need that, the kernel and the four-layer structure are enough.

## Core Formula (Immutable)

```
M = (sum(W * L * I)) * f(t) / k_n
```

This single line is the entire mathematical engine. Every tool, every domain, every adapter computes the same thing: four weights times four values times four interaction terms, summed, scaled by time, normalized. Nothing in the framework changes this formula. Nothing can.

### Why Immutability Matters

The formula is a contract. When you see an M-score from any tool — healthcare, finance, cyber, climate — you know exactly what produced it. The same inputs will always give the same output, regardless of which adapter called it, which model is interpreting it, or which domain it came from.

This is what makes cross-domain reasoning possible. A finance analyst and a clinician can compare M-scores because the math underneath is identical. The *inputs* differ (price action vs. vital signs), the *thresholds* differ (what counts as "high"), but the scoring engine is one thing.

If the formula could be modified per-domain or per-tool, that guarantee breaks. Every M-score becomes local and incomparable.

### Building on Top (Not Modifying)

Everything in the framework extends the kernel without altering it. The dependency flows one direction:

```
mantic_kernel (immutable)
    ↓
temporal kernels (pre-compute f_time, feed it in)
    ↓
validators (clamp and normalize inputs before they reach the kernel)
    ↓
domain tools (map real-world signals to W/L/I, call the kernel, apply thresholds)
    ↓
adapters (format tool I/O for Claude, Kimi, Gemini, OpenAI)
    ↓
introspection (interpret which layer drove the score, after the fact)
```

Each layer adds capability:

- **Temporal kernels** shape how signals evolve over time (exponential growth, logistic saturation, seasonal oscillation) — but they produce a single `f_time` float that gets multiplied in. The kernel doesn't know or care which temporal model generated it.

- **Validators** enforce input ranges and handle missing data (NaN graceful degradation, weight renormalization) — but they run *before* the kernel, not inside it.

- **Domain tools** translate real-world concepts into the four-number format the kernel expects. A "regime conflict" in finance is just `W=[0.35, 0.30, 0.20, 0.15]` and `L=[technical, macro, flow, risk]`. The tool adds detection logic (threshold checks, alert messages) around the raw score, but the score itself comes from the unmodified kernel.

- **Threshold overrides** let consumers adjust sensitivity without touching weights. Overrides are bounded (±20% of defaults) and clamped — they shift when an alert fires, not how the score is computed.

- **Adapters** reformat inputs and outputs for different LLM APIs. They never touch the math.

- **Introspection** maps kernel outputs back to the four-layer hierarchy (Micro/Meso/Macro/Meta) for interpretability. It's a read-only lens on the result.

The rule is simple: upstream of the kernel, you can shape what goes in. Downstream, you can interpret what comes out. The kernel itself is a fixed point.

For the full mathematical specification, including add-on guardrails, coupling matrices, and identifiability constraints, see [`configs/mantic_tech_spec.md`](configs/mantic_tech_spec.md). For the operational protocol (columnar architecture, cross-domain coupling rules), see [`configs/mantic_explicit_framework.md`](configs/mantic_explicit_framework.md).

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
pip install mantic-thinking
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

### For Gemini

```python
from adapters.gemini_adapter import get_gemini_tools, execute_tool

# Get tools in Gemini FunctionDeclaration format
tools = get_gemini_tools()

# Or get flat list for simpler SDK usage
from adapters.gemini_adapter import get_gemini_tools_flat
declarations = get_gemini_tools_flat()

result = execute_tool("climate_resilience_multiplier", {
    "atmospheric_benefit": 0.75, "ecological_benefit": 0.80,
    "infrastructure_benefit": 0.78, "policy_alignment": 0.82
})
```

### For Ollama (MiniMax, GPT-OSS, GLM, etc.)

```python
from adapters.openai_adapter import get_openai_tools, execute_tool
import openai

# Ollama's OpenAI-compatible endpoint
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

tools = get_openai_tools()
# Works with: minimax-m2.1:cloud, gpt-oss:20b-cloud, glm-4.7:cloud, etc.
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
mantic-thinking/
├── README.md                   # This file
├── core/
│   ├── mantic_kernel.py       # IMMUTABLE core formula
│   ├── safe_kernel.py         # Guarded wrapper (k_n validation)
│   └── validators.py          # Input validation and normalization
├── tools/
│   ├── friction/              # 7 divergence detection tools
│   └── emergence/             # 7 confluence detection tools
├── adapters/                  # Model-specific adapters (Claude/Kimi/Gemini/OpenAI)
├── mantic/
│   └── introspection/         # Layer visibility for reasoning (v1.2.0+)
│       ├── __init__.py
│       └── hierarchy.py
├── configs/                   # Domain configurations & framework docs
│   ├── mantic_tech_spec.md    # Full mathematical specification
│   ├── mantic_explicit_framework.md  # Operational protocol & columnar architecture
│   ├── mantic_reasoning_guidelines.md # LLM reasoning scaffold
│   ├── mantic_health.md       # Healthcare domain config
│   ├── mantic_finance.md      # Finance domain config
│   └── ...                    # (8 domain configs total)
├── schemas/
│   ├── openapi.json           # OpenAPI spec
│   └── kimi-tools.json        # Kimi native format
└── visualization/
    └── ascii_charts.py        # M-score gauges and attribution treemaps
```

## Key Principle: Same M-Score, Opposite Meaning

| M-Score | Friction (Risk) | Emergence (Opportunity) |
|---------|-----------------|------------------------|
| 0.1-0.3 | Low risk | Low opportunity (wait) |
| 0.4-0.6 | Moderate friction | Favorable window |
| 0.7-0.9 | High risk | Optimal window |

The M-score measures **intensity**. Friction tools interpret high intensity as danger. Emergence tools interpret high intensity as opportunity.

## Layer Visibility (v1.2.0+)

All tools now expose which hierarchical layer drives detection:

```python
result = detect(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
print(result["layer_visibility"]["dominant"])  # "Micro"
print(result["layer_visibility"]["rationale"])  # Why Micro dominates
```

**Layer guidance:**
- **Micro-dominant**: Check immediate signals for noise
- **Meso-dominant**: Verify local context factors
- **Macro-dominant**: Systemic trend; slower but persistent
- **Meta-dominant**: Long-term adaptation; check baseline

## Layer Coupling (v1.2.3+)

All tools also expose `layer_coupling`, a read-only view of whether the four layer values agree or diverge:

```python
result = detect(...)
print(result["layer_coupling"]["coherence"])  # 0-1 overall coherence
print({k: v["agreement"] for k, v in result["layer_coupling"]["layers"].items()})
```

- `coherence`: 1.0 means layers agree; lower means divergence/tension.
- `layers.<layer>.agreement`: mean agreement vs the other three layers.
- `layers.<layer>.tension_with`: only present when a pairwise agreement is < 0.5.

## Configuration Files

The `configs/` directory contains framework documentation and domain-specific configurations:

- **[`mantic_tech_spec.md`](configs/mantic_tech_spec.md)** — Full mathematical specification: core formula, add-on guardrails, layer definitions, coupling matrices, identifiability constraints, production guards
- **[`mantic_explicit_framework.md`](configs/mantic_explicit_framework.md)** — Operational protocol: columnar architecture, cross-domain coupling rules, strict containment
- **[`mantic_reasoning_guidelines.md`](configs/mantic_reasoning_guidelines.md)** — LLM reasoning scaffold: how to think in layers but speak in plain language
- **Domain configs**: Healthcare, Finance, Cybersecurity, Climate, Legal, Social, Command, Current Affairs

## Running Tests

```bash
# Quick sanity check
python3 -c "from adapters.openai_adapter import get_openai_tools; print(len(get_openai_tools()), 'tools ready')"

# Run all tests
python3 -m pytest tests/test_cross_model.py -v

# Test individual tool
python3 tools/emergence/healthcare_precision_therapeutic.py
```

## Design Principles

1. **Immutable Core**: The kernel cannot be modified — see [Why Immutability Matters](#why-immutability-matters)
2. **Build On Top**: Extensions shape inputs and interpret outputs — see [Building on Top](#building-on-top-not-modifying)
3. **Deterministic**: Same inputs always return same outputs
4. **No External APIs**: Pure Python + NumPy only
5. **Cross-Model Compatible**: Works with Claude, Kimi, Codex, GPT-4o
6. **Complementary Suites**: Friction for risks, Emergence for opportunities
7. **Simple Logic**: Each tool <100 lines, threshold-based

## License

### Source-Available License (Default)

Elastic License 2.0 — See [LICENSE](LICENSE) for full text.

**tl;dr:**
- Free to use, modify, distribute for internal applications
- Can use in production for your own organization
- **Cannot** offer as a hosted/managed service (SaaS)
- **Cannot** embed in commercial products without commercial license
- **Cannot** remove license protections

### Commercial License

Want to build a SaaS on top of Mantic? Embed it in your product? Redistribute?

**Purchase a commercial license** — See [COMMERCIAL_LICENSE](COMMERCIAL_LICENSE) for pricing and terms.

| Tier | Best For | From |
|------|----------|------|
| Startup | <$1M revenue, internal use | $500/year |
| Growth | <$50M revenue, internal use | $5,000/year |
| Enterprise | Unlimited internal, large orgs | $25,000/year |
| OEM/SaaS | Embed, resell, offer as service | Custom (from $50k) |

**Contact:** licensing@manticthink.com

*All licenses include updates and email support. OEM includes custom development options.*

## Version

1.2.3 - Added `layer_coupling` (coherence/agreement/tension) to all 14 tools
1.2.2 - Removed orphaned internal tools, cleaned configs
1.2.1 - README: clearer purpose and value
1.2.0 - Layer visibility for architectural reasoning (all tools include `layer_visibility` field)
1.1.6 - Safe kernel wrapper + adapter/tool fixes
1.1.5 - Ignore pytest cache in git
1.1.4 - Adapter import hygiene (no sys.path mutation)
1.1.3 - Input validation and confluence logic refinement
1.1.2 - PyPI install instructions updated
