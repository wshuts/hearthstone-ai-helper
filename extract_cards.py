import argparse
import json
import sys


def load_config(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)


def load_cards(source_file):
    try:
        with open(source_file, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading source file: {e}", file=sys.stderr)
        sys.exit(1)


def filter_cards_by_id(cards, ids_to_extract):
    return [card for card in cards if card.get("dbfId") in ids_to_extract]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to JSON config file')
    args = parser.parse_args()

    if not args.config:
        parser.error("Missing required argument: --config")

    config = load_config(args.config)
    source_file = config["sourceFile"]
    ids_to_extract = config.get("ids", [])

    cards = load_cards(source_file)
    filtered = filter_cards_by_id(cards, ids_to_extract)
    print(f"Loaded {len(filtered)} cards")


if __name__ == "__main__":
    main()
