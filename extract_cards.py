import json
import os

def load_cards(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_cards_by_dbf_ids(cards, dbf_ids):
    return [card for card in cards if card.get('dbfId') in dbf_ids]

def parse_dbf_ids(input_string):
    try:
        return [int(id_str.strip()) for id_str in input_string.split(',') if id_str.strip().isdigit()]
    except ValueError:
        raise ValueError("Invalid input: Please enter a comma-separated list of integers.")

def main():
    print("🧭 Welcome to The Maiden Voyage – Card Extractor (v2)")
    file_path = input("Enter the path to your JSON card file: ").strip()

    try:
        all_cards = load_cards(file_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    dbf_input = input("Enter dbfIds to filter (comma-separated): ").strip()
    try:
        target_dbf_ids = parse_dbf_ids(dbf_input)
    except ValueError as e:
        print(f"❌ {e}")
        return

    filtered_cards = filter_cards_by_dbf_ids(all_cards, target_dbf_ids)

    print(f"\n✅ Found {len(filtered_cards)} matching card(s):\n")
    print(json.dumps(filtered_cards, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
