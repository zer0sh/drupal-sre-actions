#!/usr/bin/env python3
import json
import sys

def main():
    summary_path = sys.argv[1]
    json_path = sys.argv[2]
    gh_output = sys.argv[3]

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    advisories = data.get("advisories", {})
    abandoned = data.get("abandoned", {})
    total_vulns = sum(len(items) for items in advisories.values())

    with open(summary_path, "a", encoding="utf-8") as f:
        if total_vulns > 0:
            f.write(f"**Alert:** Found {total_vulns} security vulnerabilities.\n\n")
            f.write("| Package | Advisory / CVE | Title | Link |\n")
            f.write("|---------|----------------|-------|------|\n")
            for pkg, items in advisories.items():
                for item in items:
                    cve = item.get("cve") or item.get("advisoryId") or "N/A"
                    title = item.get("title", "").replace("|", "-")
                    link = item.get("link", "")
                    f.write(f"| `{pkg}` | `{cve}` | {title} | [Details]({link}) |\n")
            f.write("\n")
        else:
            f.write("No known security vulnerabilities reported by Composer advisory feeds.\n\n")

        if abandoned:
            f.write(f"**Abandoned Packages ({len(abandoned)}):**\n\n")
            f.write("| Package | Suggested Replacement |\n")
            f.write("|---------|-----------------------|\n")
            for pkg, repl in abandoned.items():
                f.write(f"| `{pkg}` | `{repl or 'None'}` |\n")
            f.write("\n")

    has_vulns = "true" if total_vulns > 0 else "false"
    with open(gh_output, "a", encoding="utf-8") as out:
        out.write(f"has_vulnerabilities={has_vulns}\n")
        out.write(f"vulnerabilities_count={total_vulns}\n")

if __name__ == "__main__":
    main()
