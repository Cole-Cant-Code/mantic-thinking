"""
Schema alignment tests for Mantic detection tool.

These tests ensure OpenAPI/Kimi schemas match the adapter tool definitions
and expose the single detect tool.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mantic_thinking.adapters.openai_adapter import get_openai_tools
from mantic_thinking.adapters.kimi_adapter import get_kimi_tools


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(ROOT, "mantic_thinking", "schemas")
OPENAPI_PATH = os.path.join(SCHEMAS_DIR, "openapi.json")
KIMI_PATH = os.path.join(SCHEMAS_DIR, "kimi-tools.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_public_tool_sets_match():
    """OpenAPI, Kimi, and adapters all expose the detect tool."""
    openapi_doc = _load_json(OPENAPI_PATH)
    openapi_paths = list(openapi_doc.get("paths", {}).keys())
    assert "/detect" in openapi_paths

    kimi_doc = _load_json(KIMI_PATH)
    kimi_names = {t["name"] for t in kimi_doc}
    assert "detect" in kimi_names

    openai_names = {t["function"]["name"] for t in get_openai_tools()}
    assert "detect" in openai_names

    kimi_adapter_names = {t["name"] for t in get_kimi_tools()}
    assert "detect" in kimi_adapter_names


def test_schema_parameters_match_adapters():
    """Schema parameter properties must match adapter schemas."""
    openapi_doc = _load_json(OPENAPI_PATH)
    openapi_schema = openapi_doc["paths"]["/detect"]["post"]["requestBody"]["content"]["application/json"]["schema"]

    openai_schema = get_openai_tools()[0]["function"]["parameters"]
    kimi_schema = get_kimi_tools()[0]["parameters"]

    # Required fields must match
    assert set(openapi_schema["required"]) == set(openai_schema["required"])
    assert set(kimi_schema["required"]) == set(openai_schema["required"])

    # Core properties must be present in all schemas
    core_props = {"domain_name", "layer_names", "weights", "layer_values", "mode"}
    assert core_props.issubset(set(openapi_schema["properties"].keys()))
    assert core_props.issubset(set(openai_schema["properties"].keys()))
    assert core_props.issubset(set(kimi_schema["properties"].keys()))
