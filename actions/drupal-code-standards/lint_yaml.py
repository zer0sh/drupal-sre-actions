#!/usr/bin/env python3
import glob
import sys
import yaml

def main():
    has_error = False
    valid_paths = [p for p in sys.argv[1:]]

    for p in valid_paths:
        for filepath in glob.glob(f"{p}/**/*.yml", recursive=True) + glob.glob(f"{p}/**/*.yaml", recursive=True):
            if "node_modules" in filepath or "vendor" in filepath:
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as yf:
                    yaml.safe_load(yf)
            except Exception as exc:
                print(f"::error file={filepath}::YAML syntax error: {exc}")
                has_error = True

    if has_error:
        sys.exit(1)

if __name__ == "__main__":
    main()
