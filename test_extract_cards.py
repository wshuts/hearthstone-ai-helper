import json
import os
import subprocess

import pytest
from jsonschema import ValidationError, validate

from extract_cards import to_basic_fields
from schemas import config_schema


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


def test_extract_cards_outputs_only_basic_fields_when_flagged():
    result = subprocess.run(
        ["python", "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # Look for something that shouldn't appear in basic fields
    assert "rarity" not in result.stdout.lower()


def test_to_basic_fields_strips_non_basic():
    card = {"name": "X", "cost": 3, "attack": 2, "health": 4, "text": "t", "rarity": "Epic"}
    assert to_basic_fields(card) == {"name": "X", "cost": 3, "attack": 2, "health": 4, "text": "t"}


def test_extract_cards_writes_to_output_file(tmp_path):
    output_path = tmp_path / "test_results.json"

    # Copy or reuse a valid config, but point outputFile to our temp path
    config_path = tmp_path / "config.json"
    source_path = os.path.abspath("data/standard_cards_aug_2025.json")
    config_data = {
        "sourceFile": source_path,
        "ids": [114340, 122318],
        "basic": True,
        "outputFile": str(output_path)
    }

    config_path.write_text(json.dumps(config_data), encoding="utf-8")

    # Run CLI
    result = subprocess.run(
        ["python", "extract_cards.py", "--config", str(config_path)],
        capture_output=True,
        text=True
    )

    # Expect success
    assert result.returncode == 0
    # File should exist
    assert output_path.exists()
    # File should contain valid JSON
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(loaded, list)
    assert all(isinstance(c, dict) for c in loaded)
