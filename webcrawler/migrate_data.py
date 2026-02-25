#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data migration utility to convert old crawled_data.json format to new format.

Old format: [["name", "title"], ["name2", "title2"], ...]
New format: {"name": {"name": "name", "title": "title", ...}, ...}
"""

import json
import os
import sys
from datetime import datetime


def migrate_file(input_file: str, output_file: str | None = None) -> None:
    """Convert old data format to new format."""
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)

    if output_file is None:
        output_file = input_file

    # Load existing data
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)

    # Check if already in new format
    if isinstance(data, dict) and data and "first_crawled" in next(iter(data.values())):
        print(f"File '{input_file}' is already in new format. No migration needed.")
        return

    # Convert old format to new
    if isinstance(data, list):
        print(f"Converting {len(data)} entries from old format...")
        now = datetime.now().isoformat()
        new_data = {}

        for item in data:
            if isinstance(item, list) and len(item) >= 2:
                name = item[0]
                title = item[1]
                new_data[name] = {
                    "name": name,
                    "title": title,
                    "first_crawled": now,
                    "last_crawled": now,
                }

        # Save converted data
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)

        print(f"Successfully migrated {len(new_data)} entries")
        print(f"Saved to: {output_file}")
    else:
        print("Unknown data format. Cannot migrate.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_data.py <input_file> [output_file]")
        print("\nExample:")
        print("  python migrate_data.py crawled_data.json")
        print("  python migrate_data.py old_data.json new_data.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    migrate_file(input_file, output_file)
