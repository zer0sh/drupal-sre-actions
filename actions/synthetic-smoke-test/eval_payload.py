#!/usr/bin/env python3
import json
import sys

def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    expr = sys.argv[1]
    response_file = sys.argv[2]

    try:
        with open(response_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        valid = eval(expr, {}, data)
        print("OK" if valid else "FAIL")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
