# Mantic

**Cross-domain anomaly and opportunity detection for LLMs.**

Detects hidden risks before they cascade. Spots optimal windows before they close. Works across healthcare, finance, cybersecurity, climate, legal, military, social dynamics, system lock-in, or any domain you define.

```bash
pip install mantic-thinking
```

Compatible with **Claude, Kimi, Gemini, OpenAI, and Ollama.**
17 tools: 8 Friction (risk) + 8 Emergence (opportunity) + 1 Generic (any domain).

---

## The Problem

Expert knowledge is siloed. A cardiologist doesn't think in supply chain terms. A hedge fund analyst doesn't think in epidemiological terms. But the underlying patterns -- signals at different scales agreeing or fighting -- are structurally identical.

LLMs can see across those walls, but only if you give them structure that prevents hallucinated connections.

## What Mantic Does

Mantic is a deterministic scoring engine designed to be paired with an LLM. The framework does the math. The LLM does the reasoning. The human watches, guides, or sits back.

You describe a situation. The LLM maps it to four layer values (0-1 each), calls a Mantic tool, and reads back:

- **M-score** -- How intense is this signal?
- **Alert / Window** -- Did it cross a threshold?
- **Layer attribution** -- Which input drove the score?
- **Layer visibility** -- Which hierarchical level (Micro/Meso/Macro/Meta) dominates, and why?
- **Layer coupling** -- Do the layers agree, or are they in tension?

The framework handles what humans are bad at (consistent multi-signal scoring across domains). The LLM handles what math is bad at (contextual interpretation, ambiguity, explaining *why* a score matters in plain language).

Running Mantic without an LLM gives you numbers. Running it with one gives you answers.

## Why This Needs an LLM

The four layers are content-agnostic. How they're structured, how interactions propagate, how thresholds are tuned -- all of it depends on the situation, the domain, and the timing. There is no universal configuration. A healthcare scenario structures Micro/Meso/Macro/Meta differently than a finance scenario, and a fast-moving crisis structures them differently than a slow policy drift.

The only tool that can navigate this quickly -- mapping a messy situation to four layers, choosing sensible parameters, interpreting the output, and explaining it in context -- is an LLM. A human can do it, but slowly. A rules engine can't do it at all. The formula's simplicity is what makes this possible: there are only four layers and three values per layer. That's a small enough surface for an LLM to reason over in real time, but flexible enough to represent nearly anything.

And when an LLM is forced to reason through this structure -- to match patterns it has never matched before across unfamiliar domains -- it becomes fundamentally more useful. Everything is a pattern. Humans have only ever been able to identify the most obvious of them. A framework that makes an LLM look deeper, across layers and scales it wouldn't normally connect, surfaces the rest.

---

## Quick Start

### Python

```python
# Detect risk (friction)
from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect as detect_friction
result = detect_friction(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
print(result["alert"])        # Warning about mismatch
print(result["m_score"])      # Signal intensity

# Detect opportunity (emergence)
from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import detect as detect_emergence
result = detect_emergence(genomic_predisposition=0.85, environmental_readiness=0.82,
                          phenotypic_timing=0.88, psychosocial_engagement=0.90)
print(result["window_detected"])  # True -- optimal timing
```

### Any Domain (Generic Detection)

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

```python
# OpenAI / Codex
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool, get_tools_by_type
tools = get_openai_tools()           # 17 tools, OpenAI function-calling format
friction = get_tools_by_type("friction")   # 8 tools
emergence = get_tools_by_type("emergence") # 8 tools
```

```python
# Ollama (OpenAI-compatible endpoint)
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool
import openai
client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
tools = get_openai_tools()
```

```python
# Claude
from mantic_thinking.adapters.claude_adapter import get_claude_tools, execute_tool, format_for_claude
tools = get_claude_tools()  # 17 tools, Claude tool-use format
result = execute_tool("finance_confluence_alpha", {
    "technical_setup": 0.85, "macro_tailwind": 0.80,
    "flow_positioning": 0.75, "risk_compression": 0.70
})
print(format_for_claude(result, "finance_confluence_alpha"))
```

