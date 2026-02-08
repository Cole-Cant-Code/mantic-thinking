# **Mantic Framework (M)**

## Technical Structure & Hierarchy
### A Deterministic System for Pattern Detection Across Scales

---

## The Mantic Constant: Integrity of the Core

The Core Formula and Temporal Kernels constitute the fundamental "physics" of the Mantic system. Their immutability is paramount; the entire hierarchical logic, pattern-detection capabilities, and cross-domain validity depend on strict adherence to these mathematical foundations.

While the framework is designed for extensibility through optional "Add-ons" (such as scaling, normalization, and coupling), the underlying identity must remain untouched to ensure deterministic stability.

---

## Core Formula (Immutable)

The fundamental identity of the framework:

$$\boxed{M = \left(\sum_{i} W_i \cdot L_i \cdot I_i\right) \times f_{\text{time}}(t)}$$

- **Spatial Component** – Integrated state of all hierarchical layers
- **Temporal Component** – Global modulator defining system evolution

> **Notation:** Let $S(t) := \sum_i W_i L_i(t) I_i(t)$. Then $M(t) = S(t) \cdot f_{\text{time}}(t)$.

---

## Core Formula Add-Ons (Optional Extensions)

Technical scaling and normalization for software implementation:

- **$k_n$ (Normalization)** – Standardizes output:
  $$M_{\text{final}} = \frac{M}{k_n}$$

- **$C_{ij}$ (Coupling)** – Cross-layer feedback matrix for complex interactions (used to *generate* $L_i, I_i$; does **not** alter the immutable form of $M$).

> **Guardrail:** Add-ons must not modify $M = (\sum_i W_i L_i I_i) \cdot f_{\text{time}}(t)$; they only standardize inputs/outputs or shape $L, I$ dynamically upstream.

---

## The Four Hierarchical Layers

### 1. MICRO (μ) — *Immediate*
High frequency / local impact
- **$W_\mu$** – Micro Weight
- **$L_\mu$** – Micro Value  
- **$I_\mu$** – Micro Interaction

### 2. MESO (m) — *Short-term*
Collective dynamics / group coupling
- **$W_m$** – Meso Weight
- **$L_m$** – Meso Value
- **$I_m$** – Meso Interaction

### 3. MACRO (M) — *Medium-term*
System-wide patterns / averages
- **$W_M$** – Macro Weight
- **$L_M$** – Macro Value
- **$I_M$** – Macro Interaction

### 4. META (Ω) — *Long-term*
Learning / adaptation / memory
- **$W_\Omega$** – Meta Weight
- **$I_\Omega$** – Meta Interaction
- **$L_\Omega$ (Meta Value):**
  $$L_\Omega(t) = \left(\sum_j a_j \cdot \theta_j\right) \times e^{k \cdot t}$$
  - **$a_j$** – Adaptation coefficients
  - **$\theta_j$** – System parameters
  - **$k$** – Learning-rate constant

> **Partitioning:** The global index set is the disjoint union of layer indices: $\mathcal{E} = \mathcal{E}_\mu \cup \mathcal{E}_m \cup \mathcal{E}_M \cup \mathcal{E}_\Omega$.

---

## Core Parameters

### Spatial (State)
- **Weights [$W$]** – Importance/concentration per layer (often $W_i \geq 0$, $\sum_i W_i = 1$ for identifiability)
- **Values [$L$]** – Measurable quantities / data payload
- **Interactions [$I$]** – Internal per-layer coupling strength (bounded, domain-defined)

### Temporal (Evolution)
- **$n$ (Novelty)** – Pattern unusualness ($n > 0$ amplify, $n < 0$ attenuate)
- **$\alpha$ (Alpha)** – Sensitivity/amplification coefficient
- **$t$ (Time)** – Evaluation window
- **$S_c$ (Criticality)** – Saturation threshold (phase-shift add-on; does **not** alter core identity)

> **Units:** Ensure $n\alpha t$ is dimensionless when used inside exponentials; $\alpha$ should carry inverse-time units if $n$ is dimensionless.

---

## Behavioral Modes (Temporal Modulators)

Transform signals as **Result = Signal × Mode($n, \alpha, t$)**. These are **choice functions** for $f_{\text{time}}(t)$.

| Mode | Formula | Use Case |
|------|---------|----------|
| **Exponential** | $\text{signal} \times e^{n\alpha t}$ | Viral / cascade growth or decay |
| **Logistic** | $\text{signal} \times \frac{1}{1+e^{-n\alpha t}}$ | Saturation / carrying capacity / limits |
| **S-Curve** | $\text{signal} \times \frac{1}{1+e^{-\alpha(t-t_0)}}$ | Adoption / learning onset around $t_0$ |

