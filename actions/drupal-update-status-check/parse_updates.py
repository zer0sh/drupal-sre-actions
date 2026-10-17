#!/usr/bin/env python3
import json
import sys

def main():
    summary_file = sys.argv[1]
    outdated_file = sys.argv[2]
    pending_db_count = int(sys.argv[3])
    gh_output = sys.argv[4]

    try:
        with open(outdated_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"installed": []}

    installed = data.get("installed", [])
    drupal_pkgs = [p for p in installed if p.get("name", "").startswith("drupal/")]
    other_pkgs = [p for p in installed if not p.get("name", "").startswith("drupal/")]

    semver_breaks = []
    regular_updates = []

    for p in drupal_pkgs:
        name = p.get("name")
        curr = p.get("version", "N/A")
        latest = p.get("latest", "N/A")
        status = p.get("latest-status", "unknown")

        if status == "semver-safe-update":
            regular_updates.append((name, curr, latest, "Patch / Minor"))
        else:
            semver_breaks.append((name, curr, latest, status))

    db_status = "FAIL" if pending_db_count > 0 else "OK"
    drupal_status = "WARN" if drupal_pkgs else "OK"
    other_status = "INFO" if other_pkgs else "OK"

    with open(summary_file, "a", encoding="utf-8") as f:
        f.write("| Update Metric | Count | Status |\n")
        f.write("|---------------|-------|--------|\n")
        f.write(f"| Pending DB Updates (Drush) | `{pending_db_count}` | {db_status} |\n")
        f.write(f"| Outdated Drupal Packages | `{len(drupal_pkgs)}` | {drupal_status} |\n")
        f.write(f"| Other Outdated Packages | `{len(other_pkgs)}` | {other_status} |\n\n")

        if drupal_pkgs:
            f.write("#### Detailed Drupal Package Status\n\n")
            f.write("| Package | Current Version | Latest Available | Update Type |\n")
            f.write("|---------|-----------------|------------------|-------------|\n")
            for name, curr, latest, utype in regular_updates + semver_breaks:
                f.write(f"| `{name}` | `{curr}` | `{latest}` | `{utype}` |\n")
            f.write("\n")
        else:
            f.write("All direct Drupal dependencies are up to date.\n\n")

    has_updates = "true" if (len(drupal_pkgs) > 0 or pending_db_count > 0) else "false"
    with open(gh_output, "a", encoding="utf-8") as out:
        out.write("security_updates_count=0\n")
        out.write(f"outdated_packages_count={len(drupal_pkgs)}\n")
        out.write(f"pending_db_updates_count={pending_db_count}\n")
        out.write(f"has_pending_updates={has_updates}\n")

if __name__ == "__main__":
    main()
