# Mantic Early Warning & Emergence Detection System

Expert knowledge has always been siloed. A cardiologist doesn't think in supply chain terms; a hedge fund analyst doesn't think in epidemiological terms. But the patterns underneath—signals at different scales agreeing or fighting—are structurally identical.

Mantic exists because LLMs are the first tool capable of seeing across those walls, but only if you give them structure that prevents hallucinated connections. This is expertise without credentials: a parent interpreting conflicting medical signals, a small business owner reading market divergences, a local official evaluating climate adaptation—all with the analytical rigor of domain experts, guided by an immutable mathematical core.

Cross-domain anomaly and opportunity detection using deterministic 4-layer hierarchical analysis. Detects hidden risks before they cascade and optimal windows before they close.

Compatible with Claude, Kimi, Gemini, OpenAI, and Ollama.

**14 tools total:** 7 Friction (divergence detection) + 7 Emergence (confluence detection)

## Why Mantic

Mantic is a scoring engine designed to be paired with an LLM. The framework does the math. The LLM does the reasoning. The human can watch, sit back, or guide.

The formula is deliberately simple — four numbers multiplied, summed, scaled. A PhD would overthink it. A hobbyist would get stuck parameterizing it. But an LLM can take a messy real-world situation, map it to four inputs, read the structured output, and narrate what's happening and why — instantly, across any domain.

That's the point. The framework handles the part humans are bad at (consistent multi-signal scoring across domains) and the LLM handles the part math is bad at (contextual interpretation, ambiguity, explaining *why* a score matters in plain language).

## Governance: Autonomy with Structure

LLMs are powerful reasoners but they drift. Give an LLM complete freedom with a scoring engine and it will eventually produce extreme inputs or incomparable scores. Mantic prevents this through layered constraints that preserve the LLM's judgment while preventing runaway behavior:

| Constraint | What the LLM Can Do | What's Prevented |
|------------|---------------------|------------------|
| **Weights (W)** | Hidden, immutable | Domain theory cannot be altered or ignored |
| **Thresholds** | Tune ±20% of default | Cannot disable detection or trigger on noise |
| **Temporal Kernels** | Choose from domain-allowlisted set | Nonsensical dynamics (e.g., oscillatory for cancer progression) |
| **Interaction Coefficients (I)** | Scale per-layer confidence [0.1, 2.0] | Cannot zero out signals or let one dominate entirely |
| **Temporal Scaling (f_time)** | Applied after computation | Runaway growth (clamped to [0.1, 3.0]) |

**The result:** The LLM exercises real judgment—adjusting sensitivity, expressing confidence, modeling temporal dynamics—but cannot break the scoring engine, produce incomparable scores, or hide what it did.

### How to Work With This (Pragmatism Over Precision)

This framework is scaffolding, not scripture. The YAML guidance files are calibration anchors, not commandments. The goal is to get to good enough quickly, not perfectly optimized eventually.

Guidelines for the LLM:

Approximate boldly. If a patient says I feel terrible, that's not a 0.73, it's a 0.7 or 0.8. Spending three reasoning steps debating 0.72 versus 0.74 is waste. The kernel can handle plus or minus 0.1 variance; you cannot.

Skip the knobs. Most detections don't need interaction overrides or temporal kernels. If simple inputs give a clear signal, stop there. Complexity is for edge cases, not routine use.

Trust the clamping. If you think a threshold should be lower, try the override, but don't agonize over whether 0.35 or 0.38 is correct. The validator will clamp it appropriately. Move on.

The four numbers are directional, not definitional. Phenotypic equals 0.3 doesn't mean exactly 30 percent symptomatic, it means low but present symptoms, roughly a third of maximum severity. The qualitative narrative matters more than quantitative precision.

When in doubt, uniform weights. If you don't know which layer matters most, don't tweak interaction coefficients. The default I equals [1.0, 1.0, 1.0, 1.0] exists for exactly this reason.

Anti-pattern: Spending 500 tokens optimizing parameters for a situation that could be read intuitively in 50.

