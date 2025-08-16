import copy
import pytest
import extract_cards as ec


@pytest.mark.parametrize(
    "decoded_ids, items, expected",
    [
        # No decoded ids → no augmentation
        ([], [{"dbfId": 1, "name": "Alpha"}, {"dbfId": 2, "name": "Beta"}], {}),
        # Single present id
        ([1], [{"dbfId": 1, "name": "Alpha"}, {"dbfId": 2, "name": "Beta"}], {"Alpha": 1}),
        # Multiset with two present ids
        ([1, 1, 2], [{"dbfId": 1, "name": "Alpha"}, {"dbfId": 2, "name": "Beta"}], {"Alpha": 2, "Beta": 1}),
        # Id not present in items should be ignored
        ([42], [{"dbfId": 1, "name": "Alpha"}, {"dbfId": 2, "name": "Beta"}], {}),
        # Mixed: present + absent + malformed entry in items (ignored)
        (
            [1, 2, 2, 3],
            [
                {"dbfId": 1, "name": "Alpha"},
                {"dbfId": 2, "name": "Beta"},
                {"dbfId": 3},  # missing name → ignored
                {"dbfId": "4", "name": "Gamma"},  # non-int dbfId → ignored
            ],
            {"Alpha": 1, "Beta": 2},
        ),
    ],
)
def test_default_resolver_table_counts_by_name(monkeypatch, decoded_ids, items, expected):
    """
    Parametric table: for a variety of decoded dbfId lists and item inventories, the
    SPIKE default resolver must return counts mapped by *name* for ids present in items,
    ignoring unknown/malformed entries. Inputs must not be mutated.
    """
    snapshot = copy.deepcopy(items)

    # Fake decoder returns the parametric multiset of ids
    def fake_decoder(_deck_code: str):
        return list(decoded_ids)

    monkeypatch.setattr(ec, "DECK_DECODER", fake_decoder)

    out = ec._default_multiplicity_resolver(items, "ANY_CODE")

    assert out == expected

    # Purity: no mutation of inputs; also ensure no aliasing
    assert items == snapshot
    assert items is not snapshot
    for a, b in zip(items, snapshot):
        assert a is not b
