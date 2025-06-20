from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4   # rM2’s screen is very close to A5, but A4 scales well

c = canvas.Canvas("workout_sample.pdf", pagesize=A4)

# A very simple layout – tweak coordinates or use reportlab.platypus later
c.setFont("Helvetica-Bold", 18)
c.drawString(72, 770, "Monday Workout")

c.setFont("Helvetica", 12)
lines = [
    "• Push-ups — 3 × 15",
    "• Goblet Squats — 3 × 12",
    "• Plank — 3 × 45 s",
]
y = 740
for line in lines:
    c.drawString(72, y, line)
    y -= 20

c.save()
print("Created workout_sample.pdf")
