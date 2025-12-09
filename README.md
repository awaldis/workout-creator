# workout-creator

A complete workout management system for reMarkable tablet users. Track your exercises, create custom workout PDFs, and maintain a historical database of your fitness progress.

## Overview

This tool helps you:
1. Record completed workouts by exporting handwritten notes from your reMarkable
2. Extract workout data using AI and save it to a database
3. Select exercises for your next workout using a visual web interface
4. Generate a new workout PDF to take back to your reMarkable

## Requirements

### Python Packages

Install the required packages:

```bash
pip install pyperclip flask reportlab
```

- `pyperclip` - Clipboard access for importing workout data
- `flask` - Web server for the exercise selection GUI
- `reportlab` - PDF generation for workout sheets

### Prerequisites

- Python 3.7 or higher
- A reMarkable tablet (or any device that can export handwritten notes as images)
- Access to an AI chatbot capable of processing images (e.g., Claude, ChatGPT)

## Initial Setup

### 1. Initialize the Database

Before using the system, create the exercise database:

```bash
python exercise_database.py init
```

This creates `exercise_log.db` in your project directory. This SQLite database will store all your completed exercises.

### 2. Understanding Exercise Recording Syntax

On your reMarkable workout sheet, you'll record exercises in a specific format. The AI uses the prompt in `llm_extraction_prompt.md` to parse your handwriting. Here's a quick overview:

**Unilateral exercises** (one side at a time):
```
Exercise Name - 30# x 12, 35# x 10, 35# x 8
```
(weight and reps for each set, comma-separated)

**Bilateral exercises** (both sides):
```
Exercise Name - L - 115# x 20, 190# x 15  R - 115# x 20, 190# x 15
```
(left and right sides labeled separately)

**Body weight exercises** (no weights):
```
Chin-ups - 8, 6, 5
```
(just reps for each set)

## Workflow

### Step 1: Export Your Completed Workout

After completing a workout on your reMarkable:
1. Export the workout page from your reMarkable in PNG format
2. Save the image file to your computer

### Step 2: Convert Handwritten Data to CSV

1. Open your AI chatbot (Claude, ChatGPT, etc.)
2. Upload the PNG image of your workout
3. Paste the prompt from `llm_extraction_prompt.md` into the chat
4. The AI will return CSV-formatted text with your workout data

### Step 3: Copy CSV to Clipboard

Copy the CSV text block (not the JSON warnings) that the AI generated.

### Step 4: Import to Database

Run the clipboard import script:

```bash
python clipboard_to_db.py
```

This script will:
- Read the CSV data from your clipboard
- Save it to a timestamped CSV file
- Look up body parts for each exercise from your database
- Display a preview of the exercises
- Ask for confirmation before importing to the database

Optional flags:
- `-p` or `--preview` - Show a preview of clipboard content before processing
- `-o` or `--output` - Specify a custom output filename
- `--database` - Use a different database file (default: exercise_log.db)

### Step 5: Start the Exercise Selection GUI

Launch the web interface:

```bash
python exercise_gui.py
```

The server will start on `http://localhost:5000`. Open this URL in your web browser.

### Step 6: Select Your Exercises

In the web interface:
1. Browse exercises organized by body part
2. Click on exercises to add them to your workout plan
3. Arrange them in your desired order
4. Each exercise shows the most recent weights/reps you completed

### Step 7: Create Workout PDF

1. Click the "Create Workout PDF" button in the web interface
2. Your browser will download a PDF file named with today's date (e.g., `2025-12-09 Workout.pdf`)
3. The PDF contains blank boxes below each exercise name for recording your results

### Step 8: Transfer to reMarkable

1. Copy the generated PDF to your reMarkable tablet
2. Open it on your reMarkable
3. Complete your workout and record results using the reMarkable pen

### Step 9: Repeat

When you're ready for your next workout, return to Step 1!

## Additional Database Commands

### Manually Add an Exercise

If you need to manually add an exercise to the database, the easiest way is to open `exercise_log.db` using a SQLite GUI tool (such as DB Browser for SQLite) and insert rows directly into the `exercises` table.

Alternatively, you can use the command line:

```bash
# Unilateral example (3 sets)
python exercise_database.py add \
    --date 2025-12-09 \
    --body-part Biceps \
    --name "Concentration Curl" \
    --laterality unilateral \
    --sets 3 \
    --weight 30 35 35 \
    --reps 12 10 8

# Bilateral example (2 sets)
python exercise_database.py add \
    --date 2025-12-09 \
    --body-part Chest \
    --name "Bench Press" \
    --laterality bilateral \
    --sets 2 \
    --weight-left 135 145 \
    --weight-right 135 145 \
    --reps-left 10 8 \
    --reps-right 10 8
```

### List All Exercises

View all exercises in your database:

```bash
python exercise_database.py list
```

### Export Specific Exercises

Export exercises by their database IDs to a text file:

```bash
python exercise_database.py export --ids 1 2 3 5 8 --output my_workout.txt
```

This creates a text file formatted for use with `make_workout_pdf.py`.

## File Organization

### Active Files

- `clipboard_to_db.py` - Import workout data from clipboard to database
- `exercise_gui.py` - Web interface for exercise selection
- `exercise_database.py` - Database management utilities
- `import_csv_to_db.py` - CSV import functionality (used by clipboard_to_db.py)
- `make_workout_pdf.py` - PDF generation (used by exercise_gui.py)
- `llm_extraction_prompt.md` - AI prompt for extracting workout data from images

### Supporting Files

- `exercise_log.db` - SQLite database (created after running `init`)
- `default_exercises.txt` - Default exercise list (currently unused in main workflow)
- `templates/` - HTML templates for the web interface (Flask)

### Potentially Obsolete Files

The following files may be from an older workflow and could potentially be removed:

- `extract_exercises.py` - Old PDF text extraction (requires `pdfminer`)
- `add_body_part_to_csv.py` - Body part addition (now integrated into clipboard_to_db.py)

## Troubleshooting

### Database Not Found Error

If you see "Error: Database file not found", run:
```bash
python exercise_database.py init
```

### Clipboard Import Issues

- Make sure you've installed `pyperclip`: `pip install pyperclip`
- Ensure you've copied the CSV text (not the JSON warnings)
- Verify the CSV has the correct header format

### Web Interface Won't Start

- Check that port 5000 is not already in use
- Make sure Flask is installed: `pip install flask`
- Verify the database exists: `python exercise_database.py list`

### PDF Generation Issues

- Ensure reportlab is installed: `pip install reportlab`
- Check that you have write permissions in the current directory

## Valid Body Parts

When manually adding exercises, use these body part names:
- Chest
- Upper Back
- Lower Back
- Shoulders
- Calves
- Glutes
- Core
- Biceps
- Triceps
- Rotator Cuff
- Neck
- Forearm
- Hamstrings
- Quads
- Traps
- Tibia Dorsi
- Knee
- Hip
- Legs

## License

This is a personal workout tracking tool. Use and modify as needed for your fitness journey!
