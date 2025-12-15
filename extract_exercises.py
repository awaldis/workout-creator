#!/usr/bin/env python3
"""Extract completed exercise information from a workout PDF.

This script reads the workout PDF that was produced by
``make_workout_pdf.py`` after it has been filled in with hand written (or
otherwise inserted) numbers.  Handwritten content inside each box is
extracted via OCR to determine the repetitions, weights and sets performed.
The results for all exercises are written to a text file in JSON format
which can later be imported into the database.

The parsing rules for the text inside each box are intentionally
"minimalist" so that even hastily written notes can be interpreted:

* A number followed by ``#`` represents a weight.
* ``x`` or ``×`` separates a weight from the repetition count.
* Repetition counts are comma separated.
* If multiple sets are performed at the same weight the weight value is only
  written once before the first set.
* Bilateral exercises are denoted with ``L -`` and ``R -`` sections.
* Any extra text that cannot be interpreted as weights or repetitions is
  preserved and reported as a warning.

The goal of the parser is not to be perfect but to do its best while warning
about anything suspicious so that the user can correct the data later if
needed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract


# ---------------------------------------------------------------------------
# Data structures


@dataclass
class ExerciseData:
    """Container for parsed exercise information."""

    exercise_name: str
    laterality: str
    reps_left: str
    reps_right: Optional[str]
    sets: int
    weight_left: str
    weight_right: Optional[str]
    extra_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        data = {
            "exercise_name": self.exercise_name,
            "laterality": self.laterality,
            "reps_left": self.reps_left or None,
            "reps_right": self.reps_right,
            "sets": self.sets,
            "weight_left": self.weight_left or None,
            "weight_right": self.weight_right,
        }
        if self.extra_text:
            data["extra_text"] = self.extra_text
        return data


# ---------------------------------------------------------------------------
# Parsing helpers


PAIR_RE = re.compile(r"(\d{1,3})#\s*[x×]\s*(\d{1,3})", re.IGNORECASE)
NUM_RE = re.compile(r"\d{1,3}")


def _parse_number(token: str, line: str) -> Optional[int]:
    """Return ``int(token)`` if the token looks like a valid number.

    If the token has four or more digits it is considered suspicious and a
    warning is emitted.  ``None`` is returned in that case so that the caller
    can fall back to a reasonable interpretation.
    """

    if len(token) >= 4:
        print(
            f"WARNING: token '{token}' in line '{line}' has four or more digits and "
            "is ignored.",
            file=sys.stderr,
        )
        return None
    return int(token)


def parse_side(data: str, original_line: str) -> Dict[str, Optional[str]]:
    """Parse the content for one side of an exercise.

    Returns a mapping with ``weights`` (list[int]), ``reps`` (list[int]) and
    ``extra_text`` (optional string).
    """

    weights: List[int] = []
    reps: List[int] = []
    extra_parts: List[str] = []

    work = data.replace("×", "x")

    # Extract weight/repetition pairs first (e.g. ``90# x 10``)
    for match in PAIR_RE.finditer(work):
        w_token, r_token = match.groups()
        w = _parse_number(w_token, original_line)
        r = _parse_number(r_token, original_line)
        if w is not None and r is not None:
            weights.append(w)
            reps.append(r)
    work = PAIR_RE.sub("", work)

    # Remaining numbers are repetitions possibly sharing the last weight
    last_weight = weights[-1] if weights else 0
    for match in NUM_RE.finditer(work):
        start = match.start()
        # Ignore numbers that are part of fragments like "#4" which are
        # usually notes about equipment settings rather than reps.
        if start > 0 and work[start - 1] == "#":
            continue
        token = match.group()
        r = _parse_number(token, original_line)
        if r is not None:
            reps.append(r)
            weights.append(last_weight)
    work = NUM_RE.sub("", work)

    leftover = work.strip().strip(",")
    if leftover:
        extra_parts.append(leftover)

    extra_text = " ".join(p.strip() for p in extra_parts if p.strip()) or None

    return {
        "weights": weights,
        "reps": reps,
        "extra_text": extra_text,
    }


def join_numbers(nums: List[int]) -> str:
    return ",".join(str(n) for n in nums)


# ---------------------------------------------------------------------------
# Main extraction logic


def extract_exercise_data(pdf_path: Path) -> List[ExerciseData]:
    """Return a list of ``ExerciseData`` objects for the given PDF.

    The exercise names are taken from the printed text in the PDF while the
    repetitions and weights are read from the handwritten content inside each
    box via OCR.
    """

    text = extract_text(str(pdf_path))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []

    # The first line is the sheet title.  Everything else should be exercise
    # names possibly followed by the recognised box content.  Strip any trailing
    # data so we only keep the exercise names.
    def _extract_name(line: str) -> str:
        match = re.search(r"(?:[LR]\s*-\s*|\d)", line)
        if match:
            idx = line.rfind(" - ", 0, match.start())
            if idx != -1:
                return line[:idx].strip()
            return line[: match.start()].strip()
        return line.strip()

    exercise_names = [_extract_name(l) for l in lines[1:]]

    images = convert_from_path(str(pdf_path), dpi=300)
    if not images:
        return []

    img = images[0]
    scale = 300 / 72  # points to pixels
    page_height_pts = img.height / scale
    margin_pts = 72
    top_margin_pts = 36
    box_h_pts = 37
    text_to_box_gap_pts = 8
    box_to_next_gap_pts = 18
    y_pts = page_height_pts - top_margin_pts - 28

    exercises: List[ExerciseData] = []

    for name in exercise_names:
        box_top_pts = y_pts - text_to_box_gap_pts
        box_bottom_pts = box_top_pts - box_h_pts
        left_px = margin_pts * scale
        right_px = img.width - margin_pts * scale
        upper_px = img.height - box_top_pts * scale
        lower_px = img.height - box_bottom_pts * scale
        crop_box = (int(left_px), int(upper_px), int(right_px), int(lower_px))
        box_img = img.crop(crop_box)
        ocr_config = "--psm 6 -c tessedit_char_whitelist=0123456789LRlr#xX-,"
        box_text = pytesseract.image_to_string(box_img, config=ocr_config)
        box_text = box_text.replace("\n", " ").strip()

        if "L -" in box_text and "R -" in box_text:
            _, rest = box_text.split("L -", 1)
            left_part, right_part = rest.split("R -", 1)
            left_info = parse_side(left_part, box_text)
            right_info = parse_side(right_part, box_text)
            sets_left = len(left_info["reps"])
            sets_right = len(right_info["reps"])
            if sets_left != sets_right:
                print(
                    f"WARNING: left/right set count mismatch in line '{box_text}'",
                    file=sys.stderr,
                )
            sets = max(sets_left, sets_right)
            exercise = ExerciseData(
                exercise_name=name,
                laterality="bilateral",
                reps_left=join_numbers(left_info["reps"]),
                reps_right=join_numbers(right_info["reps"]),
                sets=sets,
                weight_left=join_numbers(left_info["weights"]),
                weight_right=join_numbers(right_info["weights"]),
                extra_text=" ".join(
                    filter(
                        None,
                        [left_info.get("extra_text"), right_info.get("extra_text")],
                    )
                )
                or None,
            )
        else:
            side_info = parse_side(box_text, box_text)
            exercise = ExerciseData(
                exercise_name=name,
                laterality="unilateral",
                reps_left=join_numbers(side_info["reps"]),
                reps_right=None,
                sets=len(side_info["reps"]),
                weight_left=join_numbers(side_info["weights"]),
                weight_right=None,
                extra_text=side_info.get("extra_text"),
            )

        exercises.append(exercise)
        y_pts = box_bottom_pts - box_to_next_gap_pts

    return exercises


def write_exercise_data(pdf_path: Path, data: List[ExerciseData]) -> Path:
    """Write ``data`` to a text file next to ``pdf_path``.

    The file is returned so callers can report its location.
    """

    output_path = pdf_path.with_suffix(".txt")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump([ex.to_dict() for ex in data], f, indent=2)
    return output_path


# ---------------------------------------------------------------------------
# Command line interface


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract exercise data from a completed workout PDF"
    )
    parser.add_argument("pdf", type=Path, help="Path to the workout PDF")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path for the extracted data (defaults to <pdf>.txt)",
    )
    args = parser.parse_args(argv)

    data = extract_exercise_data(args.pdf)

    out_file = args.output if args.output else args.pdf.with_suffix(".txt")
    with out_file.open("w", encoding="utf-8") as f:
        json.dump([ex.to_dict() for ex in data], f, indent=2)

    print(f"Wrote extracted data to {out_file}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())

