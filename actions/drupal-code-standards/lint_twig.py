#!/usr/bin/env python3
import glob
import sys

def main():
    errors = 0
    for path in sys.argv[1:]:
        for f in glob.glob(f"{path}/**/*.twig", recursive=True):
            with open(f, "r", encoding="utf-8", errors="ignore") as tf:
                content = tf.read()
                if content.count("{%") != content.count("%}"):
                    print(f"Error in {f}: Unmatched {{% ... %}} tags.")
                    errors += 1
                if content.count("{{") != content.count("}}"):
                    print(f"Error in {f}: Unmatched {{{{ ... }}}} tags.")
                    errors += 1
    sys.exit(1 if errors > 0 else 0)

if __name__ == "__main__":
    main()
