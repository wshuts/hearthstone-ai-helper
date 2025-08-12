# Hearthstone AI Helper

A small CLI that extracts deck/card data from a local Hearthstone JSON file and outputs clean JSON.

## Features
- **Deck Extraction** – Pull specific card data by ID or list of IDs.
- **JSON Output** – Generates structured files for easy reuse in other tools.
- **Config-Driven** – Accepts a simple JSON config file with source file, IDs, and options.
- **Works with your source file** – Point it at any compatible Hearthstone card JSON (Standard or full set).

## Basic Usage
### 1. Install dependencies
~~~bash
pip install -r requirements.txt
~~~

### 2. Run with a config file
~~~bash
python extract_cards.py --config config.json
~~~
Example `config.json`:
~~~json
{
  "sourceFile": "data/standard_cards_aug_2025.json",
  "ids": [114340, 123456],
  "basic": true,
  "outputFile": "output/cards.json"
}
~~~

### 3. Run with a deck code (via config file)
~~~bash
python extract_cards.py --config config.deckcode.json
~~~
Example `config.deckcode.json`:
~~~json
{
  "sourceFile": "data/standard_cards_aug_2025.json",
  "deckCode": "AAECA...",
  "outputFile": "output/decklist.json"
}
~~~
> **Note:** Requires the `hearthstone` Python library for deck code decoding.

## Output
- If `"outputFile"` is provided, results are written to that path.
- If `"outputFile"` is omitted, results are written to **stdout** (can be piped or redirected).

Example (redirect stdout to a file):
~~~bash
python extract_cards.py --config config.json > output/cards.json
~~~

- **Basic Info** – Name, cost, attack, health, text
- **Full Entry** – Complete card data from the source file

## Requirements
- Tested on Python 3.13.5
- Standard Hearthstone card JSON file (not included)
- `hearthstone` Python library for deck code decoding

## License
MIT License
