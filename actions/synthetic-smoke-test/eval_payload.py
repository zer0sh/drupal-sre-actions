#!/usr/bin/env python3
import json
import sys

def evaluate(expr, data):
    expr = expr.strip()
    try:
        return bool(eval(expr, {"__builtins__": {}}, data))
    except Exception:
        pass

    if "==" in expr:
        key, expected = [x.strip() for x in expr.split("==", 1)]
        val = data.get(key)
        expected_clean = expected.strip("'\"")
        return str(val).strip().lower() == expected_clean.lower()
    elif "!=" in expr:
        key, expected = [x.strip() for x in expr.split("!=", 1)]
        val = data.get(key)
        expected_clean = expected.strip("'\"")
        return str(val).strip().lower() != expected_clean.lower()

    if expr in data:
        return bool(data[expr])

    raise ValueError(f"Unable to evaluate condition: '{expr}' against payload")

def main():
    if len(sys.argv) < 3:
        sys.exit(0)

    expr = sys.argv[1]
    response_file = sys.argv[2]

    try:
        with open(response_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        valid = evaluate(expr, data)
        print("OK" if valid else "FAIL")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()