```python
# Gemini
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, execute_tool
tools = get_gemini_tools()  # 17 tools, Gemini FunctionDeclaration format
```

```python
# Kimi
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools, execute, compare_friction_emergence
tools = get_kimi_tools()  # 17 tools, Kimi native format

# Compare friction vs emergence for same domain
comparison = compare_friction_emergence(
    "healthcare",
    friction_params={"phenotypic": 0.3, "genomic": 0.9, "environmental": 0.4, "psychosocial": 0.8},
    emergence_params={"genomic_predisposition": 0.85, "environmental_readiness": 0.82,
                     "phenotypic_timing": 0.88, "psychosocial_engagement": 0.90}
)
# High M in friction = risk. High M in emergence = opportunity.
```

### Context Loading (System Prompt Injection)

Adapters can load the complete reasoning context for system prompt injection. Load order: **Scaffold** (universal framework) -> **Domain Config** (domain-specific reasoning) -> **Tool Guidance** (per-tool calibration from YAML files).

```python
from mantic_thinking.adapters.openai_adapter import get_full_context

# Full reasoning context: scaffold + domain config + tool guidance
context = get_full_context()

# Domain-scoped (includes only that domain's config + tools)
context = get_full_context("healthcare")

# Aliases work: "cybersecurity" -> cyber, "health" -> healthcare, etc.
context = get_full_context("cybersecurity")
```

Individual stages are also available:

```python
from mantic_thinking.adapters.openai_adapter import (
    get_scaffold,        # Stage 1: universal framework
    get_domain_config,   # Stage 2: domain-specific config
    get_tool_guidance,   # Stage 3: per-tool YAML calibration
)

scaffold = get_scaffold()                         # Always the same
config = get_domain_config("finance")             # Domain-specific
guidance = get_tool_guidance(["finance_regime_conflict"])  # Subset of tools
```

All adapters expose wrappers: `get_claude_context()`, `get_gemini_context()`, `get_kimi_context()`.

---

## Tool Suite

### Friction Tools (Risk Detection)

Detect when signals at different scales **diverge** -- the disagreement is the danger signal.

| Tool | Domain | What It Detects |
|------|--------|-----------------|
| `healthcare_phenotype_genotype` | Healthcare | Phenotype-genotype mismatch |
| `finance_regime_conflict` | Finance | Market regime conflicts |
| `cyber_attribution_resolver` | Cyber | Attribution uncertainty |
| `climate_maladaptation` | Climate | Maladaptation risk |
| `legal_precedent_drift` | Legal | Precedent drift |
| `military_friction_forecast` | Military | Operational friction |
| `social_narrative_rupture` | Social | Narrative rupture |
| `system_lock_recursive_control` | System Lock | Recursive control and lock-in |

### Emergence Tools (Opportunity Detection)

Detect when signals at different scales **converge** -- the alignment is the opportunity window.

| Tool | Domain | What It Detects |
|------|--------|-----------------|
| `healthcare_precision_therapeutic` | Healthcare | Optimal treatment windows |
| `finance_confluence_alpha` | Finance | High-conviction setups |
| `cyber_adversary_overreach` | Cyber | Defensive advantage windows |
| `climate_resilience_multiplier` | Climate | Multi-benefit interventions |
| `legal_precedent_seeding` | Legal | Precedent-setting windows |
| `military_strategic_initiative` | Military | Decisive action windows |
| `social_catalytic_alignment` | Social | Movement-building windows |
| `system_lock_dissolution_window` | System Lock | Lock-dissolution opportunities |

### Generic Tool

| Tool | Description |
|------|-------------|
| `generic_detect` | Caller-defined domain: 3-6 layers, custom weights, same kernel and governance |

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

This single line is the entire mathematical engine. Four weights times four layer values times four interaction terms, summed, scaled by time, normalized. Every tool, every domain, every adapter computes the same thing.

