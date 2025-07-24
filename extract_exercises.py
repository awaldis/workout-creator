#!/usr/bin/env python3
"""Extract exercise names from a workout PDF."""

import argparse
import re
from pdfminer.high_level import extract_text


def extract_exercise_names(pdf_path):
    """Return a list of exercise names from the given PDF."""
    text = extract_text(pdf_path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Skip the first line which is the sheet title
    pattern = re.compile(r" - (?=[0-9#])")
    names = []
    for line in lines[1:]:
        match = pattern.search(line)
        if match:
            name = line[: match.start()].strip()
            names.append(name)
    return names


def main():
    parser = argparse.ArgumentParser(description="Extract exercise names from a workout PDF")
    parser.add_argument("pdf", help="Path to the workout PDF")
    args = parser.parse_args()
    for name in extract_exercise_names(args.pdf):
        print(name)


if __name__ == "__main__":
    main()
