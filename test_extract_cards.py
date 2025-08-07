import json
import os
import pytest
from jsonschema import validate, ValidationError

# Load the schema directly or from a file if preferred
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "sourceFile": {"type": "string"},
        "ids": {
            "type": "array",
            "items": {"type": "integer"}
        },
        "basic": {"type": "boolean"},
        "outputFile": {"type": "string"}
    },
    "required": ["sourceFile", "ids"]
}

# Helper to load test configs from test_data/
def load_config(filename):
    with open(os.path.join("test_data", filename)) as f:
        return json.load(f)

# -----------------------
# Pytest Test Cases
# -----------------------

def test_valid_config():
    config = load_config("valid_config.json")
    validate(instance=config, schema=schema)

def test_missing_required_field():
    config = load_config("missing_ids.json")
    with pytest.raises(ValidationError):
        validate(instance=config, schema=schema)

def test_invalid_type():
    config = load_config("invalid_ids_type.json")
    with pytest.raises(ValidationError):
        validate(instance=config, schema=schema)
