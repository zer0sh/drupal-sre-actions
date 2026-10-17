#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET

def main():
    junit_path = sys.argv[1]
    summary_path = sys.argv[2]
    exit_code = int(sys.argv[3])
    gh_output = sys.argv[4]

    tests = 0
    assertions = 0
    failures = 0
    errors = 0
    time = "0.0"

    if os.path.exists(junit_path):
        try:
            tree = ET.parse(junit_path)
            root = tree.getroot()
            if root.tag == "testsuite":
                tests = int(root.attrib.get("tests", 0))
                assertions = int(root.attrib.get("assertions", 0))
                failures = int(root.attrib.get("failures", 0))
                errors = int(root.attrib.get("errors", 0))
                time = root.attrib.get("time", "0.0")
            else:
                for suite in root.findall(".//testsuite"):
                    tests += int(suite.attrib.get("tests", 0))
                    assertions += int(suite.attrib.get("assertions", 0))
                    failures += int(suite.attrib.get("failures", 0))
                    errors += int(suite.attrib.get("errors", 0))
        except Exception as e:
            print(f"Error parsing JUnit: {e}")

    fail_label = "FAIL" if failures > 0 else "PASS"
    error_label = "FAIL" if errors > 0 else "PASS"

    with open(summary_path, "a", encoding="utf-8") as sf:
        sf.write("| Metric | Value | Status |\n")
        sf.write("|--------|-------|--------|\n")
        sf.write(f"| Total Tests | `{tests}` | INFO |\n")
        sf.write(f"| Total Assertions | `{assertions}` | INFO |\n")
        sf.write(f"| Failures | `{failures}` | {fail_label} |\n")
        sf.write(f"| Errors | `{errors}` | {error_label} |\n")
        sf.write(f"| Duration | `{time}s` | INFO |\n\n")

        if exit_code == 0:
            sf.write("All tests passed successfully.\n")
        else:
            sf.write("**Alert:** One or more tests failed or encountered runtime errors.\n")

    status_label = "success" if exit_code == 0 else "failure"
    with open(gh_output, "a", encoding="utf-8") as out:
        out.write(f"total_tests={tests}\n")
        out.write(f"total_assertions={assertions}\n")
        out.write(f"failures_count={failures}\n")
        out.write(f"errors_count={errors}\n")
        out.write(f"status={status_label}\n")

if __name__ == "__main__":
    main()
