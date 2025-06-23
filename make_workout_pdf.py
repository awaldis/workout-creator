"""Generate a PDF workout sheet with blank boxes for recording reps/weights."""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


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
    DEFAULT_EXERCISES = [
        "• Pull-ups — No Assist - 7",
        "• Neck — Back Head on Bench - 14, 10",
        "• Push-Ups - Narrow - PS Feet on Floor — 9, 6",
        "• Glutes - One Hip Thrust - L — 0# × 25, 20 - R — 0# × 25, 20",
        "• Traps - Hex Bar - 180# × 20, 20",
        "• Lower Back - GHD - #4 Hole  × 18, 8",
        "• Shoulder - Uppercut - 25# × 21, 18",
        "• Traps - Elbow Chair Reverse Pushup Belly Up - 19, 12",
        "• Ab Wheel - 0# × 12, 8",
        "• Hammer Curls - One Arm Side - 20# × 22, 25# × 10",
        "• Back Squats - 85# × 17, 10",
        "• Standing Triceps Extensions - Behind Head - 15# × 22, 20# × 10",
    ]

    create_workout_pdf(DEFAULT_EXERCISES, DEFAULT_OUTPUT_FILENAME, DEFAULT_SHEET_TITLE)
