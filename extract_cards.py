import json
import os
import argparse

class CardExtractor:
    def __init__(self, file_path, dbf_ids, basic_only=False):
        self.file_path = file_path
        self.dbf_ids = dbf_ids
        self.basic_only = basic_only

    def load_cards(self):
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def filter_cards_by_dbf_ids(self, cards):
        return [card for card in cards if card.get('dbfId') in self.dbf_ids]

    @staticmethod
    def trim_card_fields(cards):
        basic_keys = ["name", "cost", "attack", "health", "text", "type", "cardClass"]
        return [{k: c.get(k) for k in basic_keys if k in c} for c in cards]

    def extract(self):
        all_cards = self.load_cards()
        filtered = self.filter_cards_by_dbf_ids(all_cards)
        return self.trim_card_fields(filtered) if self.basic_only else filtered

def parse_dbf_ids(input_string):
    try:
        return [int(id_str.strip()) for id_str in input_string.split(',') if id_str.strip().isdigit()]
    except ValueError:
        raise ValueError("Invalid input: Please enter a comma-separated list of integers.")

def write_output_to_file(cards, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)
    print(f"💾 Output written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract specific Hearthstone cards from a JSON file.")
    parser.add_argument('--file', required=True, help='Path to the JSON card file')
    parser.add_argument('--ids', required=True, help='Comma-separated list of dbfIds to filter')
    parser.add_argument('--basic', action='store_true', help='Only display basic card fields')
    parser.add_argument('--output', help='Optional: path to save the output JSON')

    args = parser.parse_args()
    print("🧭 Card Extractor (Phase 1 Final + Class-based CLI)")

    try:
        dbf_ids = parse_dbf_ids(args.ids)
        extractor = CardExtractor(args.file, dbf_ids, args.basic)
        result = extractor.extract()

        print(f"\n✅ Found {len(result)} matching card(s):\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if args.output:
            write_output_to_file(result, args.output)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
