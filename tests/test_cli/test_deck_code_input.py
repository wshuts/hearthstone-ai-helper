import json
import subprocess
import sys
from pathlib import Path

"""
RED PHASE TESTS
---------------
These tests define the intended behavior for deckCode + ids dual support.
They are self-contained: they write their own temp datasets and configs.

Expected (now): These will FAIL against the current implementation,
which ignores 'deckCode' and does not error when neither field is present.
"""


def _write_cards(tmp_path: Path):
    # Minimal list-based dataset (matches current extract_cards expectation)
    cards = [
        {"dbfId": 1, "name": "Alpha", "cost": 1, "type": "SPELL"},
        {"dbfId": 2, "name": "Bravo", "cost": 2, "type": "MINION", "attack": 2, "health": 2},
        {"dbfId": 3, "name": "Charlie", "cost": 3, "type": "MINION", "attack": 3, "health": 3},
        {"dbfId": 4, "name": "Delta", "cost": 4, "type": "SPELL"},
    ]
    cards_path = tmp_path / "cards.json"
    cards_path.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    return cards_path


def _run_cli_with_config(cfg_path: Path):
    return subprocess.run(
        [sys.executable, "extract_cards.py", "--config", str(cfg_path)],
        capture_output=True,
        text=True
    )


def test_deck_code_only_success(tmp_path):
    """
    New behavior: deckCode-only configs should succeed by decoding to dbfIds.
    Expect output to include the decoded cards (e.g., dbfIds [1, 3] -> Alpha, Charlie).
    """
    cards_path = _write_cards(tmp_path)

    # deckCode is a placeholder; GREEN phase will implement decoding.
    cfg = {
        "sourceFile": str(cards_path),
        "deckCode": "AAECA-PLACEHOLDER",
        # no 'ids' -> relies entirely on deckCode decode
        "basic": False
    }
    cfg_path = tmp_path / "cfg_deckcode_only.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)

    # GREEN behavior expectation:
    # - returncode == 0
    # - stdout JSON contains Alpha and Charlie
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "Alpha" in out and "Charlie" in out


def test_both_union_and_dedupe(tmp_path):
    """
    New behavior: deckCode + ids are merged (union, deduped).
    Example: deckCode -> [2,3], ids -> [3,4] => final {2,3,4}.
    Expect Bravo (2), Charlie (3), Delta (4) in output.
    """
    cards_path = _write_cards(tmp_path)
    cfg = {
        "sourceFile": str(cards_path),
        "deckCode": "AAECA-PLACEHOLDER",
        "ids": [3, 4],
        "basic": False
    }
    cfg_path = tmp_path / "cfg_both_union.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)

    # GREEN expectation:
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "Bravo" in out and "Charlie" in out and "Delta" in out


def test_neither_fields_errors(tmp_path):
    """
    New behavior: if neither deckCode nor ids are provided, exit with error.
    """
    cards_path = _write_cards(tmp_path)
    cfg = {
        "sourceFile": str(cards_path),
        # no deckCode, no ids
        "basic": True
    }
    cfg_path = tmp_path / "cfg_neither.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)

    # GREEN expectation:
    assert proc.returncode != 0
    assert "provide 'deckCode' or 'ids'" in (proc.stderr or proc.stdout)


def test_bad_deck_code_errors(tmp_path):
    """
    New behavior: invalid deckCode should produce a friendly error.
    """
    cards_path = _write_cards(tmp_path)
    cfg = {
        "sourceFile": str(cards_path),
        "deckCode": "INVALID_CODE",
        "basic": False
    }
    cfg_path = tmp_path / "cfg_bad_code.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)

    # GREEN expectation:
    assert proc.returncode != 0
    # Message can appear on stderr or stdout depending on implementation
    combined = f"{proc.stdout}\n{proc.stderr}"
    assert "Deck code decode failed" in combined


def test_empty_union_errors(tmp_path):
    """
    New behavior: if deckCode decodes to empty AND ids is empty -> error.
    Since we cannot patch subprocess here, we simulate by providing ids=[] and
    relying on deck decode to be empty in GREEN; until then this will still be red.
    """
    cards_path = _write_cards(tmp_path)
    cfg = {
        "sourceFile": str(cards_path),
        "deckCode": "AAECA-DECODES-TO-EMPTY",
        "ids": [],
        "basic": True
    }
    cfg_path = tmp_path / "cfg_empty_union.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")

    proc = _run_cli_with_config(cfg_path)

    # GREEN expectation:
    assert proc.returncode != 0
    combined = f"{proc.stdout}\n{proc.stderr}"
    assert "No cards resolved from provided inputs" in combined
