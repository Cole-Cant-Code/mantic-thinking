# Mantic

**Cross-domain anomaly and opportunity detection for LLMs.**

Detects hidden risks before they cascade. Spots optimal windows before they close. Works across healthcare, finance, cybersecurity, climate, legal, military, social dynamics, system lock-in, or any domain you define.

```bash
pip install mantic-thinking
```

Compatible with **Claude, Kimi, Gemini, OpenAI, and Ollama.**

---

## The Problem

Expert knowledge is siloed. A cardiologist doesn't think in supply chain terms. A hedge fund analyst doesn't think in epidemiological terms. But the underlying patterns -- signals at different scales agreeing or fighting -- are structurally identical.

LLMs can see across those walls, but only if you give them structure that prevents hallucinated connections.

## What Mantic Does

Mantic is a deterministic scoring engine designed to be paired with an LLM. The framework does the math. The LLM does the reasoning. The human watches, guides, or sits back.

**One detection tool.** The LLM defines the layers, weights, and values. The kernel handles the math.

You describe a situation. The LLM maps it to layer values (0-1 each), calls the detect tool, and reads back:

- **M-score** -- How intense is this signal?
- **Alert / Window** -- Did it cross a threshold?
- **Layer attribution** -- Which input drove the score?
- **Layer visibility** -- Which hierarchical level (Micro/Meso/Macro/Meta) dominates, and why?
- **Layer coupling** -- Do the layers agree, or are they in tension?

The framework handles what humans are bad at (consistent multi-signal scoring across domains). The LLM handles what math is bad at (contextual interpretation, ambiguity, explaining *why* a score matters in plain language).

Running Mantic without an LLM gives you numbers. Running it with one gives you answers.

## What the LLM Controls

The LLM decides:
- **Layer names** -- What dimensions matter for this situation
- **Weights** -- How important each layer is (sum to 1.0)
- **Layer values** -- Assessment of each signal (0-1)
- **Interaction coefficients** -- Per-layer confidence adjustments (0.1-2.0)
- **Temporal kernel** -- How urgency evolves over time
- **Mode** -- Friction (risk/divergence) or emergence (opportunity/alignment)

## What Never Changes

- **Formula** -- `M = (sum(W * L * I)) * f(t) / k_n`
- **7 temporal kernels** -- exponential, linear, logistic, s_curve, power_law, oscillatory, memory
- **4-layer hierarchy** -- Micro/Meso/Macro/Meta structure
- **Governance bounds** -- All inputs clamped, all overrides audited

---

## Quick Start

### Python

```python
from mantic_thinking.tools.generic_detect import detect

# Detect risk (friction)
result = detect(
    domain_name="healthcare",
    layer_names=["phenotypic", "genomic", "environmental", "psychosocial"],
    weights=[0.35, 0.30, 0.20, 0.15],
    layer_values=[0.3, 0.9, 0.4, 0.8],
    mode="friction"
)
print(result["alert"])        # Warning about mismatch
print(result["m_score"])      # Signal intensity

# Detect opportunity (emergence) -- same inputs, different mode
result = detect(
    domain_name="healthcare",
    layer_names=["phenotypic", "genomic", "environmental", "psychosocial"],
    weights=[0.35, 0.30, 0.20, 0.15],
    layer_values=[0.85, 0.82, 0.88, 0.90],
    mode="emergence"
)
print(result["window_detected"])  # True -- optimal timing
```

### Any Domain

```python
from mantic_thinking.tools.generic_detect import detect

result = detect(
    domain_name="supply_chain",
    layer_names=["supplier_health", "logistics_flow", "demand_signal", "regulatory"],
    weights=[0.30, 0.25, 0.25, 0.20],
    layer_values=[0.4, 0.8, 0.3, 0.7],
    mode="friction"
)
print(result["alert"])
print(result["m_score"])
```

### With LLM Adapters

All adapters expose one `detect` tool where the LLM supplies everything.

```python
# OpenAI / Codex / Ollama
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool
tools = get_openai_tools()  # 1 tool: detect
result = execute_tool("detect", {
    "domain_name": "finance",
    "layer_names": ["technical", "macro", "flow", "risk"],
    "weights": [0.35, 0.30, 0.20, 0.15],
    "layer_values": [0.85, 0.80, 0.75, 0.70],
    "mode": "emergence"
})
```

```python
# Claude
from mantic_thinking.adapters.claude_adapter import get_claude_tools, execute_tool
tools = get_claude_tools()  # 1 tool: detect (Claude tool-use format)
```

```python
# Gemini
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, execute_tool
tools = get_gemini_tools()  # 1 tool: detect (FunctionDeclaration format)
```

