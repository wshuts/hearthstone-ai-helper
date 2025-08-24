from __future__ import annotations

from typing import Callable, Dict, Optional

# Optional dependency (PEP 8: imports at top; safe if the lib isn't installed).
try:
    from hearthstone import deckstrings as _deckstrings  # type: ignore
except ImportError:  # pragma: no cover
    _deckstrings: Optional[object] = None

# Public seam type: tests can import and inject fakes.
DecodeDeck = Callable[[str], Dict[int, int]]  # dbfId -> count


def default_decode_deck(deck_code: str) -> Dict[int, int]:
    """
    Default production decoder using the 'hearthstone' library.

    Returns a mapping of dbfId -> count. Errors collapse to a single actionable
    message to keep tests stable across environments.
    """
    # Basic validation early (consistent, actionable message).
    if not deck_code or not isinstance(deck_code, str):
        raise ValueError(
            "Deck code decode failed. Ensure it's valid or install 'hearthstone' (pip install hearthstone)."
        )

    # Guard: only fail when the default is actually used and the lib is unavailable.
    if _deckstrings is None:
        raise RuntimeError(
            "Deck code decode failed. Ensure it's valid or install 'hearthstone' (pip install hearthstone)."
        )

    try:
        deck = _deckstrings.Deck.from_deckstring(deck_code)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        # Any parse/validation error should map to the same actionable message.
        raise ValueError(
            "Deck code decode failed. Ensure it's valid or install 'hearthstone' (pip install hearthstone)."
        )

    # deck.cards is typically a list of (dbfId: int, count: int)
    counts: Dict[int, int] = {}
    for dbf_id, count in getattr(deck, "cards", []) or []:
        try:
            c = int(count)
        except (TypeError, ValueError):
            c = 1
        counts[dbf_id] = counts.get(dbf_id, 0) + c

    return counts


__all__ = ["DecodeDeck", "default_decode_deck"]