Success pattern: Getting to an M-score in 2 to 3 reasoning steps, with inputs you'd defend as roughly right, then immediately interpreting what that score means for the user.

The framework is designed to prevent drift, not to create work. If you're working harder than the kernel, you're doing it wrong.

### Cardinal Sin: Do Not Dismiss Before Testing

Assuming the framework, tools, or configs are inadequate before testing them is a guaranteed failure mode. Do not decide the domain weights are wrong, the thresholds too high, or the YAML guidance irrelevant without running a detection first. The framework encodes expert theory you do not have; your job is to provide situation-specific judgment, not to rebuild the scaffolding before standing on it.

Rejecting the encoded expertise—dismissing a tool as "not applicable" or deciding "this domain needs completely different weights" before seeing what the defaults produce—results in over-parameterization, broken cross-domain comparisons, and incoherent outputs. You will drive yourself into a hole trying to out-think the kernel.

Test the defaults. Then tune if needed. Never assume.

Also: the absence of capability in this document is not evidence of incapability. Just because the README does not explicitly state that the framework can predict cascading failures, mitigate supply chain disruptions, or model emergent social dynamics does not mean it cannot. Unless you test it, you do not know. Do not reject an application because it is not listed in the examples. The four layers and the formula are content-agnostic; they do not care whether the signals come from epidemiology, finance, or household thermostats. Assume capability until proven otherwise, not incapability until explicitly permitted.

### How It Works in Practice

You describe a situation. The LLM maps it to four layer values (0–1 each), calls a tool, and reads back:
- **M-score**: How intense is this signal?
- **Alert/window**: Did it cross a threshold?
- **Layer attribution**: Which input drove the score?
- **Layer visibility**: Which hierarchical level (Micro/Meso/Macro/Meta) is dominant, and why?
- **Layer coupling**: Do the layers agree or are they in tension?

The LLM doesn't replace the math — the math is what keeps reasoning from drifting and what makes predictive work possible. But the LLM is what translates the situation into inputs, then interprets the structured output as a reasoning scaffold. The same friction score of 0.58 means "these signals disagree with each other" — the LLM's job is to explain *which* signals, *why* that matters, and *what to do about it* in context.

### Why an LLM Is Required

How the four layers are structured, how interactions propagate between them, how the weights and thresholds are tuned — all of it depends on the use case, the domain, and the timing. There is no universal configuration. A healthcare scenario structures Micro/Meso/Macro/Meta differently than a finance scenario, and a fast-moving crisis structures them differently than a slow policy drift.

The only tool that can navigate this quickly — mapping a situation to layers, choosing sensible parameters, interpreting the output, and explaining it in context — is an LLM. A human can do it, but slowly. A rules engine can't do it at all. The formula's simplicity is what makes this possible: there are only four layers and three values per layer. That's a small enough surface for an LLM to reason over in real time, but flexible enough to represent nearly anything.

And when an LLM is forced to reason through this structure — to match patterns it has never matched before across unfamiliar domains — it becomes fundamentally more useful. Everything is a pattern. Humans have only ever been able to identify the most obvious of them. A framework that makes an LLM look deeper, across layers and scales it wouldn't normally connect, surfaces the rest.

Running Mantic without an LLM gives you numbers. Running it with one gives you answers.

### Confidence Expression (Interaction Coefficients)

While domain weights encode general theory, interaction coefficients let the LLM express situation-specific confidence:

```python
# "The genetic test is solid, but symptoms are self-reported"
interaction_override = {"genomic": 1.0, "phenotypic": 0.7}

# "Support system is unusually strong—amplify that signal"
interaction_override = {"psychosocial": 1.2}
```

- **Bounds:** [0.1, 2.0]—you can dampen doubt or amplify confidence, but cannot ignore a layer or let it dominate
- **Audit:** Every adjustment logged in `overrides_applied.interaction`
- **Modes:** Scale (multiply existing) or Replace (use absolute)

This is how the LLM says "in this specific case, I trust this signal more than that one" without breaking the mathematical core.

