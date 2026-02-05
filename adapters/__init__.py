"""
Mantic Early Warning System - Cross-Model Adapters

Provides model-specific interfaces for:
- Claude (Computer Use format)
- Kimi (Native tool format)
- OpenAI/Codex (Function calling format)

All adapters support 14 tools:
- 7 Friction tools (divergence detection)
- 7 Emergence tools (confluence detection)
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
]
