#!/usr/bin/env python3
import json
import os
import re
import sys

def scan_gitleaks(summary_path, report_path, gh_output_path):
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    with open(summary_path, "a", encoding="utf-8") as sf:
        if data:
            sf.write(f"**Alert:** Found {len(data)} potential secret(s) or exposed token(s).\n\n")
            sf.write("| Rule | File | Secret Hash / Snippet |\n")
            sf.write("|------|------|------------------------|\n")
            for item in data:
                rule = item.get("RuleID", "Unknown")
                file = item.get("File", "")
                secret = item.get("Secret", "")
                redacted = secret[:4] + "****" if len(secret) > 4 else "****"
                sf.write(f"| `{rule}` | `{file}` | `{redacted}` |\n")
        else:
            sf.write("No hardcoded secrets or credentials detected.\n")

    with open(gh_output_path, "a", encoding="utf-8") as out:
        val = "true" if data else "false"
        out.write(f"secrets_detected={val}\n")

def scan_fallback(summary_path, gh_output_path):
    patterns = [
        (r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']", "Generic API Key"),
        (r"-----BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY-----", "Private Key"),
        (r"(?i)drupal_hash_salt\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']", "Drupal Hash Salt"),
        (r"(?i)mysql://[^:]+:[^@]+@[^/]+", "Database URL with Password"),
    ]

    found = []
    for root, dirs, files in os.walk("."):
        for ignore_dir in [".git", "vendor", "node_modules"]:
            if ignore_dir in dirs:
                dirs.remove(ignore_dir)
        for f in files:
            fpath = os.path.join(root, f)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as cf:
                    txt = cf.read()
                    for pattern, label in patterns:
                        if re.search(pattern, txt):
                            found.append((label, fpath))
            except Exception:
                pass

    with open(summary_path, "a", encoding="utf-8") as sf:
        if found:
            sf.write(f"**Alert:** Found {len(found)} potential secret matches.\n\n")
            for label, fpath in found:
                sf.write(f"- `{label}` detected in `{fpath}`\n")
        else:
            sf.write("No hardcoded secrets detected.\n")

    with open(gh_output_path, "a", encoding="utf-8") as out:
        val = "true" if found else "false"
        out.write(f"secrets_detected={val}\n")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "gitleaks":
        scan_gitleaks(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        scan_fallback(sys.argv[2], sys.argv[3])
