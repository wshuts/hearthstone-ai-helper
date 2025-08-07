import argparse
import json
import sys

def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to JSON config file')
    args = parser.parse_args()

    if not args.config:
        parser.error("Missing required argument: --config")

    config = load_config(args.config)
    # For now, just print the loaded config and exit
    print("✅ Config loaded:", config)

if __name__ == "__main__":
    main()
