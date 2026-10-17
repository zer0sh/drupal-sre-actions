#!/usr/bin/env python3
"""
Semantic version calculator based on Conventional Commits and Git tags.
Zero external dependencies.
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


def parse_semver(tag_str, prefix="v"):
    clean = tag_str
    if prefix and clean.startswith(prefix):
        clean = clean[len(prefix):]
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$", clean)
    if not m:
        return None
    major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
    prerelease = m.group(4) or ""
    return (major, minor, patch, prerelease, clean)


def get_latest_tag(prefix="v"):
    output = run_git(["tag", "-l"])
    if not output:
        return None, (0, 0, 0, "", "0.0.0")

    tags = output.splitlines()
    parsed = []
    for t in tags:
        p = parse_semver(t.strip(), prefix)
        if p:
            parsed.append((t.strip(), p))

    if not parsed:
        return None, (0, 0, 0, "", "0.0.0")

    parsed.sort(key=lambda item: (item[1][0], item[1][1], item[1][2]))
    latest_tag_name, latest_semver = parsed[-1]
    return latest_tag_name, latest_semver


def get_commit_messages(since_tag=None):
    args = ["log", "--format=%B%x00"]
    if since_tag:
        args.append(f"{since_tag}..HEAD")
    else:
        args.append("HEAD")

    raw = run_git(args)
    if not raw:
        return []
    commits = [c.strip() for c in raw.split("\x00") if c.strip()]
    return commits


def determine_bump_from_commits(commits):
    breaking_patterns = [
        re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE),
        re.compile(r"^[a-zA-Z0-9_-]+(\([^\)]+\))?!:")
    ]
    feat_pattern = re.compile(r"^feat(\([^\)]+\))?:")
    fix_pattern = re.compile(r"^(fix|perf|refactor|docs|style|test|build|ci|chore)(\([^\)]+\))?:")

    has_breaking = False
    has_feat = False
    has_fix = False

    for msg in commits:
        for bp in breaking_patterns:
            if bp.search(msg):
                has_breaking = True
                break
        if has_breaking:
            break
        if feat_pattern.search(msg):
            has_feat = True
        elif fix_pattern.search(msg):
            has_fix = True

    if has_breaking:
        return "major"
    if has_feat:
        return "minor"
    if has_fix:
        return "patch"
    return "none"


def main():
    bump_input = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else "auto"
    tag_prefix = sys.argv[2].strip() if len(sys.argv) > 2 and sys.argv[2].strip() else "v"
    first_version = sys.argv[3].strip() if len(sys.argv) > 3 and sys.argv[3].strip() else "1.0.0"

    latest_tag_name, (prev_maj, prev_min, prev_patch, _, prev_ver_str) = get_latest_tag(tag_prefix)
    commits = get_commit_messages(latest_tag_name)

    explicit_semver = parse_semver(bump_input, tag_prefix)
    if explicit_semver:
        new_maj, new_min, new_patch, _, new_ver_str = explicit_semver
        bump_type = "explicit"
        has_bump = True
    elif bump_input in ["patch", "minor", "major"]:
        bump_type = bump_input
        if latest_tag_name is None:
            p_first = parse_semver(first_version, tag_prefix)
            new_maj, new_min, new_patch, _, new_ver_str = p_first
        else:
            if bump_type == "major":
                new_maj, new_min, new_patch = prev_maj + 1, 0, 0
            elif bump_type == "minor":
                new_maj, new_min, new_patch = prev_maj, prev_min + 1, 0
            else:
                new_maj, new_min, new_patch = prev_maj, prev_min, prev_patch + 1
            new_ver_str = f"{new_maj}.{new_min}.{new_patch}"
        has_bump = True
    elif bump_input == "auto":
        detected_bump = determine_bump_from_commits(commits)
        if latest_tag_name is None:
            p_first = parse_semver(first_version, tag_prefix)
            new_maj, new_min, new_patch, _, new_ver_str = p_first
            bump_type = "initial"
            has_bump = bool(commits)
        else:
            if detected_bump == "none":
                bump_type = "none"
                new_maj, new_min, new_patch, new_ver_str = prev_maj, prev_min, prev_patch, prev_ver_str
                has_bump = False
            else:
                bump_type = detected_bump
                if bump_type == "major":
                    new_maj, new_min, new_patch = prev_maj + 1, 0, 0
                elif bump_type == "minor":
                    new_maj, new_min, new_patch = prev_maj, prev_min + 1, 0
                else:
                    new_maj, new_min, new_patch = prev_maj, prev_min, prev_patch + 1
                new_ver_str = f"{new_maj}.{new_min}.{new_patch}"
                has_bump = True
    else:
        raise ValueError(f"Invalid bump input: {bump_input}")

    tag_name = f"{tag_prefix}{new_ver_str}"
    major_tag = f"{tag_prefix}{new_maj}"

    outputs = {
        "previous_tag": latest_tag_name or "",
        "previous_version": prev_ver_str,
        "version": new_ver_str,
        "tag": tag_name,
        "major_tag": major_tag,
        "bump_type": bump_type,
        "has_bump": "true" if has_bump else "false",
        "commits_count": str(len(commits)),
    }

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            for k, v in outputs.items():
                f.write(f"{k}={v}\n")

    for k, v in outputs.items():
        print(f"{k}={v}")


if __name__ == "__main__":
    main()
