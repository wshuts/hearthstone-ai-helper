from extract_cards import to_basic_fields


def test_to_basic_fields_strips_non_basic():
    card = {"name": "X", "cost": 3, "attack": 2, "health": 4, "text": "t", "rarity": "Epic"}
    # Expect only the basic fields (no rarity, etc.)
    assert to_basic_fields(card) == {"name": "X", "cost": 3, "attack": 2, "health": 4, "text": "t"}
