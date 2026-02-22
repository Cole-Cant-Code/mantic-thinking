# Mantic Framework Configurations

This directory contains domain-specific configurations and framework documentation for the Mantic Early Warning System.

## Core Framework Documentation

| File | Description |
|------|-------------|
| `mantic_tech_spec.md` | Technical specification - core formula, mathematical properties, implementation details |
| `mantic_explicit_framework.md` | Explicit framework mode - technical operating protocol with columnar architecture |
| `mantic_reasoning_guidelines.md` | Reasoning assistant guidelines - internal thinking scaffold |
| `mantic_boundary_weaver.md` | Cross-silo navigation pattern - translating complexity between boundaries |
| `mantic_early_warning_tools.md` | Friction tools descriptions (8 divergence detection tools) |
| `mantic_value_emergence_tools.md` | Emergence tools descriptions (8 confluence detection tools) |

## Ollama Compatibility

All Mantic tools work with Ollama's OpenAI-compatible endpoint:
```python
client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
```

Tested with: MiniMax M2.1, GPT-OSS, GLM-4, Llama 3.1/3.2, Qwen 2.5, and other tool-capable models.

## Domain-Specific Configurations

| File | Domain | Description |
|------|--------|-------------|
| `mantic_health.md` | Healthcare | Clinical reasoning for medical decision-making & genomic interpretation |
| `mantic_finance.md` | Finance | Financial market analysis & investment reasoning |
| `mantic_security.md` | Cybersecurity | Cyber threat analysis & security operations |
| `mantic_climate.md` | Climate | Climate adaptation & resilience planning |
| `mantic_legal.md` | Legal | Legal reasoning & case strategy |
| `mantic_social.md` | Social/Cultural | Social movement analysis & cultural narrative tracking |
| `mantic_command.md` | Military/Command | Strategic decision-making & operational planning |
| `mantic_system_lock.md` | System Lock | Lock-in detection and dissolution window analysis |
| `mantic_plan.md` | Planning | Universal planning reasoning for structured plan development & readiness assessment |
| `mantic_current.md` | Current Affairs | Real-time event analysis & trend monitoring |

## Usage

These configurations provide:
1. **Layer mappings** for each domain (Micro → Meso → Macro → Meta)
2. **Multi-column architectures** for complex cross-domain analysis
3. **Cross-domain coupling** patterns and conflict resolution strategies
4. **Translation guides** from framework terminology to domain language

Use these as reference when implementing domain-specific tools or when reasoning about complex problems that span multiple domains.