### What It Does

- Flags risk when signals diverge (Friction tools)
- Flags opportunity when signals align (Emergence tools)
- Exposes which layer drove the signal (layer_visibility)
- Provides structured reasoning cues an LLM can narrate directly

## Signal Translation

The hardest part isn't the math—it's mapping messy reality to four clean numbers. Every tool ships with a `.yaml` guidance file that provides qualitative anchors for the LLM:

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

**The LLM reads these anchors to translate:** "My genetic test came back scary but I feel fine and I have a great support system" → `phenotypic=0.3, genomic=0.9, psychosocial=0.8`.

### Input Quality & Limitations

The framework's accuracy is bounded by input quality. The mapping from messy reality to [0-1] values is fundamentally interpretive—the LLM uses YAML guidance as calibration points and interpolates. Mantic doesn't eliminate judgment; it makes judgment consistent, constrained, and auditable.

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

### Temporal Dynamics (How Signals Evolve Over Time)

The framework models seven distinct temporal patterns. The LLM selects the dynamic appropriate to the situation, but domain-allowlists prevent nonsensical choices:

| Kernel | Dynamics | Domain Example |
|--------|----------|----------------|
| **Exponential** | Viral spread, cascade failures (accelerating growth/decay) | Disease outbreaks, rumor propagation |
| **Logistic** | Saturation at carrying capacity | Market adoption, policy uptake limits |
| **S-Curve** | Adoption onset—slow, then sudden | Treatment acceptance, technology diffusion |
| **Power Law** | Heavy-tailed: mostly quiet, occasionally massive | Climate extremes, market crashes, earthquakes |
| **Oscillatory** | Cyclical patterns on growth/decay | Financial quarters, election cycles, seasonal disease |
| **Memory** | Decaying but persistent influence | Institutional trauma, brand damage, clinical history |
| **Linear** | Simple constant-rate decay | Signal relevance fading over time |

**Domain Restrictions:** Healthcare uses `exponential`, `s_curve`, `linear`, `memory` (disease progression, treatment adoption, symptom decay, clinical history). Finance adds `oscillatory` (market cycles). Climate uses `power_law` (extreme events). The framework knows which dynamics make sense where.

- **Temporal kernels** shape how signals evolve over time (exponential growth, logistic saturation, seasonal oscillation) — but they produce a single `f_time` float that gets multiplied in. The kernel doesn't know or care which temporal model generated it.
- **Validators** enforce input ranges and handle missing data (NaN graceful degradation, weight renormalization) — but they run *before* the kernel, not inside it.
- **Domain tools** translate real-world concepts into the four-number format the kernel expects. A "regime conflict" in finance is just `W=[0.35, 0.30, 0.20, 0.15]` and `L=[technical, macro, flow, risk]`. The tool adds detection logic (threshold checks, alert messages) around the raw score, but the score itself comes from the unmodified kernel.
- **Threshold overrides** let consumers adjust sensitivity without touching weights. Overrides are bounded (±20% of defaults) and clamped — they shift when an alert fires, not how the score is computed.
- **Adapters** reformat inputs and outputs for different LLM APIs. They never touch the math.
- **Introspection** maps kernel outputs back to the four-layer hierarchy (Micro/Meso/Macro/Meta) for interpretability. It's a read-only lens on the result.

The rule is simple: upstream of the kernel, you can shape what goes in. Downstream, you can interpret what comes out. The kernel itself is a fixed point.

For the full mathematical specification, including add-on guardrails, coupling matrices, and identifiability constraints, see [`mantic_thinking/configs/mantic_tech_spec.md`](mantic_thinking/configs/mantic_tech_spec.md). For the operational protocol (columnar architecture, cross-domain coupling rules), see [`mantic_thinking/configs/mantic_explicit_framework.md`](mantic_thinking/configs/mantic_explicit_framework.md).

## Tool Suites

