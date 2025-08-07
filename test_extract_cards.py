import json
import os
import subprocess

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


def test_extract_cards_succeeds_with_valid_config():
    result = subprocess.run(
        ["python", "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "loaded" in result.stdout.lower()


def test_extract_cards_loads_source_file():
    result = subprocess.run(
        ["python", "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Loaded" in result.stdout  # expecting e.g., "Loaded 123 cards"


def test_extract_cards_filters_by_ids():
    result = subprocess.run(
        ["python", "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Expect exactly 2 cards printed or mentioned in stdout
    assert "2 cards" in result.stdout.lower()
