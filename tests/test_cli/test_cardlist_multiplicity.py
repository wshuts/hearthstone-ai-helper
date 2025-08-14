import json
import sys
import subprocess
from pathlib import Path

import pytest


# ----------------------------
# Test helpers (minimal, local)
# ----------------------------

def _write_min_source(tmp_path: Path) -> Path:
    """
    Create a minimal source file with EXACTLY the two cards that our fake deck will reference.
    This avoids zero-count/noise cases during RED.
    """
    cards = [
        {
            "dbfId": 1,
            "name": "Alpha",
            "cost": 1,
            "attack": 1,
            "health": 1,
            "type": "MINION",
            "rarity": "COMMON",
            "text": "Just a test card.",
        },
        {
            "dbfId": 2,
            "name": "Beta",
            "cost": 2,
            "attack": 2,
            "health": 2,
            "type": "MINION",
            "rarity": "RARE",
            "text": "Also a test card.",
        },
    ]
    src = tmp_path / "cards_min.json"
    src.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    return src


def _run_cli_with_config(cfg_path: Path) -> subprocess.CompletedProcess:
    """
    Invoke extract_cards.py with the provided config.
    NOTE: Repo root is two levels up from this test file.
    """
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "extract_cards.py"
    assert script.exists(), f"extract_cards.py not found at {script}"

    return subprocess.run(
        [sys.executable, str(script), "--config", str(cfg_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def _read_output_list(out_path: Path):
    """
    Current extractor emits a TOP-LEVEL LIST of card dicts (not a dict with 'cardList').
    """
    assert out_path.exists(), f"Expected output file at {out_path} was not created."
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert isinstance(data, list), "Extractor output must be a top-level list."
    return data


def _expect_display_name(name: str, count: int) -> str:
    return f"{name} ×{count}"


# ----------------------------------------------------
# RED Test 1: Behavior with deckCode (format + values)
# ----------------------------------------------------

def test_multiplicity_behavior_with_deckcode(tmp_path: Path):
    """
    Given a deckCode, each output entry must include:
      - countFromDeck (int) with the expected value per card
      - displayName string exactly "<name> ×<countFromDeck>"
      - name remains faithful to source (no embedded count)

    Minimal deck composition we assert against:
      Alpha ×2, Beta ×1

    Current implementation is expected to FAIL (RED) because multiplicity isn't implemented yet.
    """
    src = _write_min_source(tmp_path)
    out_file = tmp_path / "out_behavior.json"

    # ids match the minimal source; deckCode is a placeholder for RED
    cfg = {
        "sourceFile": str(src),
        "ids": [1, 2],
        "basic": True,
        "deckCode": "TEST-DECKCODE-ALPHAx2-BETAx1",
        "outputFile": str(out_file),
    }
    cfg_path = tmp_path / "config_behavior.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)
    assert proc.returncode == 0, (
        "CLI crashed unexpectedly; RED should fail on missing fields/format, not process errors.\n"
        f"STDERR:\n{proc.stderr}"
    )

    cards = _read_output_list(out_file)
    assert cards, "Expected non-empty output list."

    # Expected counts by name for the fake deck
    expected_counts = {"Alpha": 2, "Beta": 1}

    # Index by name for easy assertions
    by_name = {c.get("name"): c for c in cards}
    for name, expected_count in expected_counts.items():
        assert name in by_name, f"Expected card '{name}' missing from output."
        entry = by_name[name]

        # Name remains faithful to source
        assert entry.get("name") == name, "Name must remain unchanged (no multiplicity baked in)."

        # New fields required when deckCode is present
        assert "countFromDeck" in entry, "Missing 'countFromDeck' when deckCode is present."
        assert isinstance(entry["countFromDeck"], int), "'countFromDeck' must be an int."
        assert entry["countFromDeck"] == expected_count, (
            f"countFromDeck for {name} should be {expected_count}."
        )

        assert "displayName" in entry, "Missing 'displayName' when deckCode is present."
        assert isinstance(entry["displayName"], str), "'displayName' must be a string."
        # Exact formatting with Unicode multiplication sign and single space before it
        assert entry["displayName"] == _expect_display_name(name, expected_count), (
            f"displayName must be exactly '{_expect_display_name(name, expected_count)}'."
        )

        # Extra guardrail: prefix/suffix parse
        prefix = f"{name} ×"
        assert entry["displayName"].startswith(prefix), "displayName must start with '<name> ×'."
        try:
            int(entry["displayName"].split("×", 1)[1].strip())
        except (ValueError, IndexError):
            pytest.fail("displayName must end with a valid integer count.")


# ------------------------------------------------------------
# RED Test 2: Triggering (with deckCode vs without deckCode)
# ------------------------------------------------------------

def test_multiplicity_triggers_only_with_deckcode(tmp_path: Path):
    """
    Verify the feature gate:
      - WITHOUT deckCode: no 'countFromDeck' / 'displayName' on any entry
      - WITH    deckCode: fields are present and correctly formatted

    Current implementation is expected to FAIL (RED) on the WITH deckCode case.
    """
    src = _write_min_source(tmp_path)

    # --- Case A: WITHOUT deckCode ---
    out_no = tmp_path / "out_no_deckcode.json"
    cfg_no = {
        "sourceFile": str(src),
        "ids": [1, 2],
        "basic": False,
        "outputFile": str(out_no),
    }
    (tmp_path / "config_no_deckcode.json").write_text(
        json.dumps(cfg_no, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    proc_no = _run_cli_with_config(tmp_path / "config_no_deckcode.json")
    assert proc_no.returncode == 0, f"CLI failed unexpectedly.\nSTDERR:\n{proc_no.stderr}"
    cards_no = _read_output_list(out_no)
    assert cards_no, "Expected non-empty list without deckCode."
    for e in cards_no:
        assert "name" in e and isinstance(e["name"], str), "Entries must include 'name'."
        assert "countFromDeck" not in e, "countFromDeck must NOT appear without deckCode."
        assert "displayName" not in e, "displayName must NOT appear without deckCode."

    # --- Case B: WITH deckCode ---
    out_yes = tmp_path / "out_with_deckcode.json"
    cfg_yes = {
        "sourceFile": str(src),
        "ids": [1, 2],
        "basic": True,
        "deckCode": "TEST-DECKCODE-ALPHAx2-BETAx1",
        "outputFile": str(out_yes),
    }
    (tmp_path / "config_with_deckcode.json").write_text(
        json.dumps(cfg_yes, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    proc_yes = _run_cli_with_config(tmp_path / "config_with_deckcode.json")
    assert proc_yes.returncode == 0, (
        "CLI crashed unexpectedly; RED should fail on missing fields, not process errors.\n"
        f"STDERR:\n{proc_yes.stderr}"
    )
    cards_yes = _read_output_list(out_yes)
    assert cards_yes, "Expected non-empty list with deckCode."
    for e in cards_yes:
        assert "name" in e and isinstance(e["name"], str), "Entries must include 'name'."
        assert "countFromDeck" in e, "With deckCode, 'countFromDeck' must be present."
        assert "displayName" in e, "With deckCode, 'displayName' must be present."
        assert isinstance(e["displayName"], str), "'displayName' must be a string."
        assert e["displayName"].startswith(f"{e['name']} ×"), "displayName must start with '<name> ×'."
        # Suffix parses to int
        try:
            int(e["displayName"].split("×", 1)[1].strip())
        except (ValueError, IndexError):
            pytest.fail("displayName must end with a valid integer count.")
