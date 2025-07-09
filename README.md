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

## Exercise Database

The repository includes a small utility script, `exercise_database.py`, which
manages a local SQLite database of completed exercises. The database is stored in
`exercise_log.db` in the repository directory. Because it uses SQLite, the
database is a single file and requires no additional server setup.

### Initializing the Database

Run the following command once to create the database file and table:

```
python3 exercise_database.py init
```

### Adding Entries

Use the `add` command to record an exercise. The body part and laterality
arguments are validated against predefined lists. A required `--sets` argument
controls how many values are expected for the weight and reps options.
For unilateral exercises, provide one weight and rep value per set using
`--weight` and `--reps`. For bilateral exercises, provide left and right values
separately using `--weight-left`, `--weight-right`, `--reps-left` and
`--reps-right`.

Examples:

```

# Unilateral example (3 sets)
python3 exercise_database.py add \
    --date 2023-09-07 \
    --body-part Biceps \
    --name "Concentration Curl" \
    --laterality unilateral \
    --sets 3 \
    --weight 30 35 35 \
    --reps 12 10 8

# Bilateral example (2 sets)
python3 exercise_database.py add \
    --date 2023-09-07 \
    --body-part Chest \
    --name "Bench Press" \
    --laterality bilateral \
    --sets 2 \
    --weight-left 135 145 \
    --weight-right 135 145 \
    --reps-left 10 8 \
    --reps-right 10 8
```

### Listing Entries

To view all recorded exercises:

```
python3 exercise_database.py list
```

Each row is printed as a tuple in the order it was stored in the database.

