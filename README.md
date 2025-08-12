# Hearthstone AI Helper

A Python utility for extracting and summarizing **Hearthstone** deck and card data into clean, structured **JSON** output.  
Ideal for quick lookups, strategy analysis, and automated deck documentation.

## Features
- **Deck Extraction** – Decode a deck code or pull specific card data by ID.
- **JSON Output** – Generates structured files for easy reuse in other tools.
- **Config-Driven** – Accepts a simple JSON config file with source file, IDs, and output settings.
- **Hearthstone Standard Support** – Works with Standard-format card data files.

## Basic Usage
### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run with a config file
```bash
python extract_cards.py config.json
```
Example config:
```json
{
  "sourceFile": "data/standard_cards_aug_2025.json",
  "ids": [114340, 123456],
  "basic": true,
  "outputFile": "output/cards.json"
}
```

### 3. Run with a deck code
```bash
python extract_cards.py --deck-code "AAECA..."
```

## Output
- **Basic Info** – Name, cost, attack, health, text
- **Full Entry** – Complete card data from the source file
- JSON files are saved to the `output/` directory

## Requirements
- Python 3.8+
