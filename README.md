# workout-creator

Generate PDF workout logs intended to be used in a reMarkable 2.

Requires `reportlab`.

The script reads the exercises from `default_exercises.txt`. Edit this file to
customize the exercises that appear on the PDF.

```
python3 make_workout_pdf.py [-d YYYY-MM-DD] [-n "Workout Name"]
```

* `-d` / `--date` - optional date for the sheet in `YYYY-MM-DD` format. Defaults to today's date.
* `-n` / `--name` - optional workout name that appears in the sheet title. Defaults to `Workout`.

The generated PDF will be saved as `<DATE> Workout.pdf` in the current directory.