```python
# Kimi
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools, execute
tools = get_kimi_tools()  # 1 tool: detect (Kimi native format)
```

### MCP Server

```bash
# Install with MCP support
pip install "mantic-thinking[mcp]"

# Run the server
python -m mantic_thinking
# or: mantic-thinking
```

The MCP server exposes 7 tools, 9 resources, and 3 prompts. Read `mantic://presets` for reference starting points from 16 built-in domain configurations.

### Reference Presets

16 built-in domain configurations are available as data (not locked functions). Use them as starting points, modify them, or ignore them:

```python
from mantic_thinking.adapters.openai_adapter import get_presets
presets = get_presets()
# {'healthcare_phenotype_genotype': {'layer_names': [...], 'weights': {...}}, ...}
```

### Context Loading (System Prompt Injection)

```python
from mantic_thinking.adapters.openai_adapter import get_full_context

# Full reasoning context: scaffold + domain config + tool guidance
context = get_full_context()

# Domain-scoped (includes only that domain's config + tools)
context = get_full_context("healthcare")
```

All adapters expose wrappers: `get_claude_context()`, `get_gemini_context()`, `get_kimi_context()`.

---

## Detection Modes

### Same Score, Opposite Meaning

| M-Score | Friction (Risk) | Emergence (Opportunity) |
|---------|-----------------|------------------------|
| 0.1-0.3 | Low risk | Low opportunity (wait) |
| 0.4-0.6 | Moderate friction | Favorable window |
| 0.7-0.9 | High risk | Optimal window (act now) |

The M-score measures **intensity**. Friction tools interpret high intensity as danger. Emergence tools interpret it as opportunity. `m_score` can exceed 1.0 when temporal scaling or interaction coefficients are elevated.

---

## Core Formula

```
M = (sum(W * L * I)) * f(t) / k_n
```

This single line is the entire mathematical engine. Weights times layer values times interaction terms, summed, scaled by time, normalized. Every detection computes the same thing.

### Why Immutability Matters

The formula is a contract. When you see an M-score -- from any domain, any adapter, any model -- you know exactly what produced it. The same inputs always give the same output.

This is what makes cross-domain reasoning possible. A finance analyst and a clinician can compare M-scores because the math underneath is identical. The *inputs* differ, the *thresholds* differ, but the scoring engine is one thing.

### Building on Top (Not Modifying)

```
mantic_kernel (immutable)
    |
temporal kernels (pre-compute f_time, feed it in)
    |
validators (clamp and normalize inputs before they reach the kernel)
    |
generic_detect (map real-world signals to W/L/I, call the kernel, apply thresholds)
    |
adapters (format tool I/O for Claude, Kimi, Gemini, OpenAI)
    |
introspection (interpret which layer drove the score, after the fact)
```

---

## Governance

LLMs are powerful reasoners but they drift. Mantic prevents this through layered constraints that preserve the LLM's judgment while preventing runaway behavior:

| Constraint | What the LLM Can Do | What's Prevented |
|------------|---------------------|------------------|
| **Weights (W)** | Define per detection | Weights must sum to 1.0 |
| **Thresholds** | Tune +/-20% of default | Cannot disable detection or trigger on noise |
| **Temporal Kernels** | Choose from 7 modes | All modes available; parameters bounded |
| **Interaction Coefficients (I)** | Scale per-layer confidence [0.1, 2.0] | Cannot zero out signals or let one dominate |
| **Temporal Scaling (f_time)** | Applied after computation | Clamped to [0.1, 3.0] |

Every adjustment is logged in `overrides_applied`. Nothing is hidden.

### Interaction Coefficients (Confidence Expression)

```python
# "The genetic test is solid, but symptoms are self-reported"
interaction_override = {"genomic": 1.0, "phenotypic": 0.7}

# "Support system is unusually strong -- amplify that signal"
interaction_override = {"psychosocial": 1.2}
```

---

## Temporal Dynamics

Seven temporal kernels model how signals evolve over time:

| Kernel | Dynamics | Example |
|--------|----------|---------|
| **Exponential** | Cascade failures, viral spread | Disease outbreaks, rumor propagation |
| **Logistic** | Saturation at carrying capacity | Market adoption, policy uptake |
| **S-Curve** | Slow then sudden adoption | Treatment acceptance, tech diffusion |
| **Power Law** | Mostly quiet, occasionally massive | Climate extremes, market crashes |
| **Oscillatory** | Cyclical patterns | Financial quarters, seasonal disease |
| **Memory** | Decaying but persistent influence | Institutional trauma, clinical history |
| **Linear** | Simple constant-rate decay | Signal relevance fading over time |

---

## Beyond the Built-in Domains