### Why Immutability Matters

The formula is a contract. When you see an M-score from any tool -- healthcare, finance, cyber, climate -- you know exactly what produced it. The same inputs will always give the same output, regardless of which adapter called it, which model is interpreting it, or which domain it came from.

This is what makes cross-domain reasoning possible. A finance analyst and a clinician can compare M-scores because the math underneath is identical. The *inputs* differ (price action vs. vital signs), the *thresholds* differ (what counts as "high"), but the scoring engine is one thing.

If the formula could be modified per-domain or per-tool, that guarantee breaks. Every M-score becomes local and incomparable.

### Building on Top (Not Modifying)

Everything in the framework extends the kernel without altering it. The dependency flows one direction:

```
mantic_kernel (immutable)
    |
temporal kernels (pre-compute f_time, feed it in)
    |
validators (clamp and normalize inputs before they reach the kernel)
    |
domain tools (map real-world signals to W/L/I, call the kernel, apply thresholds)
    |
adapters (format tool I/O for Claude, Kimi, Gemini, OpenAI)
    |
introspection (interpret which layer drove the score, after the fact)
```

Each layer adds capability:

- **Temporal kernels** shape how signals evolve over time (exponential growth, logistic saturation, seasonal oscillation) -- but they produce a single `f_time` float that gets multiplied in. The kernel doesn't know or care which temporal model generated it.
- **Validators** enforce input ranges and handle missing data (NaN graceful degradation, weight renormalization) -- but they run *before* the kernel, not inside it.
- **Domain tools** translate real-world concepts into the four-number format the kernel expects. A "regime conflict" in finance is just `W=[0.35, 0.30, 0.20, 0.15]` and `L=[technical, macro, flow, risk]`. The tool adds detection logic (threshold checks, alert messages) around the raw score, but the score itself comes from the unmodified kernel.
- **Threshold overrides** let consumers adjust sensitivity without touching weights. Overrides are bounded (+/-20% of defaults) and clamped -- they shift when an alert fires, not how the score is computed.
- **Adapters** reformat inputs and outputs for different LLM APIs. They never touch the math.
- **Introspection** maps kernel outputs back to the four-layer hierarchy (Micro/Meso/Macro/Meta) for interpretability. It's a read-only lens on the result.

The rule is simple: upstream of the kernel, you can shape what goes in. Downstream, you can interpret what comes out. The kernel itself is a fixed point.

For the full mathematical specification, including add-on guardrails, coupling matrices, and identifiability constraints, see [`mantic_thinking/configs/mantic_tech_spec.md`](mantic_thinking/configs/mantic_tech_spec.md). For the operational protocol (columnar architecture, cross-domain coupling rules), see [`mantic_thinking/configs/mantic_explicit_framework.md`](mantic_thinking/configs/mantic_explicit_framework.md).

---

## Governance

LLMs are powerful reasoners but they drift. Give an LLM complete freedom with a scoring engine and it will eventually produce extreme inputs or incomparable scores. Mantic prevents this through layered constraints that preserve the LLM's judgment while preventing runaway behavior:

| Constraint | What the LLM Can Do | What's Prevented |
|------------|---------------------|------------------|
| **Weights (W)** | Visible, immutable | Domain theory cannot be altered or ignored |
| **Thresholds** | Tune +/-20% of default | Cannot disable detection or trigger on noise |
| **Temporal Kernels** | Choose from domain-allowlisted set | Nonsensical dynamics blocked |
| **Interaction Coefficients (I)** | Scale per-layer confidence [0.1, 2.0] | Cannot zero out signals or let one dominate |
| **Temporal Scaling (f_time)** | Applied after computation | Runaway growth clamped to [0.1, 3.0] |

The LLM exercises real judgment -- adjusting sensitivity, expressing confidence, modeling temporal dynamics -- but cannot break the scoring engine, produce incomparable scores, or hide what it did.

