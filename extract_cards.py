import argparse
import json
import os
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


def to_basic_fields(card):
    return {
        k: card.get(k)
        for k in ("name", "cost", "attack", "health", "text")
        if k in card
    }


def write_output(path, data):
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to JSON config file')
    args = parser.parse_args()

    if not args.config:
        parser.error("Missing required argument: --config")

    config = load_config(args.config)
    source_file = config["sourceFile"]
    ids_to_extract = config.get("ids", [])
    basic = bool(config.get("basic"))
    output_file = config.get("outputFile")

    cards = load_cards(source_file)
    filtered = filter_cards_by_id(cards, ids_to_extract)
    if basic:
        filtered = [to_basic_fields(c) for c in filtered]

    if output_file:
        write_output(output_file, filtered)
    print(f"Loaded {len(filtered)} cards")
    print(json.dumps(filtered, indent=2))


if __name__ == "__main__":
    main()
