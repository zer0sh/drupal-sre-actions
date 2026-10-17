#!/usr/bin/env python3
import json
import sys

def main():
    summary_file = sys.argv[1]

    try:
        with open("composer.lock.old", "r", encoding="utf-8") as f:
            old_data = json.load(f)
        with open("composer.lock", "r", encoding="utf-8") as f:
            new_data = json.load(f)

        old_pkgs = {p["name"]: p["version"] for p in old_data.get("packages", [])}
        new_pkgs = {p["name"]: p["version"] for p in new_data.get("packages", [])}

        updated = []
        for name, new_ver in sorted(new_pkgs.items()):
            old_ver = old_pkgs.get(name, "new")
            if old_ver != new_ver:
                updated.append(f"| `{name}` | `{old_ver}` | `{new_ver}` |")

        with open(summary_file, "a", encoding="utf-8") as out:
            if updated:
                out.write("\n".join(updated) + "\n")
            else:
                out.write("| No package version changes detected | - | - |\n")
    except Exception as e:
        with open(summary_file, "a", encoding="utf-8") as out:
            out.write(f"| Error parsing lockfile | {e} | - |\n")

if __name__ == "__main__":
    main()
