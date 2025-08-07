import json
import os
import pytest
from jsonschema import validate, ValidationError
from schemas import config_schema  # ✅ Now imported

# ✅ Reusable loader
def load_config(filename):
    with open(os.path.join("test_data", filename)) as f:
        return json.load(f)

def test_valid_config():
    config = load_config("valid_config.json")
    validate(instance=config, schema=config_schema)

def test_missing_required_field():
    config = load_config("missing_ids.json")
    with pytest.raises(ValidationError):
        validate(instance=config, schema=config_schema)

def test_invalid_type():
    config = load_config("invalid_ids_type.json")
    with pytest.raises(ValidationError):
        validate(instance=config, schema=config_schema)
