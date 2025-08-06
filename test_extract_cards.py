import unittest
from extract_cards import CardExtractor, parse_dbf_ids

# Sample data for testing
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
    },
    {
        "dbfId": 999999,
        "name": "Test Dummy",
        "cost": 1,
        "attack": 0,
        "health": 2,
        "text": "",
        "type": "Minion",
        "cardClass": "NEUTRAL"
    }
]

class TestCardExtractor(unittest.TestCase):
    def test_filter_cards_by_dbf_ids(self):
        extractor = CardExtractor(file_path="", dbf_ids=[114340, 122318])
        result = extractor.filter_cards_by_dbf_ids(sample_cards)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "Ysondre")
        self.assertEqual(result[1]['name'], "Cloud Serpent")

    def test_trim_card_fields(self):
        extractor = CardExtractor(file_path="", dbf_ids=[], basic_only=True)
        trimmed = extractor.trim_card_fields(sample_cards)
        for card in trimmed:
            self.assertSetEqual(set(card.keys()), {"name", "cost", "attack", "health", "text", "type", "cardClass"})

    def test_parse_dbf_ids(self):
        self.assertEqual(parse_dbf_ids("114340,122318"), [114340, 122318])
        self.assertEqual(parse_dbf_ids(""), [])
        self.assertEqual(parse_dbf_ids("notanid,123"), [123])

if __name__ == "__main__":
    unittest.main()