### Interaction Coefficients (Confidence Expression)

While domain weights encode general theory, interaction coefficients let the LLM express situation-specific confidence:

```python
# "The genetic test is solid, but symptoms are self-reported"
interaction_override = {"genomic": 1.0, "phenotypic": 0.7}

# "Support system is unusually strong -- amplify that signal"
interaction_override = {"psychosocial": 1.2}
```

- **Bounds:** [0.1, 2.0] -- you can dampen doubt or amplify confidence, but cannot ignore a layer or let it dominate
- **Audit:** Every adjustment logged in `overrides_applied.interaction`
- **Modes:** Scale (multiply existing dynamic values) or Replace (use absolute values)

This is how the LLM says "in this specific case, I trust this signal more than that one" without breaking the mathematical core.

### "But What If the Weights Are Wrong?" (Regime Changes)

The weights (W) are fixed. That's intentional. But it raises a fair question: what happens when the rules change -- a market crash where risk dominates, a pandemic where psychosocial factors eclipse genomics?

The framework has four responses, in escalating order:

1. **Layer visibility already tells you.** Even with risk weighted at 0.15, if risk input is 0.95 and everything else is low, `layer_visibility.dominant` flags risk as the driver. The LLM reads attribution, not just the score. A moderate M-score with risk-dominant attribution *is* the regime change signal.

2. **Interaction coefficients reweight in practice.** `interaction_override = {"risk": 1.8, "technical": 0.3}` shifts effective contribution from `W` alone to `W * I`. Risk goes from 0.15 to 0.27 effective; technical drops from 0.35 to 0.105. The LLM is doing regime-aware reweighting -- bounded and audited.

3. **Layer coupling exposes the tension.** When risk screams but technical says everything's fine, `layer_coupling.coherence` drops and `tension_with` names the disagreement. The LLM doesn't need reweighted scores to see the conflict -- the conflict *is* the insight.

4. **Generic detect allows full reweighting.** If the regime is truly unprecedented, `generic_detect` lets the LLM call the same kernel with `weights=[0.10, 0.15, 0.15, 0.60]` -- risk at 60%. Same governance, same audit trail, caller-defined weights.

Why not just let the LLM modify W directly? Because then cross-domain M-scores become incomparable, the audit trail is meaningless, and the LLM can rationalize extreme weight shifts to confirm its priors. Fixed W is the anti-hallucination mechanism. I is the regime-adjustment dial. Generic detect is the escape valve.

---

## Temporal Dynamics

Seven temporal kernels model how signals evolve over time. Domain-allowlists prevent nonsensical choices:

| Kernel | Dynamics | Example |
|--------|----------|---------|
| **Exponential** | Cascade failures, viral spread | Disease outbreaks, rumor propagation |
| **Logistic** | Saturation at carrying capacity | Market adoption, policy uptake |
| **S-Curve** | Slow then sudden adoption | Treatment acceptance, tech diffusion |
| **Power Law** | Mostly quiet, occasionally massive | Climate extremes, market crashes |
| **Oscillatory** | Cyclical patterns | Financial quarters, seasonal disease |
| **Memory** | Decaying but persistent influence | Institutional trauma, clinical history |
| **Linear** | Simple constant-rate decay | Signal relevance fading over time |

Each kernel produces a single `f_time` float that scales the M-score. The kernel doesn't know or care which temporal model generated it.

---

## Signal Translation

The hardest part isn't the math -- it's mapping messy reality to four clean numbers. Every tool ships with a `.yaml` guidance file that provides qualitative anchors:

```yaml
# healthcare_phenotype_genotype.yaml (excerpt)
parameters:
  phenotypic:
    low: "Minimal symptoms; vitals/labs stable"
    high: "Severe presentation; objective markers elevated"
    dampen_when: "Symptoms are self-reported only; limited objective confirmation"
  psychosocial:
    high: "Strong support system; good adherence; high resilience"
    amplify_when: "Patient reports robust family/social support structure"

example_scenarios:
  - description: "High genetic risk but symptom report is noisy; strong support"
    overrides:
      interaction_override: {phenotypic: 0.7, psychosocial: 1.2}
```

