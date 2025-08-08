import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

from extract_cards import to_basic_fields
from schemas import config_schema


# ✅ Reusable loader
def load_config(filename):
    path = Path("test_data") / filename
    return json.loads(path.read_text(encoding="utf-8"))


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
        [sys.executable, "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Loaded" in result.stdout  # expecting e.g., "Loaded 123 cards"


def test_extract_cards_filters_by_ids():
    result = subprocess.run(
        [sys.executable, "extract_cards.py", "--config", "test_data/valid_config.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Expect exactly 2 cards printed or mentioned in stdout
    assert "2 cards" in result.stdout.lower()


def test_extract_cards_outputs_only_basic_fields_when_flagged():
    result = subprocess.run(
        [sys.executable, "extract_cards.py", "--config", "test_data/valid_config.json"],
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
    # Arrange a temp config that includes outputFile
    source_path = Path("data/standard_cards_aug_2025.json").resolve()
    output_path = tmp_path / "test_results.json"
    config_data = {
        "sourceFile": str(source_path),
        "ids": [114340, 122318],
        "basic": True,
        "outputFile": str(output_path)
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config_data, ensure_ascii=False), encoding="utf-8")

    # Act: run the CLI with --config pointing to our temp config
    result = subprocess.run(
        [sys.executable, "extract_cards.py", "--config", str(config_path)],
        capture_output=True,
        text=True
    )

    # Assert: command succeeded
    assert result.returncode == 0
    # When writing to a file, stdout should be silent
    assert result.stdout.strip() == ""
    # File exists and is valid JSON list of dicts
    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(loaded, list)
    assert all(isinstance(c, dict) for c in loaded)
