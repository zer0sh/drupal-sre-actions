#!/usr/bin/env python3
import os
import sys
import yaml

def main():
    sync_dir = sys.argv[1]
    errors = 0
    total = 0

    for root, _, files in os.walk(sync_dir):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                total += 1
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                except Exception as e:
                    print(f"::error file={fpath}::Invalid YAML in config sync: {e}")
                    errors += 1

    print(f"Validated {total} configuration files with {errors} errors.")
    if errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
