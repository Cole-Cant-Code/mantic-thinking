"""
Schema alignment tests for Mantic public tools.

These tests ensure OpenAPI/Kimi schemas match the adapter tool definitions
and only expose the public 14-tool surface.
"""

import json
import os
import sys

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tools
from adapters.openai_adapter import get_openai_tools
from adapters.kimi_adapter import get_kimi_tools


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(ROOT, "schemas")
OPENAPI_PATH = os.path.join(SCHEMAS_DIR, "openapi.json")
KIMI_PATH = os.path.join(SCHEMAS_DIR, "kimi-tools.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _openapi_tool_schemas(openapi_doc):
    schemas = {}
    for path, methods in openapi_doc.get("paths", {}).items():
        assert path.startswith("/detect/"), f"Unexpected OpenAPI path: {path}"
        tool_name = path[len("/detect/"):]
        schema = (
            methods["post"]["requestBody"]["content"]["application/json"]["schema"]
        )
        schemas[tool_name] = schema
    return schemas


def _openai_tool_schemas():
    return {
        tool["function"]["name"]: tool["function"]["parameters"]
        for tool in get_openai_tools()
    }


def _kimi_tool_schemas():
    return {
        tool["name"]: tool["parameters"]
        for tool in get_kimi_tools()
    }


def test_public_tool_sets_match():
    """OpenAPI, Kimi, and adapters must expose the same public 14 tools."""
    public = set(tools.__all__)

    openapi_doc = _load_json(OPENAPI_PATH)
    openapi_tools = set(_openapi_tool_schemas(openapi_doc).keys())

    openai_tools = set(_openai_tool_schemas().keys())
    kimi_tools = set(_kimi_tool_schemas().keys())

    assert openapi_tools == public
    assert openai_tools == public
    assert kimi_tools == public

    # Explicitly confirm internal tools are not exposed.
    assert "codebase_layer_conflict" not in openapi_tools
    assert "codebase_alignment_window" not in openapi_tools


def test_schema_parameters_match_adapters():
    """Schema parameter properties/required sets must match adapter schemas."""
    openapi_doc = _load_json(OPENAPI_PATH)
    openapi_schemas = _openapi_tool_schemas(openapi_doc)
    openai_schemas = _openai_tool_schemas()
    kimi_schemas = _kimi_tool_schemas()

    for tool_name in tools.__all__:
        openapi_schema = openapi_schemas[tool_name]
        openai_schema = openai_schemas[tool_name]
        kimi_schema = kimi_schemas[tool_name]

        assert set(openapi_schema["properties"].keys()) == set(openai_schema["properties"].keys())
        assert set(openapi_schema["required"]) == set(openai_schema["required"])

        assert set(kimi_schema["properties"].keys()) == set(openai_schema["properties"].keys())
        assert set(kimi_schema["required"]) == set(openai_schema["required"])