---

## Temporal Kernels (Immutable Plug-Ins)

| Kernel | Formula | Dynamics |
|--------|---------|----------|
| **Power-Law** | $(1+t)^{n\alpha \cdot \text{exponent}}$ | Heavy-tailed dynamics |
| **Oscillatory** | $e^{n\alpha t} \cdot 0.5[1+0.5\sin(ft)]$ | Seasonal rhythms |
| **Memory** | $1 + [\text{memory\_strength} \cdot e^{-t}]$ | Decaying influence |

> **Positivity & Stability:** Choose parameters so $f_{\text{time}}(t) > 0$ for all $t$ in use.

---

## Implementation Components

**`mantic_core.py`** structure:

```python
def mantic_kernel(W, L, I, f_time, k_n=1.0):
    """
    W: array [E]; L, I: arrays [T, E] or callables t->R^E; 
    f_time: array [T] or callable t->R+
    Returns: M [T], S [T]
    """
    S = (W[None, :] * L * I).sum(axis=1)
    M = (S * f_time) / k_n
    return M, S
```

**Attribution shares:** $s_{i,t} = \frac{W_i L_{i,t} I_{i,t}}{\sum_j W_j L_{j,t} I_{j,t}}$

**Layer roll-ups:** Sums of $s_{i,t}$ over $(\mu, m, M, \Omega)$.

**Classes:**
- `BehavioralModes` – Transformation class (gates / modes)
- `TemporalKernels` – Logic plug-in class
- `Constants` – `MAX_VAL = 1e300` (production-only saturation guard)

---

## Mathematical Properties (Proven)

| Property | Definition | Brief Proof |
|----------|------------|-------------|
| **Deterministic** | Same inputs $\Rightarrow$ same output | $M(t)=S(t)f(t)$ with $S$ finite linear sum of deterministic terms |
| **Time-Separable** | Spatial state decoupled from temporal | By definition $M(t)=S(t) \cdot f_{\text{time}}(t)$; separable rank-1 in $(t)$ |
| **Scale-Hierarchical** | Operates across 4 distinct time horizons | Partition indices by $({\mu,m,M,\Omega})$, write $S=\sum_\ell S_\ell$ |
| **Meta-Convergent** | $\Omega$ follows long-term growth laws | If $S_\ell(t)\sim c_\ell e^{\gamma_\ell t}$ and $L_\Omega(t)\sim c_\Omega e^{kt}$, $\Omega$ share $\to$ dominance based on rate comparison |

> **Identifiability note:** The transformation $(W_i,L_i) \mapsto (\lambda_i W_i, L_i/\lambda_i)$ leaves $S$ unchanged. Enforce normalization (e.g., $\sum_i W_i=1$, $W_i \geq 0$) for unique weights.

---

## Use Cases / Domains (Illustrative)

| Domain | Micro | Meso | Macro | Meta |
|--------|-------|------|-------|------|
| **Healthcare** | Vitals | Ward | Hospital | Policy |
| **Finance** | Trade | Portfolio | Market | Regulation |
| **Operations** | Part | Team | Network | Org-Learning |
| **Personal Health** | Waking HR/HRV | Recovery | Weekly trend | Personal baseline |
| **Family Network** | Individual M | Cross-coupling | Care capacity | Household resilience |

---

## Workflow

1. **Domain Mapping** – Define $(W, L, I)$ for each layer (units, bounds, cadence)
2. **Parameter Tuning** – Set $(n, \alpha, t)$ and select Behavioral Mode / Kernel
3. **Execution** – Run `mantic_kernel()` or apply core $M$ formula
4. **Interpretation** – Inspect layer contributions and optional scaling ($k_n$); compute shares $s_{i,t}$
5. **Action** – Trigger alerts or policy shifts based on M-Score, guarding with `MAX_VAL`

---

## Production Guards & Best Practices

- **Normalization:** Choose and document one scheme (e.g., $\sum_i W_i=1$)
- **Bounds:** Clip $L, I$ to validated ranges; ensure $f_{\text{time}}(t) > 0$
- **Overflow/Underflow:** Apply `MAX_VAL`, log warnings when $|\log f_{\text{time}}|$ exceeds thresholds
- **Auditability:** Persist $(W, L, I, f_{\text{time}})$ snapshots for exact recompute
- **Versioning:** Bump **KernelSet** and **LayerMap** versions independently; never version-skew the core identity

---

*End of Specification*