The shipped presets -- healthcare, finance, cyber, climate, legal, military, social, and system lock -- are reference points. Traditional starting spots. They formalize common domains with pre-set weights and thresholds so you can get results immediately.

But the framework is the four layers and the formula. That's it. An LLM can apply the same structure to anything that has signals at different scales: childbirth, household dynamics, MMA fight analysis, concert tour economics, virtual game economies, college admissions, supply chain disruption -- whatever shows up.

The LLM decides what Micro/Meso/Macro/Meta mean for the situation, maps signals to values, and reasons through the output. No new tool needed. No new code.

| Domain | Micro | Meso | Macro | Meta |
|--------|-------|------|-------|------|
| MMA Fight Analysis | Strike accuracy | Round control | Career trajectory | Rule/culture shifts |
| Household Dynamics | Individual mood | Family routines | Financial stability | Generational patterns |
| Childbirth | Vitals/contractions | Care team coordination | Hospital capacity | Maternal health policy |
| Concert Tour Economics | Ticket sales | Local business impact | Industry revenue | Cultural adoption |
| Supply Chain | Supplier health | Logistics flow | Demand signals | Regulatory shifts |

---

## Layer Visibility

All detections expose which hierarchical layer drives the result:

```python
result = detect(...)
print(result["layer_visibility"]["dominant"])  # "Micro"
print(result["layer_visibility"]["rationale"])  # Why Micro dominates
```

**Layer guidance:**
- **Micro-dominant**: Check immediate signals for noise
- **Meso-dominant**: Verify local context factors
- **Macro-dominant**: Systemic trend; slower but persistent
- **Meta-dominant**: Long-term adaptation; check baseline

## Layer Coupling

All detections expose `layer_coupling`, a read-only view of whether the layer values agree or diverge:

```python
result = detect(...)
print(result["layer_coupling"]["coherence"])  # 0-1 overall coherence
```

- `coherence`: 1.0 means layers agree; lower means divergence/tension.
- `layers.<layer>.tension_with`: only present when a pairwise agreement is < 0.5.

## Audit Trail & Traceability

Every detection response includes an `overrides_applied` block that logs any threshold, temporal, and interaction tuning. In regulated environments -- clinical, financial, legal -- this provides provenance.

Every score is traceable. Every judgment is logged. Nothing is hidden.

---

## Pragmatism Over Precision

This framework is scaffolding, not scripture.

**Approximate boldly.** If a patient says "I feel terrible," that's a 0.7 or 0.8, not a 0.73. The kernel handles +/-0.1 variance; you cannot.

**Skip the knobs.** Most detections don't need interaction overrides or temporal kernels. If simple inputs give a clear signal, stop there.

**Trust the clamping.** If you think a threshold should be lower, try the override. The validator will clamp it appropriately. Move on.

**Anti-pattern:** Spending 500 tokens optimizing parameters for a situation that could be read intuitively in 50.

**Success pattern:** Getting to an M-score in 2-3 reasoning steps, with inputs you'd defend as roughly right, then immediately interpreting what that score means for the user.

---

## Test Drive

Copy/paste any of these into your LLM. They build intuition for layered structural reasoning under constraints.

<details>
<summary><strong>Healthcare: Emergency Department Wait Times (2014)</strong></summary>

```text
You are consulting for a hospital system in 2014. You have been given only this information:

- Average ED wait time: 4.2 hours (2014) vs. 2.8 hours (2009)
- ED visit volume: +8% over 5 years
- Hospital staffing levels: roughly flat
- Patient satisfaction scores: declined sharply
- Hospital administrator's hypothesis: "We need more ED beds and staff"
- ED director's hypothesis: "We're seeing more non-urgent cases because people can't afford primary care"
- Finance department notes: ED operating margin negative; inpatient still profitable

Your task: Using only the limited information above, identify:
1. What are the 3 most likely root causes (not symptoms)?
2. Which single question would you ask to distinguish between them?
3. What layer (Micro/Meso/Macro) does each potential root cause live at?
4. What coordination failure pattern could generate these symptoms regardless of specific data?

Constraint: You cannot request more data. Reason from structure, not statistics.
```
</details>

<details>
<summary><strong>Structural Intervention: Global Shipping Container Standardization</strong></summary>

```text
In 2019, a consortium of Pacific Rim nations proposed replacing the 40-foot ISO container standard with a new modular system offering 23% better volume efficiency and native IoT integration. The proposal had backing from three of the world's five largest shipping companies and two major port operators, with a 10-year transition timeline and $4.2 billion in committed investment. Despite demonstrated efficiency gains in pilot programs and no technical barriers, the initiative collapsed within 18 months.

Analyze this system using a multi-layer structural framework to determine why the intervention failed, identify the dominant coupling type, and specify what conditions would need to change for a future attempt to succeed.
```
</details>