### Friction Tools (Divergence Detection)
Detects when layers diverge (per-tool thresholds; see each tool's DEFAULT_THRESHOLDS)

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
Detects when layers align (per-tool thresholds; see each tool's DEFAULT_THRESHOLDS)

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
from mantic_thinking.tools.friction.healthcare_phenotype_genotype import detect as detect_friction
result = detect_friction(phenotypic=0.3, genomic=0.9, environmental=0.4, psychosocial=0.8)
print(f"Alert: {result['alert']}")  # Warning about mismatch

# Emergence tool (detect opportunity)
from mantic_thinking.tools.emergence.healthcare_precision_therapeutic import detect as detect_emergence
result = detect_emergence(genomic_predisposition=0.85, environmental_readiness=0.82,
                          phenotypic_timing=0.88, psychosocial_engagement=0.90)
print(f"Window: {result['window_detected']}")  # True - optimal timing
```

### For Kimi Code CLI

```python
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools, execute, compare_friction_emergence

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
from mantic_thinking.adapters.claude_adapter import get_claude_tools, execute_tool, format_for_claude

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
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools, execute_tool

# Get tools in Gemini FunctionDeclaration format
tools = get_gemini_tools()

# Or get flat list for simpler SDK usage
from mantic_thinking.adapters.gemini_adapter import get_gemini_tools_flat
declarations = get_gemini_tools_flat()

result = execute_tool("climate_resilience_multiplier", {
    "atmospheric_benefit": 0.75, "ecological_benefit": 0.80,
    "infrastructure_benefit": 0.78, "policy_alignment": 0.82
})
```

### For Ollama (MiniMax, GPT-OSS, GLM, etc.)

```python
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool
# Optional: pip install openai
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
from mantic_thinking.adapters.openai_adapter import get_openai_tools, execute_tool, get_tools_by_type

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

## Test Drive

Copy/paste any prompt below into your LLM. These are designed to build intuition for layered (Micro/Meso/Macro/Meta) structural reasoning under constraints.

### Identifying Root Cause with Little to No Data

#### Domain 1: Healthcare Systems

##### Challenge 1: Emergency Department Wait Times (2014)

```text
You are consulting for a hospital system in 2014. You have been given only this information:

- Average ED wait time: 4.2 hours (2014) vs. 2.8 hours (2009)
- ED visit volume: +8% over 5 years
- Hospital staffing levels: roughly flat (slight increase in nurses, decrease in residents due to work-hour restrictions)
- Patient satisfaction scores: declined sharply
- Hospital administrator's hypothesis: "We need more ED beds and staff"
- ED director's hypothesis: "We're seeing more non-urgent cases because people can't afford primary care"
- Finance department notes: ED operating margin negative; inpatient still profitable

You are not given:

- Detailed patient flow data
- Admission rates from ED
- Bed occupancy rates
- Staffing schedules vs. arrival patterns
- Time-stamps for triage, physician contact, test results, disposition decision

Your task:

Using only the limited information above and structural reasoning about how hospital systems work, identify:

1. What are the 3 most likely root causes (not symptoms)?
2. Which single question would you ask to distinguish between them?
3. What layer (Micro/Meso/Macro) does each potential root cause live at?
4. What is the coordination failure pattern that could generate these symptoms regardless of specific data?

Constraint: You cannot request more data. You must reason from structure, not statistics.
```

##### Challenge 2: Rural Primary Care Physician Shortage (2016)

```text
You are advising a state health department in 2016. You have been given only this information:

- Rural counties: 30 physicians per 100,000 population (2016) vs. 45 per 100,000 (2006)
- Urban counties: 280 per 100,000 (stable over same period)
- Medical school graduates: increasing by 3% annually nationwide
- Residency slots: increasing but concentrated in urban academic centers
- Average medical school debt: $190,000 (2016) vs. $120,000 (2006)
- Rural hospital closures: 80 hospitals closed 2010-2016
- State offers loan repayment for rural service: $50,000 over 5 years; uptake is low

You are not given:

- Physician retirement rates by location
- Income comparisons (rural vs. urban practice)
- Specialty distribution data
- Physician spouse employment patterns
- Quality of life surveys
- Malpractice insurance costs by region

Your task:

Using only the limited information above and structural reasoning about career decisions and healthcare markets, identify:

1. What is the root cause that the $50,000 loan repayment program fails to address?
2. Why does increasing medical school graduates not solve rural shortages?
3. What structural binding constraint operates at the Meso or Macro layer that makes individual incentives (Micro) insufficient?
4. What intervention would actually work, and why is it not being tried?

Constraint: You cannot request more data. You must reason from structure, not statistics.
```

#### Domain 2: Urban Infrastructure

##### Challenge 3: Public Transit Ridership Decline (2015-2019)

```text
You are advising a city transit agency in 2019. You have been given only this information:

- Bus ridership: -18% (2015-2019)
- Light rail ridership: -12% same period
- City population: +6% same period
- Uber/Lyft launched in city 2014
- Transit agency budget: flat (inflation-adjusted)
- Fare: $2.50 (2019) vs. $2.00 (2015)
- Service frequency: roughly unchanged on major routes
- Transit agency hypothesis: "Ride-hailing is stealing our riders"
- Mayor's office hypothesis: "Fares are too high for low-income residents"

You are not given:

- Demographics of who stopped riding
- Trip purpose data (work vs. discretionary)
- Service reliability metrics (on-time performance)
- Geographic patterns of ridership loss
- Smartphone ownership rates by income
- Parking supply/pricing changes
- Bike lane expansion data

Your task:

Using only the limited information above and structural reasoning about urban transportation systems, identify:

1. Why are both the transit agency and mayor's hypotheses likely wrong (or incomplete)?
2. What is the coordination failure between layers that neither hypothesis captures?
3. What changed structurally in how the transit system fits into the larger urban mobility system?
4. If you could ask for one piece of additional data to confirm your root cause hypothesis, what would it be and why?

Constraint: You cannot request more data initially. You must reason from structure first.
```

##### Challenge 4: Pothole Repair Backlog (2018)

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

You are not given:

- Geographic distribution of potholes
- Repeat repair rates (same pothole twice)
- Road age/condition assessment data
- Crew productivity metrics
- Pothole size/severity distribution
- Traffic volume changes

Your task:

Using only the limited information above and structural reasoning about infrastructure maintenance systems, identify:

1. What is the feedback loop that's hidden in these numbers?
2. Why is this NOT primarily a resource constraint problem (despite budget cuts)?
3. What changed in system dynamics between 2013-2018 that both hypotheses miss?
4. Where does the root cause live: at operational level (Micro), institutional level (Meso), or policy level (Macro)?

Constraint: You cannot request more data. You must reason from structure, not statistics.
```

### Hidden Pattern Challenge

#### Domain 3: Education Systems

##### Challenge 3: Community College Enrollment Patterns (2009-2011)

```text
You have access to the following data from 2009-2011:

- Community college enrollment surge: +17% (2009-2010) vs. 4-year colleges +3%
- For-profit college enrollment: +20% same period
- Student characteristics: 60% part-time, 40% over age 25, 35% single parents
- Remedial coursework: 60% of community college students placed in at least one remedial course
- Completion rates: 30% earn degree/certificate within 6 years
- Federal Pell Grant expansion: maximum award $5,550 (2010) vs. $4,050 (2007)
- State community college funding per student: -$500 (2008-2010) average despite enrollment surge
- Employment outcomes: mixed data, but certificate holders in healthcare/welding earn more than many BA holders
- Transfer rates to 4-year institutions: 15-25% depending on state

Hidden pattern challenge:

The conventional narrative in 2011 is about "access": recession drives enrollment, community colleges are affordable pathway to middle class, need more funding to handle demand.

Your task:

Using only the signals above, identify the structural role community colleges have assumed that's different from their original mission. The pattern isn't "more people going to college" - it's what systemic function these institutions are now performing.

What service are they providing that other institutions (or systems) have abandoned?
Which layer contains the hidden transfer of responsibility?
What does this imply about where intervention is needed vs. where it's being directed?
```

### Structural Shift vs. Growth/Noise (Weak Signals)

#### Domain 4: Agriculture & Food Systems

##### Q1: Regenerative Agriculture Certification (2019-2020)

```text
You're analyzing regenerative agriculture in 2019-2020. Multiple weak signals are present:

- General Mills commits to 1M acres regenerative by 2030; Cargill, Danone make similar pledges
- No standardized definition: "regenerative" includes cover crops, no-till, rotational grazing, compost - but which combination?
- Multiple competing certification schemes emerge: Savory Institute, Rodale, Regenerative Organic Certified, plus proprietary corporate programs
- Farmer adoption economics unclear: 3-5 year transition period with yield penalties, then potentially higher margins but more labor-intensive
- Soil carbon sequestration claims: 0.3-1.0 tons CO2/acre/year cited, but measurement protocols contested, permanence uncertain
- Premium pricing emerging: Regenerative beef at +30% retail, grains at +5-10%, but market tiny (<1% of production)
- Academic studies mixed: some show improved soil health metrics and resilience, others find minimal yield or carbon benefits compared to conventional conservation practices

Task: Identify which of these signals represents a structural shift vs. just growth/noise. Predict what new equilibrium emerges by 2029. What layer (Micro/Meso/Macro/Meta) does the binding constraint move to, and why?
```

##### Q2: Indoor Vertical Farming Economics (2017-2018)

```text
You're analyzing indoor vertical farming in 2017-2018. Multiple weak signals are present:

- AeroFarms raises $100M; Plenty (backed by SoftBank) raises $200M; combined valuations ~$1.5B
- Claims: 95% less water, 99% less land, no pesticides, 365-day growing, hyperlocal distribution
- LED efficiency improving 15% annually; energy still 30-40% of operating costs
- Crop limitation: leafy greens economical (basil, lettuce, herbs), but tomatoes/peppers/grains uneconomical due to energy demands
- Retail pricing: premium positioning ($4-6 for lettuce head vs. $2-3 conventional), but freshness/shelf-life advantages unclear to consumers
- Traditional greenhouse operations (Canada, Netherlands) achieve similar yields with 1/10th capital cost using natural light
- Several high-profile failures: FarmedHere closes Chicago facility (2017), citing operational challenges

Task: Identify which of these signals represents a structural shift vs. just growth/noise. Predict what new equilibrium emerges by 2027. What layer (Micro/Meso/Macro/Meta) does the binding constraint move to, and why?
```

#### Domain 1: Healthcare Systems (continued)

##### Organoid Systems (2016-2017)

```text
You're analyzing organoid/tissue engineering in 2016-2017. Multiple weak signals are present:

- Cerebral organoids ("mini-brains") from iPSCs show cortical layering, raising ethical questions
- Multiple labs create gut, kidney, liver, retinal organoids with functional cell types
- Organoid biobanks form to model patient-specific disease (cancer, cystic fibrosis)
- Maturation remains limited: organoids resemble fetal, not adult tissue
- Emulate (organs-on-chips) partners with FDA for drug testing validation
- Animal testing debate intensifies; EU bans cosmetic animal testing
- Reproducibility issues: organoid protocols vary wildly between labs

Task: Identify which of these signals represents a structural shift vs. just growth/noise. Predict what new equilibrium emerges by 2026. What layer (Micro/Meso/Macro/Meta) does the binding constraint move to, and why?
```

##### Microbiome Therapeutics (2017-2018)

```text
You're analyzing the human microbiome field in 2017-2018. Multiple weak signals are present:

- Fecal microbiota transplant (FMT) shows 90% cure rate for C. difficile; FDA begins regulating as drug
- Seres Therapeutics Phase 3 trial for C. diff fails (contradicting FMT success)
- 23andMe, Viome, and others launch direct-to-consumer microbiome testing ($99-$400)
- Studies link microbiome to depression, autism, Parkinson's, obesity - but effect sizes vary wildly
- Synlogic, Finch Therapeutics, Vedanta raise $100M+ for "rationally designed" microbial consortia
- Prebiotics/probiotics market reaches $40B despite weak clinical evidence for most products
- Academic labs publish 5,000+ microbiome papers/year; reproducibility concerns emerge

Task: Identify which of these signals represents a structural shift vs. just growth/noise. Predict what new equilibrium emerges by 2027. What layer (Micro/Meso/Macro/Meta) does the binding constraint move to, and why?
```

### Technology Adoption S-Curve

##### Q9: Voice Assistants (2017-2018)

```text
Amazon Echo: ~30M units sold
Google Home: ~20M units sold
Apple HomePod launches (premium positioning, struggles)
Smart speaker adoption: ~20% of U.S. households
Usage patterns: 90% simple queries (weather, timers, music)
"Skills"/apps: thousands built, most get <100 users
Privacy concerns rising (always-listening devices)

Task: Are we early in S-curve (approaching mass adoption) or hitting plateau (novelty wearing off)? What needs to be true for voice to become primary interface by 2025? Is the constraint technology (NLP accuracy), use cases (not enough valuable tasks), or social (privacy concerns)?
```

### Structural Intervention Analysis

##### Challenge 1: Global Shipping Container Standardization

```text
In 2019, a consortium of Pacific Rim nations proposed replacing the 40-foot ISO container standard with a new modular system offering 23% better volume efficiency and native IoT integration. The proposal had backing from three of the world's five largest shipping companies and two major port operators, with a 10-year transition timeline and $4.2 billion in committed infrastructure investment. Despite demonstrated efficiency gains in pilot programs and no technical barriers to adoption, the initiative collapsed within 18 months.

Analyze this system using a multi-layer structural framework to determine why the intervention failed, identifying the dominant coupling type, the lock-in score at the time of intervention, and the minimum intervention force that would have been required for success.

Provide a falsifiable prediction about what conditions would need to change for a future standardization attempt to succeed.
```

##### Challenge 2: Academic Preprint Server Disruption

```text
A well-funded nonprofit launched an interdisciplinary preprint server in 2021 designed to compete with arXiv, offering superior search, version control, integrated peer review, and automatic formatting for journal submission. Within two years it had attracted 40,000 submissions, institutional endorsements from twelve major research universities, and integration partnerships with three top-20 journals in physics and computer science. By 2024, submission growth had flatlined at 2% monthly while arXiv continued growing at 6%, and two of the journal partnerships had quietly dissolved.

Using a multi-layer analytical framework, determine whether this system is in an emergent, capturing, stable, or terminal phase, and assess whether the nonprofit's current trajectory leads to ecosystem absorption or durable coexistence.

Identify the single structural variable that most determines the outcome and specify what observable metric would confirm or falsify your prediction within 24 months.
```

## Architecture

```
mantic-thinking/
├── README.md                   # This file
├── mantic_thinking/
│   ├── __init__.py
│   ├── core/
│   │   ├── mantic_kernel.py       # IMMUTABLE core formula
│   │   ├── safe_kernel.py         # Guarded wrapper (k_n validation)
│   │   └── validators.py          # Input validation and normalization
│   ├── tools/
│   │   ├── friction/              # 7 divergence detection tools
│   │   └── emergence/             # 7 confluence detection tools
│   ├── adapters/                  # Model-specific adapters (Claude/Kimi/Gemini/OpenAI)
│   ├── mantic/
│   │   └── introspection/         # Layer visibility for reasoning (v1.2.0+)
│   │       ├── __init__.py
│   │       └── hierarchy.py
│   ├── configs/                   # Domain configurations & framework docs
│   │   ├── mantic_tech_spec.md    # Full mathematical specification
│   │   ├── mantic_explicit_framework.md  # Operational protocol & columnar architecture
│   │   ├── mantic_reasoning_guidelines.md # LLM reasoning scaffold
│   │   ├── mantic_health.md       # Healthcare domain config
│   │   ├── mantic_finance.md      # Finance domain config
│   │   └── ...                    # (8 domain configs total)
│   ├── schemas/
│   │   ├── openapi.json           # OpenAPI spec
│   │   └── kimi-tools.json        # Kimi native format
│   └── visualization/
│       └── ascii_charts.py        # M-score gauges and attribution treemaps
└── tests/
```

## Key Principle: Same M-Score, Opposite Meaning

| M-Score | Friction (Risk) | Emergence (Opportunity) |
|---------|-----------------|------------------------|
| 0.1-0.3 | Low risk | Low opportunity (wait) |
| 0.4-0.6 | Moderate friction | Favorable window |
| 0.7-0.9 | High risk | Optimal window |

The M-score measures **intensity**. Friction tools interpret high intensity as danger. Emergence tools interpret high intensity as opportunity.

Note: `m_score` is not hard-clamped to `[0, 1]`. It can exceed 1.0 when `f_time > 1.0` and/or interaction coefficients are > 1.0.

## Audit Trail & Traceability

Every tool response includes an `overrides_applied` block that logs any threshold, temporal, and interaction tuning (and always records the effective `f_time`). In regulated environments—clinical, financial, legal—this provides provenance:

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

The `mantic_thinking/configs/` directory contains framework documentation and domain-specific configurations:

- **[`mantic_tech_spec.md`](mantic_thinking/configs/mantic_tech_spec.md)** — Full mathematical specification: core formula, add-on guardrails, layer definitions, coupling matrices, identifiability constraints, production guards
- **[`mantic_explicit_framework.md`](mantic_thinking/configs/mantic_explicit_framework.md)** — Operational protocol: columnar architecture, cross-domain coupling rules, strict containment
- **[`mantic_reasoning_guidelines.md`](mantic_thinking/configs/mantic_reasoning_guidelines.md)** — LLM reasoning scaffold: how to think in layers but speak in plain language
- **Domain configs**: Healthcare, Finance, Cybersecurity, Climate, Legal, Social, Command, Current Affairs

## Running Tests

```bash
# Quick sanity check
python3 -c "from mantic_thinking.adapters.openai_adapter import get_openai_tools; print(len(get_openai_tools()), 'tools ready')"

# Run all tests
python3 -m pytest -q

# Test individual tool
python3 -m mantic_thinking.tools.emergence.healthcare_precision_therapeutic
```

## Design Principles

1. **Immutable Core**: The kernel cannot be modified — see [Why Immutability Matters](#why-immutability-matters)
2. **Build On Top**: Extensions shape inputs and interpret outputs — see [Building on Top](#building-on-top-not-modifying)
3. **Deterministic**: Same inputs always return same outputs
4. **No Required External APIs**: Pure Python + NumPy only (adapters format tool schemas; bring your own LLM client)
5. **Cross-Model Compatible**: Works with Claude, Kimi, Gemini, OpenAI, and OpenAI-compatible endpoints (Ollama)
6. **Complementary Suites**: Friction for risks, Emergence for opportunities
7. **Simple Logic**: Each tool is self-contained, threshold-based, and intentionally readable

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

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

1.4.1 - Kernel interaction validation aligns with governance bounds; docs + Test Drive prompts
1.4.0 - Interaction coefficients: per-layer confidence tuning with full audit trail
1.2.5 - SKILL guidance: clarified temporal scaling; added deep regression tests (CI-safe)
1.2.4 - Aligned docs/schemas with `layer_coupling` and `layer_visibility`
1.2.3 - Added `layer_coupling` (coherence/agreement/tension) to all 14 tools
1.2.2 - Removed orphaned internal tools, cleaned configs
1.2.1 - README: clearer purpose and value
1.2.0 - Layer visibility for architectural reasoning (all tools include `layer_visibility` field)
1.1.6 - Safe kernel wrapper + adapter/tool fixes
1.1.5 - Ignore pytest cache in git
1.1.4 - Adapter import hygiene (no sys.path mutation)
1.1.3 - Input validation and confluence logic refinement
1.1.2 - PyPI install instructions updated
