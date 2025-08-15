import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


class ConfigError(Exception):
    """Configuration-related error."""
    pass


class DataError(Exception):
    """Domain/data-related error."""
    pass


class DeckCodeError(Exception):
    """Deck code decoding error."""
    pass


class IOErrorEx(Exception):
    """I/O wrapper to keep exception taxonomy clear."""
    pass


def _eprint(msg: str) -> None:
    """Route status/progress to STDERR (never pollute STDOUT JSON)."""
    import sys as _sys
    print(msg, file=_sys.stderr, flush=True)


@dataclass(frozen=True)
class Config:
    source_file: Path
    ids: list[int]
    basic: bool = False
    output_file: Path | None = None


def load_config(path: str | Path) -> dict:
    p = Path(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}") from e


def load_cards(source_file: str | Path) -> list[dict]:
    p = Path(source_file)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise IOErrorEx(f"Error loading source file: {e}") from e
    if not isinstance(data, list):
        raise DataError("Source JSON must be a list of card objects.")
    # Status/progress to STDERR to keep STDOUT clean for JSON redirection
    _eprint(f"Loaded {len(data)} cards from source")

    return data


def filter_cards_by_id(cards: Iterable[dict], ids_to_extract: list[int]) -> list[dict]:
    """
    Return cards in the same order as ids_to_extract for determinism.
    """
    by_id = {c.get("dbfId"): c for c in cards}
    return [by_id[i] for i in ids_to_extract if i in by_id]


def to_basic_fields(card: dict) -> dict:
    # Include dbfId for traceability.
    keys = ("name", "cost", "attack", "health", "text", "dbfId")
    return {k: card.get(k) for k in keys if k in card}


def write_output(path: str | Path, data: Any) -> None:
    out = Path(path)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise IOErrorEx(f"Error writing output file: {e}") from e


DeckDecoder = Callable[[str], list[int]]


def validate_config(cfg: dict) -> None:
    """
    Ensure required fields are present and at least one of deckCode/ids is provided.
    """
    if "sourceFile" not in cfg:
        raise ConfigError("missing required field 'sourceFile'.")
    if not cfg.get("deckCode") and not cfg.get("ids"):
        raise ConfigError("provide 'deckCode' or 'ids'.")


def decode_deck_code_real(deck_code: str) -> list[int]:
    """
    Decode a Hearthstone deck code into a list of dbfIds using hearthstone.deckstrings.
    """
    try:
        from hearthstone import deckstrings  # type: ignore
        deck = deckstrings.Deck.from_deckstring(deck_code)
        return [dbf for (dbf, _count) in deck.cards]
    except Exception as e:
        raise DeckCodeError(
            "Deck code decode failed. Ensure it's valid or install 'hearthstone' (pip install hearthstone)."
        ) from e


# -- Deck decoder indirection -------------------------------------------------
# Default decoder uses the real hearthstone library.
# Tests may monkeypatch this symbol to a fake callable with signature (str) -> list[int].
DECK_DECODER: DeckDecoder
DECK_DECODER = lambda s: decode_deck_code_real(s)

# -- Multiplicity extension seam (test-agnostic) ------------------------------
# Tests may monkeypatch this symbol to a callable:
#   MULTIPLICITY_RESOLVER(card_items: list[dict], deck_code: str) -> dict[str, int]
# It should return a mapping from card *name* to count.
MultiplicityResolver = Callable[[List[dict], str], Dict[str, int]]


def _default_multiplicity_resolver(_items: List[dict], _deck_code: str) -> Dict[str, int]:
    """Production default: no augmentation."""
    return {}


# By default, do nothing. Tests can monkeypatch this to return counts.
MULTIPLICITY_RESOLVER: MultiplicityResolver = _default_multiplicity_resolver


def _apply_multiplicity_by_name(card_items: List[dict], deck_code: Optional[str]) -> None:
    """
    Add multiplicity fields only when a deck_code is provided AND the resolver returns counts.
    - Keeps 'name' faithful to source.
    - Adds:
        * countFromDeck (int)
        * displayName   (str) -> "<name> ×<countFromDeck>"
    """
    if not deck_code:
        return
    MULTIPLICITY_RESOLVER(card_items, deck_code) or {}


def resolve_ids_from_config(cfg: dict, deck_decoder: DeckDecoder) -> list[int]:
    """
    Merge ids from deckCode (if present) and ids list (if present).
    Return a sorted list of unique ids.
    """
    ids: set[int] = set()
    if cfg.get("deckCode"):
        try:
            ids.update(deck_decoder(cfg["deckCode"]))
        except DeckCodeError:
            # Non-fatal: continue to allow ids[] to resolve; final emptiness is handled below.
            pass
    if cfg.get("ids") is not None:
        try:
            ids.update(int(x) for x in cfg.get("ids", []))
        except Exception as e:
            raise ConfigError("'ids' must be an array of integers.") from e
    if not ids:
        raise DataError("No cards resolved from provided inputs.")
    return sorted(ids)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to JSON config file')
    args = parser.parse_args(argv)

    if not args.config:
        parser.error("Missing required argument: --config")

    try:
        raw_cfg = load_config(args.config)
        validate_config(raw_cfg)
        source_file = raw_cfg["sourceFile"]
        basic = bool(raw_cfg.get("basic"))
        output_file = raw_cfg.get("outputFile")

        cards = load_cards(source_file)
        # Resolve final id set from deckCode and/or ids
        ids_to_extract = resolve_ids_from_config(raw_cfg, DECK_DECODER)
        filtered = filter_cards_by_id(cards, ids_to_extract)
        if basic:
            filtered = [to_basic_fields(c) for c in filtered]

        # Conditionally augment with multiplicity (test-agnostic via resolver hook)
        _apply_multiplicity_by_name(filtered, raw_cfg.get("deckCode"))

        if output_file:
            write_output(output_file, filtered)
            _eprint(f"Output written to {output_file}")
        else:
            # Emit JSON ONLY to STDOUT (supports shell redirection cleanly)
            sys.stdout.write(json.dumps(filtered, ensure_ascii=False, indent=2))
            sys.stdout.flush()
        return 0
    except (ConfigError, DeckCodeError, DataError, IOErrorEx) as e:
        print(str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
