"""Generate a PDF workout sheet with blank boxes for recording reps/weights."""

from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def load_exercises_from_file(path):
    """Return a list of exercise lines from the given text file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def create_workout_pdf(exercises, output_filename, sheet_title):
    """Create a workout PDF with the given exercises."""
    # Page setup
    c = canvas.Canvas(output_filename, pagesize=A4)
    page_width, page_height = A4
    top_margin = 36
    margin = 72  # 1" margin
    usable_width = page_width - 2 * margin

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, page_height - top_margin, sheet_title)

    # Exercises
    c.setFont("Helvetica", 12)

    # Layout parameters
    y = page_height - top_margin - 28  # start below header
    box_h = 37  # box height for handwriting
    text_to_box_gap = 8  # space between text baseline and top of box
    box_to_next_gap = 18  # space after box before next exercise

    for ex in exercises:
        # draw the exercise text
        c.drawString(margin, y, ex)

        # compute box position: box top is text baseline minus gap
        box_top = y - text_to_box_gap
        box_bottom = box_top - box_h

        # draw the box spanning the margins
        c.rect(margin, box_bottom, usable_width, box_h)

        # advance y for next exercise
        y = box_bottom - box_to_next_gap

    c.save()
    print(f"Created {output_filename}")


if __name__ == "__main__":
    DEFAULT_OUTPUT_FILENAME = "2025-06-23 Workout.pdf"
    DEFAULT_SHEET_TITLE = "2025-06-23 - Full Body"

    DEFAULT_EXERCISES_FILE = Path(__file__).with_name("default_exercises.txt")
    DEFAULT_EXERCISES = load_exercises_from_file(DEFAULT_EXERCISES_FILE)

    create_workout_pdf(
        DEFAULT_EXERCISES, DEFAULT_OUTPUT_FILENAME, DEFAULT_SHEET_TITLE
    )
