"""
Mantic Thinking - Cross-Model Adapters

One detection tool per adapter. The LLM defines layer names, weights,
and values. The 16 built-in domains are available as presets (data).

Provides model-specific interfaces for:
- OpenAI/Codex (Function calling format)
- Claude (Tool-use format)
- Kimi (Native tool format)
- Gemini (FunctionDeclaration format)
"""

from .openai_adapter import (
    get_openai_tools,
    execute_tool as execute_openai,
    get_presets,
    get_tool_descriptions,
)
from .kimi_adapter import (
    get_kimi_tools,
    execute as execute_kimi,
    batch_execute,
    get_tool_summary,
    validate_params,
    compare_friction_emergence,
)
from .claude_adapter import (
    get_claude_tools,
    execute_tool as execute_claude,
    format_for_claude,
)
from .gemini_adapter import (
    get_gemini_tools,
    get_gemini_tools_flat,
    execute_tool as execute_gemini,
    format_for_gemini,
    get_gemini_prompt_addon,
    get_tool_by_name,
)

__all__ = [
    # OpenAI/Codex
    "get_openai_tools",
    "execute_openai",
    "get_presets",
    "get_tool_descriptions",
    # Kimi
    "get_kimi_tools",
    "execute_kimi",
    "batch_execute",
    "get_tool_summary",
    "validate_params",
    "compare_friction_emergence",
    # Claude
    "get_claude_tools",
    "execute_claude",
    "format_for_claude",
    # Gemini
    "get_gemini_tools",
    "get_gemini_tools_flat",
    "execute_gemini",
    "format_for_gemini",
    "get_gemini_prompt_addon",
    "get_tool_by_name",
]
