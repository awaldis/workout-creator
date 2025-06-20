from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Output filename
OUTPUT = "workout_boxes_underneath.pdf"

# Page setup
c = canvas.Canvas(OUTPUT, pagesize=A4)
page_width, page_height = A4
margin = 72              # 1" margin
usable_width = page_width - 2 * margin

# Header
c.setFont("Helvetica-Bold", 18)
c.drawString(margin, page_height - margin, "Monday Workout")

# Exercises
c.setFont("Helvetica", 12)
exercises = [
    "• Push-ups — 3 × 15",
    "• Goblet Squats — 3 × 12",
    "• Plank — 3 × 45 s",
]

# Layout parameters
y = page_height - margin - 30  # start below header
box_h = 40                     # box height for handwriting
text_to_box_gap = 8            # space between text baseline and top of box
box_to_next_gap = 20           # space after box before next exercise

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
print(f"Created {OUTPUT}")