**The LLM reads these anchors to translate:** "My genetic test came back scary but I feel fine and I have a great support system" becomes `phenotypic=0.3, genomic=0.9, psychosocial=0.8`.

### Input Quality & Limitations

The framework's accuracy is bounded by input quality. The mapping from messy reality to [0-1] values is fundamentally interpretive -- the LLM uses YAML guidance as calibration points and interpolates. Mantic doesn't eliminate judgment; it makes judgment consistent, constrained, and auditable.

---

## Beyond the Built-in Domains

The shipped tools -- healthcare, finance, cyber, climate, legal, military, social, and system lock -- are reference points. Traditional starting spots. They formalize common domains with pre-set weights and thresholds so you can get results immediately.

But the framework is the four layers and the formula. That's it. An LLM can apply the same structure to anything that has signals at different scales: childbirth, household dynamics, MMA fight analysis, concert tour economics, virtual game economies, college admissions, supply chain disruption -- whatever shows up.

The LLM decides what Micro/Meso/Macro/Meta mean for the situation, maps signals to values, and reasons through the output. No new tool needed. No new code.

| Domain | Micro | Meso | Macro | Meta |
|--------|-------|------|-------|------|
| MMA Fight Analysis | Strike accuracy | Round control | Career trajectory | Rule/culture shifts |
| Household Dynamics | Individual mood | Family routines | Financial stability | Generational patterns |
| Childbirth | Vitals/contractions | Care team coordination | Hospital capacity | Maternal health policy |
| Concert Tour Economics | Ticket sales | Local business impact | Industry revenue | Cultural adoption |
| Supply Chain | Supplier health | Logistics flow | Demand signals | Regulatory shifts |

No new tool needed. No new code. The LLM decides what the layers mean and maps signals to values.

---

## Layer Visibility

All tools expose which hierarchical layer drives detection:

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

## Layer Coupling

All tools expose `layer_coupling`, a read-only view of whether the four layer values agree or diverge:

```python
result = detect(...)
print(result["layer_coupling"]["coherence"])  # 0-1 overall coherence
print({k: v["agreement"] for k, v in result["layer_coupling"]["layers"].items()})
```

- `coherence`: 1.0 means layers agree; lower means divergence/tension.
- `layers.<layer>.agreement`: mean agreement vs the other three layers.
- `layers.<layer>.tension_with`: only present when a pairwise agreement is < 0.5.

## Audit Trail & Traceability

Every tool response includes an `overrides_applied` block that logs any threshold, temporal, and interaction tuning (and always records the effective `f_time`). In regulated environments -- clinical, financial, legal -- this provides provenance:

```json
{
  "m_score": 0.72,
  "overrides_applied": {
    "threshold_overrides": {
      "requested": {"buffering": 0.35},
      "applied": {"buffering": {"requested": 0.35, "used": 0.35, "was_clamped": false}},
      "clamped": false,
      "ignored_keys": null
    },
    "temporal_config": {
      "requested": {"kernel_type": "s_curve", "alpha": 0.6},
      "applied": {"kernel_type": "s_curve", "alpha": 0.5},
      "rejected": null,
      "clamped": {"alpha": {"requested": 0.6, "used": 0.5, "bounds": [0.01, 0.5]}}
    },
    "interaction": {
      "interaction_mode": "dynamic",
      "override_mode": "scale",
      "requested": {"phenotypic": 0.7, "psychosocial": 1.2},
      "validated": [0.7, 1.0, 1.0, 1.2],
      "used": [0.7, 1.0, 1.0, 1.2],
      "rejected": null,
      "clamped": null
    },
    "f_time": {
      "requested": 1.8,
      "used": 1.8,
      "clamped": false
    }
  }
}
```

