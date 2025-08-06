import unittest
from extract_cards import filter_cards_by_dbf_ids, trim_card_fields, parse_dbf_ids

# Sample card dataset for testing
sample_cards = [
    {
        "dbfId": 114340,
        "name": "Ysondre",
        "cost": 7,
        "attack": 8,
        "health": 5,
        "text": "Taunt. Deathrattle: Summon a random Dragon.",
        "type": "Minion",
        "cardClass": "WARRIOR"
    },
    {
        "dbfId": 122318,
        "name": "Cloud Serpent",
        "cost": 3,
        "attack": 3,
        "health": 3,
        "text": "Battlecry: Get a copy of another Elemental or Dragon.",
        "type": "Minion",
        "cardClass": "NEUTRAL"
    }
]

class TestExtractCards(unittest.TestCase):

    def test_parse_dbf_ids(self):
        self.assertEqual(parse_dbf_ids("114340,122318"), [114340, 122318])
        self.assertEqual(parse_dbf_ids(" 114340 "), [114340])
        self.assertEqual(parse_dbf_ids(""), [])
        self.assertEqual(parse_dbf_ids("abc,123"), [123])  # only valid integers pass

    def test_filter_cards_by_dbf_ids(self):
        result = filter_cards_by_dbf_ids(sample_cards, [114340])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], "Ysondre")

    def test_trim_card_fields(self):
        trimmed = trim_card_fields(sample_cards)
        self.assertEqual(len(trimmed), 2)
        for card in trimmed:
            self.assertSetEqual(set(card.keys()), {"name", "cost", "attack", "health", "text", "type", "cardClass"})

if __name__ == "__main__":
    unittest.main()