<details>
<summary><strong>Technology: Voice Assistants (2017-2018)</strong></summary>

```text
Amazon Echo: ~30M units sold. Google Home: ~20M units sold. Apple HomePod launches (premium positioning, struggles). Smart speaker adoption: ~20% of U.S. households. Usage patterns: 90% simple queries (weather, timers, music). "Skills"/apps: thousands built, most get <100 users. Privacy concerns rising (always-listening devices).

Task: Are we early in S-curve (approaching mass adoption) or hitting plateau (novelty wearing off)? What needs to be true for voice to become primary interface by 2025? Is the constraint technology (NLP accuracy), use cases (not enough valuable tasks), or social (privacy concerns)?
```
</details>

---

## Architecture

```
mantic-thinking/
├── mantic_thinking/
│   ├── core/
│   │   ├── mantic_kernel.py       # IMMUTABLE core formula
│   │   ├── safe_kernel.py         # Guarded wrapper (k_n validation)
│   │   └── validators.py          # Input validation & normalization
│   ├── tools/
│   │   ├── friction/              # 8 reference preset tools + YAML guidance
│   │   ├── emergence/             # 8 reference preset tools + YAML guidance
│   │   └── generic_detect.py      # THE detect function (3-6 layers, any domain)
│   ├── adapters/                  # Claude / Kimi / Gemini / OpenAI adapters
│   ├── server.py                  # FastMCP server (7 tools, 9 resources, 3 prompts)
│   ├── mantic/introspection/      # Layer visibility & hierarchy mappings
│   ├── configs/                   # Domain configs, system prompt, framework docs
│   ├── schemas/                   # OpenAPI & Kimi-native schemas
│   └── visualization/             # ASCII charts & gauges
└── tests/                         # 626 tests
```

---

## Configuration

### Config Files

The `mantic_thinking/configs/` directory provides LLM reasoning context:

- **[`mantic_scaffold.md`](mantic_thinking/configs/mantic_scaffold.md)** -- Universal reasoning scaffold
- **[`mantic_tech_spec.md`](mantic_thinking/configs/mantic_tech_spec.md)** -- Full mathematical specification
- **[`mantic_explicit_framework.md`](mantic_thinking/configs/mantic_explicit_framework.md)** -- Operational protocol & columnar architecture
- **[`mantic_reasoning_guidelines.md`](mantic_thinking/configs/mantic_reasoning_guidelines.md)** -- LLM reasoning guidelines
- **Domain configs**: Healthcare, Finance, Cybersecurity, Climate, Legal, Social, Military, System Lock

### Running Tests

```bash
# Quick check
python3 -c "from mantic_thinking.tools.generic_detect import detect; print('detect ready')"

# Full suite (626 tests)
python3 -m pytest -q
```

---

## Design Principles

1. **Immutable Core** -- The kernel cannot be modified
2. **LLM Controls the Inputs** -- Layer names, weights, values, interactions are all LLM-decided
3. **Build On Top** -- Extensions shape inputs and interpret outputs, never the formula
4. **Deterministic** -- Same inputs always return same outputs
5. **No External APIs** -- Pure Python + NumPy + PyYAML. Bring your own LLM client
6. **Cross-Model** -- Claude, Kimi, Gemini, OpenAI, Ollama
7. **Auditable** -- Every override logged, every judgment traceable

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

### Source-Available (Default)

Elastic License 2.0 -- See [LICENSE](LICENSE).

- Free to use, modify, distribute for internal applications
- Can use in production for your own organization
- **Cannot** offer as a hosted/managed service (SaaS)
- **Cannot** embed in commercial products without commercial license

### Commercial License

Want to build a SaaS on top of Mantic? Embed it in your product?

See [COMMERCIAL_LICENSE](COMMERCIAL_LICENSE) for pricing and terms.

| Tier | Best For | From |
|------|----------|------|
| Startup | <$1M revenue | $500/year |
| Growth | <$50M revenue | $5,000/year |
| Enterprise | Unlimited, large orgs | $25,000/year |
| OEM/SaaS | Embed, resell, hosted service | Custom (from $50k) |

**Contact:** licensing@manticthink.com

---

## Version History

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for full changelog.

| Version | Highlights |
|---------|-----------|
| **2.2.0** | Single-detect architecture. LLM controls layers, weights, values. 16 built-in tools become presets. |
| 2.0.1 | PyPI README sync |
| 2.0.0 | README overhaul, v2 milestone |
| 1.6.0 | System lock domain |
| 1.5.x | Context assembly, MCP bootstrap, generic detect |
| 1.4.x | Interaction coefficients, per-tool YAML guidance |
| 1.2.x | Layer visibility, layer coupling, safe kernel wrapper |
