import json
import os

def load_cards(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_cards_by_dbf_ids(cards, dbf_ids):
    return [card for card in cards if card.get('dbfId') in dbf_ids]

def main():
    print("🧭 Welcome to The Maiden Voyage – Card Extractor")
    file_path = input("Enter the path to your JSON card file: ").strip()

    try:
        all_cards = load_cards(file_path)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    # Sample dbfIds to filter (you can modify this list)
    target_dbf_ids = [114340, 122318]  # Example: Ysondre, Cloud Serpent

    filtered_cards = filter_cards_by_dbf_ids(all_cards, target_dbf_ids)

    print(f"\n✅ Found {len(filtered_cards)} matching cards:\n")
    print(json.dumps(filtered_cards, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
