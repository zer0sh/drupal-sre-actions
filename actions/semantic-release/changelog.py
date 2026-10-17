#!/usr/bin/env python3
"""
Generates structured Markdown release notes from Conventional Commits.
Zero external dependencies and strictly no emojis.
"""
import os
import re
import subprocess
import sys


def run_git(args):
    try:
        res = subprocess.run(
            ["git"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_commits(since_tag=None):
    cmd = ["log", "--format=%h%x1f%s%x1f%b%x1e"]
    if since_tag:
        cmd.append(f"{since_tag}..HEAD")
    else:
        cmd.append("HEAD")

    raw = run_git(cmd)
    if not raw:
        return []

    commits = []
    for entry in raw.split("\x1e"):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split("\x1f")
        h = parts[0].strip() if len(parts) > 0 else ""
        s = parts[1].strip() if len(parts) > 1 else ""
        b = parts[2].strip() if len(parts) > 2 else ""
        commits.append({
            "hash": h,
            "subject": s,
            "body": b
        })
    return commits


def parse_conventional_commit(subject, body):
    breaking_patterns = [
        re.compile(r"^BREAKING[ -]CHANGE:\s*(.*)", re.MULTILINE),
        re.compile(r"^[a-zA-Z0-9_-]+(\([^\)]+\))?!:\s*(.*)")
    ]
    is_breaking = False
    breaking_desc = ""

    for bp in breaking_patterns:
        m = bp.search(body) or bp.search(subject)
        if m:
            is_breaking = True
            breaking_desc = m.group(1) if m.groups() else subject
            break

    conv_match = re.match(r"^([a-zA-Z0-9_-]+)(?:\(([^\)]+)\))?!?:?\s*(.*)$", subject)
    if conv_match:
        ctype = conv_match.group(1).lower()
        scope = conv_match.group(2) or ""
        desc = conv_match.group(3) or subject
    else:
        ctype = "other"
        scope = ""
        desc = subject

    return {
        "type": ctype,
        "scope": scope,
        "description": desc,
        "is_breaking": is_breaking,
        "breaking_desc": breaking_desc
    }


def generate_markdown(version, tag, previous_tag, commits):
    sections = {
        "breaking": [],
        "feat": [],
        "fix": [],
        "perf": [],
        "refactor": [],
        "docs": [],
        "chore": [],
        "other": []
    }

    type_map = {
        "feat": "Features",
        "fix": "Bug Fixes",
        "perf": "Performance Improvements",
        "refactor": "Refactoring",
        "docs": "Documentation",
        "chore": "Chores & Maintenance",
        "build": "Build & Dependencies",
        "ci": "CI/CD & Workflows"
    }

    for c in commits:
        parsed = parse_conventional_commit(c["subject"], c["body"])
        item = {
            "hash": c["hash"],
            "scope": parsed["scope"],
            "desc": parsed["description"]
        }
        if parsed["is_breaking"]:
            sections["breaking"].append({
                "hash": c["hash"],
                "desc": parsed["breaking_desc"] or parsed["desc"]
            })

        t = parsed["type"]
        if t in sections:
            sections[t].append(item)
        elif t in ["build", "ci"]:
            sections["chore"].append(item)
        else:
            sections["other"].append(item)

    lines = []
    lines.append(f"## Release {tag}")
    lines.append("")
    if previous_tag:
        lines.append(f"Changes since `{previous_tag}`:")
    else:
        lines.append("Initial release.")
    lines.append("")

    if sections["breaking"]:
        lines.append("### Breaking Changes")
        lines.append("")
        for it in sections["breaking"]:
            lines.append(f"- {it['desc']} (`{it['hash']}`)")
        lines.append("")

    for key, title in type_map.items():
        items = sections.get(key, [])
        if items:
            lines.append(f"### {title}")
            lines.append("")
            for it in items:
                scope_str = f"**{it['scope']}:** " if it["scope"] else ""
                lines.append(f"- {scope_str}{it['desc']} (`{it['hash']}`)")
            lines.append("")

    if sections["other"]:
        lines.append("### Other Changes")
        lines.append("")
        for it in sections["other"]:
            lines.append(f"- {it['desc']} (`{it['hash']}`)")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    version = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "1.0.0"
    tag = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else f"v{version}"
    previous_tag = sys.argv[3].strip() if len(sys.argv) > 3 and sys.argv[3].strip() else ""
    output_file = sys.argv[4].strip() if len(sys.argv) > 4 and sys.argv[4].strip() else "/tmp/release_notes.md"

    commits = get_commits(previous_tag if previous_tag else None)
    md = generate_markdown(version, tag, previous_tag, commits)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Generated changelog at {output_file} ({len(commits)} commits)")


if __name__ == "__main__":
    main()