**What this means:** "The M-score was 0.72. The LLM requested a threshold shift to 0.35 (applied as requested). It requested an S-curve kernel with alpha 0.6, which was clamped to 0.5 (domain maximum). It amplified the psychosocial layer by 1.2x based on patient context."

Every score is traceable. Every judgment is logged. Nothing is hidden.

---

## Pragmatism Over Precision

This framework is scaffolding, not scripture. The YAML guidance files are calibration anchors, not commandments.

**Approximate boldly.** If a patient says "I feel terrible," that's a 0.7 or 0.8, not a 0.73. The kernel handles +/-0.1 variance; you cannot.

**Skip the knobs.** Most detections don't need interaction overrides or temporal kernels. If simple inputs give a clear signal, stop there.

**Trust the clamping.** If you think a threshold should be lower, try the override. The validator will clamp it appropriately. Move on.

**The four numbers are directional, not definitional.** `phenotypic=0.3` doesn't mean exactly 30% symptomatic. It means low but present symptoms. The qualitative narrative matters more than quantitative precision.

**Anti-pattern:** Spending 500 tokens optimizing parameters for a situation that could be read intuitively in 50.

**Success pattern:** Getting to an M-score in 2-3 reasoning steps, with inputs you'd defend as roughly right, then immediately interpreting what that score means for the user.

### Do Not Dismiss Before Testing

Assuming the framework is inadequate before testing it is a guaranteed failure mode. Do not decide the domain weights are wrong, the thresholds too high, or the YAML guidance irrelevant without running a detection first. The framework encodes expert theory; your job is to provide situation-specific judgment, not to rebuild the scaffolding before standing on it.

The absence of capability in this document is not evidence of incapability. The four layers and the formula are content-agnostic; they do not care whether the signals come from epidemiology, finance, or household thermostats. Assume capability until proven otherwise.

Test the defaults. Then tune if needed. Never assume.

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
│   │   ├── friction/              # 8 divergence detection tools + YAML guidance
│   │   ├── emergence/             # 8 confluence detection tools + YAML guidance
│   │   └── generic_detect.py      # Caller-defined domains (3-6 layers)
│   ├── adapters/                  # Claude / Kimi / Gemini / OpenAI adapters
│   ├── mantic/introspection/      # Layer visibility & hierarchy mappings
│   ├── configs/                   # Domain configs & framework docs
│   ├── schemas/                   # OpenAPI & Kimi-native schemas
│   └── visualization/             # ASCII charts & gauges
└── tests/                         # 626 tests
```

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
<summary><strong>Urban Infrastructure: Public Transit Ridership Decline (2015-2019)</strong></summary>

```text
You are advising a city transit agency in 2019. You have been given only this information:

- Bus ridership: -18% (2015-2019)
- Light rail ridership: -12% same period
- City population: +6% same period
- Uber/Lyft launched in city 2014
- Transit agency budget: flat (inflation-adjusted)
- Fare: $2.50 (2019) vs. $2.00 (2015)
- Transit agency hypothesis: "Ride-hailing is stealing our riders"
- Mayor's office hypothesis: "Fares are too high for low-income residents"

Your task: Using only the limited information above, identify:
1. Why are both hypotheses likely wrong (or incomplete)?
2. What is the coordination failure between layers that neither hypothesis captures?
3. What changed structurally in how transit fits into the larger urban mobility system?
4. If you could ask for one piece of additional data, what would it be and why?

Constraint: Reason from structure first.
```
</details>

<details>
<summary><strong>Agriculture: Regenerative Certification (2019-2020)</strong></summary>

```text
You're analyzing regenerative agriculture in 2019-2020. Multiple weak signals:

- General Mills commits to 1M acres regenerative by 2030
- No standardized definition of "regenerative"
- Multiple competing certification schemes emerge
- Farmer adoption economics unclear: 3-5 year transition with yield penalties
- Soil carbon claims contested; measurement protocols vary
- Premium pricing emerging but market tiny (<1% of production)

