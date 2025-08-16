import copy

import extract_cards as ec


# Characterization tests for today's SPIKE implementation of the default resolver.
# Behavior (as implemented):
# - If deck_code is falsy -> {}
# - If DECK_DECODER raises DeckCodeError -> {}
# - Otherwise: decode to dbfIds, count them, and return {name: count} for ids present in items.


def test_default_resolver_returns_empty_when_deck_code_missing():
    items = [{"dbfId": 1, "name": "Alpha"}]
    for dc in (None, ""):
        out = ec._default_multiplicity_resolver(items, dc)  # type: ignore[arg-type]
        assert out == {}


def test_default_resolver_invalid_code_returns_empty(monkeypatch):
    # Arrange: decoder that always errors like an invalid deck code
    def fake_decoder(_deck_code: str):
        raise ec.DeckCodeError("invalid code")

    monkeypatch.setattr(ec, "DECK_DECODER", fake_decoder)
    items = [{"dbfId": 1, "name": "Alpha"}]

    # Act
    out = ec._default_multiplicity_resolver(items, "NOT_A_REAL_CODE")

    # Assert
    assert out == {}


def test_default_resolver_maps_counts_by_name_for_present_ids_and_no_mutation(monkeypatch):
    # Arrange: decoder returns a multiset of dbfIds; some are not present in items
    def fake_decoder(_deck_code: str):
        # ids: 1 appears twice, 2 appears twice, 3 appears once (should be ignored if not in items)
        return [1, 1, 2, 3, 2]

    monkeypatch.setattr(ec, "DECK_DECODER", fake_decoder)

    items = [
        {"dbfId": 1, "name": "Alpha", "cost": 1},
        {"dbfId": 2, "name": "Beta", "cost": 2},
        # This entry is malformed (missing name) and should not cause issues
        {"dbfId": 3, "cost": 3},
        # This entry has a non-int dbfId and should be ignored for mapping
        {"dbfId": "4", "name": "Gamma", "cost": 4},
    ]
    snapshot = copy.deepcopy(items)

    # Act
    out = ec._default_multiplicity_resolver(items, "SOME_CODE")

    # Assert: only names present in items 1 and 2 are counted; id 3 ignored; id "4" ignored
    assert out == {"Alpha": 2, "Beta": 2}
    # Purity: the resolver must not mutate inputs
    assert items == snapshot
    assert items is not snapshot
    for a, b in zip(items, snapshot):
        assert a is not b
