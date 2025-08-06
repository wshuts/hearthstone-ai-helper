import json
import os

def load_cards(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_dbf_ids(input_string):
    try:
        return [int(id_str.strip()) for id_str in input_string.split(',') if id_str.strip().isdigit()]
    except ValueError:
        raise ValueError("Invalid input: Please enter a comma-separated list of integers.")

def filter_cards_by_dbf_ids(cards, dbf_ids):
    return [card for card in cards if card.get('dbfId') in dbf_ids]

def trim_card_fields(cards):
    basic_keys = ["name", "cost", "attack", "health", "text", "type", "cardClass"]
    return [{k: c.get(k) for k in basic_keys if k in c} for c in cards]

def extract_cards(file_path, dbf_ids, basic_only=False):
    all_cards = load_cards(file_path)
    filtered = filter_cards_by_dbf_ids(all_cards, dbf_ids)
    return trim_card_fields(filtered) if basic_only else filtered

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract specific Hearthstone cards from a JSON file.")
    parser.add_argument('--file', required=False, help='Path to the JSON card file')
    parser.add_argument('--ids', required=False, help='Comma-separated list of dbfIds to filter')
    parser.add_argument('--basic', action='store_true', help='Only display basic card fields')
    args = parser.parse_args()

    print("🧭 Welcome to The Maiden Voyage – Card Extractor (Refactored for Testing)")

    if not args.file:
        file_path = input("Enter the path to your JSON card file: ").strip()
    else:
        file_path = args.file

    if not args.ids:
        dbf_input = input("Enter dbfIds to filter (comma-separated): ").strip()
    else:
        dbf_input = args.ids

    try:
        target_dbf_ids = parse_dbf_ids(dbf_input)
        result = extract_cards(file_path, target_dbf_ids, args.basic)
        print(f"\n✅ Found {len(result)} matching card(s):\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
