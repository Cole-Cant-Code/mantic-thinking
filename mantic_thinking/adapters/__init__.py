"""
Mantic Early Warning System - Cross-Model Adapters

Provides model-specific interfaces for:
- Claude (Computer Use format)
- Kimi (Native tool format)
- Gemini (FunctionDeclaration format)
- OpenAI/Codex (Function calling format)

All adapters support 17 tools:
- 8 Friction tools (divergence detection)
- 8 Emergence tools (confluence detection)
- 1 Generic tool (caller-defined domains)
"""

from .openai_adapter import (
    get_openai_tools, 
    execute_tool as execute_openai,
    get_tools_by_type,
    get_tool_descriptions
)
from .kimi_adapter import (
    get_kimi_tools, 
    execute as execute_kimi,
    batch_execute,
    get_tool_summary,
    validate_params,
    compare_friction_emergence
)
from .claude_adapter import (
    get_claude_tools, 
    execute_tool as execute_claude,
    format_for_claude,
    get_claude_prompt_addon,
    get_summary_by_type
)
from .gemini_adapter import (
    get_gemini_tools,
    get_gemini_tools_flat,
    execute_tool as execute_gemini,
    format_for_gemini,
    get_gemini_prompt_addon,
    get_tool_by_name
)

__all__ = [
    # OpenAI/Codex
    "get_openai_tools",
    "execute_openai",
    "get_tools_by_type",
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
    "get_claude_prompt_addon",
    "get_summary_by_type",
    # Gemini
    "get_gemini_tools",
    "get_gemini_tools_flat",
    "execute_gemini",
    "format_for_gemini",
    "get_gemini_prompt_addon",
    "get_tool_by_name",
]
