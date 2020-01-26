import json
from typing import Dict


def read_json(json_path: str) -> Dict:
    """Reads JSON file."""
    with open(json_path, 'r') as infile:
        return json.load(infile)