Task: Identify which signals represent a structural shift vs. growth/noise. Predict what new equilibrium emerges by 2029. What layer (Micro/Meso/Macro/Meta) does the binding constraint move to?
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
<summary><strong>Healthcare: Rural Primary Care Physician Shortage (2016)</strong></summary>

```text
You are advising a state health department in 2016. You have been given only this information:

- Rural counties: 30 physicians per 100,000 population (2016) vs. 45 per 100,000 (2006)
- Urban counties: 280 per 100,000 (stable over same period)
- Medical school graduates: increasing by 3% annually nationwide
- Residency slots: increasing but concentrated in urban academic centers
- Average medical school debt: $190,000 (2016) vs. $120,000 (2006)
- Rural hospital closures: 80 hospitals closed 2010-2016
- State offers loan repayment for rural service: $50,000 over 5 years; uptake is low

Your task: Using only the limited information above, identify:
1. What is the root cause that the $50,000 loan repayment program fails to address?
2. Why does increasing medical school graduates not solve rural shortages?
3. What structural binding constraint operates at the Meso or Macro layer that makes individual incentives (Micro) insufficient?
4. What intervention would actually work, and why is it not being tried?

Constraint: You cannot request more data. Reason from structure, not statistics.
```
</details>

<details>
<summary><strong>Urban Infrastructure: Pothole Repair Backlog (2018)</strong></summary>

```text
You are advising a city public works department in 2018. You have been given only this information:

- Pothole repair requests: 12,000 annually (2018) vs. 8,000 (2013)
- Average time to repair: 45 days (2018) vs. 18 days (2013)
- Public works budget: +5% same period (below inflation)
- Road resurfacing budget: -20% same period (shifted to other priorities)
- Winter severity: roughly average (no unusual freeze-thaw cycles)
- City launches 311 app (2014) making pothole reporting easier
- Public works director hypothesis: "We need more crews and equipment"
- Budget office hypothesis: "The 311 app created fake demand from complainers"

Your task: Using only the limited information above, identify:
1. What is the feedback loop that's hidden in these numbers?
2. Why is this NOT primarily a resource constraint problem (despite budget cuts)?
3. What changed in system dynamics between 2013-2018 that both hypotheses miss?
4. Where does the root cause live: at operational level (Micro), institutional level (Meso), or policy level (Macro)?

Constraint: You cannot request more data. Reason from structure, not statistics.
```
</details>

<details>
<summary><strong>Education: Community College Enrollment Patterns (2009-2011)</strong></summary>

```text
You have access to the following data from 2009-2011:

- Community college enrollment surge: +17% (2009-2010) vs. 4-year colleges +3%
- For-profit college enrollment: +20% same period
- Student characteristics: 60% part-time, 40% over age 25, 35% single parents
- Remedial coursework: 60% placed in at least one remedial course
- Completion rates: 30% earn degree/certificate within 6 years
- Federal Pell Grant expansion: maximum award $5,550 (2010) vs. $4,050 (2007)
- State community college funding per student: -$500 (2008-2010) despite enrollment surge
- Employment outcomes: mixed, but certificate holders in healthcare/welding earn more than many BA holders

The conventional narrative in 2011 is about "access": recession drives enrollment, community colleges are affordable pathway to middle class.

Your task: Using only the signals above, identify the structural role community colleges have assumed that's different from their original mission. What service are they providing that other institutions have abandoned? Which layer contains the hidden transfer of responsibility?
```
</details>

<details>
<summary><strong>Agriculture: Indoor Vertical Farming Economics (2017-2018)</strong></summary>

