import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import extract_cards as ec


# ----------------------------
# Local helpers (tests only)
# ----------------------------
def _write_cards(tmp_path: Path) -> Path:
    """
    Minimal source list matching our extractor's expectations.
    """
    cards = [
        {"dbfId": 1, "name": "Alpha", "cost": 1, "attack": 1, "health": 1, "text": "A."},
        {"dbfId": 2, "name": "Bravo", "cost": 2, "attack": 2, "health": 2, "text": "B."},
        {"dbfId": 3, "name": "Charlie", "cost": 3, "attack": 3, "health": 3, "text": "C."},
    ]
    p = tmp_path / "cards.json"
    p.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
    return p


def _write_config(tmp_path: Path, *, source: Path, ids=None, basic=False, output_file: Path | None = None) -> Path:
    """
    Compose a config that uses the ids path (kept simple for this dev cycle).
    """
    cfg = {"sourceFile": str(source)}
    if ids is not None:
        cfg["ids"] = list(ids)
    if basic:
        cfg["basic"] = True
    if output_file is not None:
        cfg["outputFile"] = str(output_file)
    cp = tmp_path / "config.json"
    cp.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return cp


def _run_cli_with_config(cfg_path: Path, capsys) -> SimpleNamespace:
    """
    Mirror existing CLI test style in this project:
    pass argv directly into main(argv) and capture with capsys.
    """
    rc = ec.main(["--config", str(cfg_path)])
    cap = capsys.readouterr()
    return SimpleNamespace(returncode=rc, stdout=cap.out, stderr=cap.err)


def _parse_json_or_fail(text: str):
    """
    Helper: assert stdout is *pure* JSON (no status lines mixed in).
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"stdout should be pure JSON, but failed to decode: {e}\n--- STDOUT START ---\n{text}\n--- STDOUT END ---"
        ) from e


# ----------------------------
# Tests (RED phase)
# ----------------------------
def test_stdout_json_stderr_status_when_redirected(tmp_path, capsys):
    """
    When outputFile is omitted:
      - stdout must contain only valid JSON
      - stderr contains status (e.g., 'Loaded N cards')
    """
    source = _write_cards(tmp_path)
    cfg = _write_config(tmp_path, source=source, ids=[1, 3], basic=True, output_file=None)

    res = _run_cli_with_config(cfg, capsys)

    # Program should succeed
    assert res.returncode == 0, res.stderr

    # stdout is valid JSON only (no status noise)
    payload = _parse_json_or_fail(res.stdout)
    assert isinstance(payload, list)
    # sanity: ensure selected names are present
    names = {c.get("name") for c in payload}
    assert {"Alpha", "Charlie"} <= names

    # stderr should include a status line indicating cards were loaded/processed
    assert "Loaded" in res.stderr, "Expected a status line in stderr"


def test_file_write_keeps_stdout_clean(tmp_path, capsys):
    """
    When outputFile is provided:
      - File exists and contains valid JSON
      - stdout is empty (JSON is not printed to console)
      - stderr contains success/status line ('Output written to ...')
    """
    source = _write_cards(tmp_path)
    out_file = tmp_path / "out.json"
    cfg = _write_config(tmp_path, source=source, ids=[2], basic=False, output_file=out_file)

    res = _run_cli_with_config(cfg, capsys)

    # Program should succeed
    assert res.returncode == 0, res.stderr

    # stdout should be empty when writing to file
    assert res.stdout.strip() == ""

    # File should parse as JSON
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data and data[0].get("name") == "Bravo"

    # stderr should mention success
    assert "Output written to" in res.stderr, "Expected a success line in stderr"


def test_no_status_in_stdout_even_when_tty_false(tmp_path, capsys, monkeypatch):
    """
    Even if stdout.isatty() is False, status should remain on stderr (never stdout).
    """
    source = _write_cards(tmp_path)
    cfg = _write_config(tmp_path, source=source, ids=[1], basic=True, output_file=None)

    # Force stdout to behave like a non-tty stream.
    class _FakeStdout:
        def __init__(self, wrapped):
            self._w = wrapped
        def write(self, s):
            return self._w.write(s)
        def flush(self):
            return self._w.flush()
        def isatty(self):
            return False

    fake_stdout = _FakeStdout(sys.stdout)
    monkeypatch.setattr(sys, "stdout", fake_stdout, raising=False)

    res = _run_cli_with_config(cfg, capsys)

    # Program should succeed
    assert res.returncode == 0, res.stderr

    # stdout must be *pure* JSON
    _parse_json_or_fail(res.stdout)

    # No status leakage into stdout
    assert "Loaded" not in res.stdout
    assert "Output written to" not in res.stdout

    # Status must be in stderr
    assert "Loaded" in res.stderr

#
# Notes:
# - These tests define the acceptance criteria for clean stdout JSON and stderr-only status.
# - They are expected to FAIL against the current implementation (status currently printed to stdout).
# - Next step in TDD: modify extract_cards.py to route status to stderr and print JSON only to stdout.
#
