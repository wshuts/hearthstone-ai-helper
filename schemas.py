# schemas.py
config_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "sourceFile": {"type": "string"},
        "deckCode": { "type": "string", "minLength": 5 },
        "ids": {
            "type": "array",
            "items": {"type": "integer"}
        },
        "basic": {"type": "boolean"},
        "outputFile": {"type": "string"}
    },
    "required": ["sourceFile"],
    "anyOf": [
        { "required": ["deckCode"] },
        { "required": ["ids"] }
    ]
}