```text
You're analyzing indoor vertical farming in 2017-2018. Multiple weak signals:

- AeroFarms raises $100M; Plenty (backed by SoftBank) raises $200M; combined valuations ~$1.5B
- Claims: 95% less water, 99% less land, no pesticides, 365-day growing
- LED efficiency improving 15% annually; energy still 30-40% of operating costs
- Crop limitation: leafy greens economical, but tomatoes/peppers/grains uneconomical
- Retail pricing: premium ($4-6 for lettuce vs. $2-3 conventional)
- Traditional greenhouses (Canada, Netherlands) achieve similar yields with 1/10th capital cost
- Several high-profile failures: FarmedHere closes Chicago facility (2017)

Task: Identify which signals represent a structural shift vs. growth/noise. Predict what new equilibrium emerges by 2027. What layer does the binding constraint move to?
```
</details>

<details>
<summary><strong>Healthcare: Organoid Systems (2016-2017)</strong></summary>

```text
You're analyzing organoid/tissue engineering in 2016-2017. Multiple weak signals:

- Cerebral organoids ("mini-brains") from iPSCs show cortical layering, raising ethical questions
- Multiple labs create gut, kidney, liver, retinal organoids with functional cell types
- Organoid biobanks form to model patient-specific disease
- Maturation remains limited: organoids resemble fetal, not adult tissue
- Emulate (organs-on-chips) partners with FDA for drug testing validation
- Animal testing debate intensifies; EU bans cosmetic animal testing
- Reproducibility issues: protocols vary wildly between labs

Task: Identify structural shift vs. growth/noise. Predict new equilibrium by 2026. What layer does the binding constraint move to?
```
</details>

<details>
<summary><strong>Technology: Voice Assistants (2017-2018)</strong></summary>

```text
Amazon Echo: ~30M units sold. Google Home: ~20M units sold. Apple HomePod launches (premium positioning, struggles). Smart speaker adoption: ~20% of U.S. households. Usage patterns: 90% simple queries (weather, timers, music). "Skills"/apps: thousands built, most get <100 users. Privacy concerns rising (always-listening devices).

Task: Are we early in S-curve (approaching mass adoption) or hitting plateau (novelty wearing off)? What needs to be true for voice to become primary interface by 2025? Is the constraint technology (NLP accuracy), use cases (not enough valuable tasks), or social (privacy concerns)?
```
</details>

<details>
<summary><strong>Structural Intervention: Academic Preprint Server Disruption</strong></summary>

```text
A well-funded nonprofit launched an interdisciplinary preprint server in 2021 designed to compete with arXiv, offering superior search, version control, integrated peer review, and automatic formatting for journal submission. Within two years it had attracted 40,000 submissions, institutional endorsements from twelve major research universities, and integration partnerships with three top-20 journals. By 2024, submission growth had flatlined at 2% monthly while arXiv continued growing at 6%, and two journal partnerships had quietly dissolved.

Using a multi-layer analytical framework, determine whether this system is in an emergent, capturing, stable, or terminal phase. Identify the single structural variable that most determines the outcome and specify what observable metric would confirm or falsify your prediction within 24 months.
```
</details>

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
python3 -c "from mantic_thinking.adapters.openai_adapter import get_openai_tools; print(len(get_openai_tools()), 'tools ready')"

# Full suite (626 tests)
python3 -m pytest -q
```

---

## Design Principles

1. **Immutable Core** -- The kernel cannot be modified
2. **Build On Top** -- Extensions shape inputs and interpret outputs, never the formula
3. **Deterministic** -- Same inputs always return same outputs
4. **No External APIs** -- Pure Python + NumPy + PyYAML. Bring your own LLM client
5. **Cross-Model** -- Claude, Kimi, Gemini, OpenAI, Ollama
6. **Complementary Suites** -- Friction for risks, Emergence for opportunities
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
| **2.0.0** | README overhaul, 17-tool stable surface, v2 milestone |
| 1.6.0 | System lock domain (friction + emergence), 17 tools |
| 1.5.x | Context assembly, MCP bootstrap, generic detect, PyPI alignment |
| 1.4.x | Interaction coefficients, per-tool YAML guidance, Test Drive prompts |
| 1.2.x | Layer visibility, layer coupling, safe kernel wrapper |
| 1.1.x | Namespace migration, import hygiene |
