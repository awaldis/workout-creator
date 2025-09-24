#!/usr/bin/env python3
"""
Web-based GUI for exercise selection and workout planning.
Shows most recent exercises grouped by body part with drag-and-drop workout builder.
"""

from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
from pathlib import Path
from collections import defaultdict
import tempfile
import os
from datetime import datetime
from exercise_database import export_exercises
from make_workout_pdf import create_workout_pdf, load_exercises_from_file

app = Flask(__name__)

DB_PATH = Path('exercise_log.db')


def get_most_recent_exercises():
    """
    Get the most recent exercise for each unique exercise name, grouped by body part.
    Returns dict with body_part as keys and list of exercise info as values.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get most recent exercise for each unique exercise name
    query = """
    SELECT e.id, e.exercise_name, e.body_part, e.date_completed, e.laterality, e.sets,
           e.weight_left, e.weight_right, e.reps_left, e.reps_right
    FROM exercises e
    INNER JOIN (
        SELECT exercise_name, MAX(date_completed) as max_date
        FROM exercises
        GROUP BY exercise_name
    ) recent ON e.exercise_name = recent.exercise_name AND e.date_completed = recent.max_date
    ORDER BY e.body_part, e.date_completed
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    # Group by body part
    grouped = defaultdict(list)
    for row in results:
        exercise_info = {
            'id': row[0],
            'name': row[1],
            'body_part': row[2],
            'date': row[3],
            'laterality': row[4],
            'sets': row[5],
            'weight_left': row[6],
            'weight_right': row[7],
            'reps_left': row[8],
            'reps_right': row[9]
        }
        grouped[row[2]].append(exercise_info)
    
    return dict(grouped)


@app.route('/')
def index():
    """Main page with exercise selection interface."""
    exercises_by_body_part = get_most_recent_exercises()
    return render_template('exercise_selector.html', exercises=exercises_by_body_part)


@app.route('/api/exercises')
def api_exercises():
    """API endpoint to get exercises data as JSON."""
    return jsonify(get_most_recent_exercises())


@app.route('/api/copy_ids', methods=['POST'])
def copy_ids():
    """API endpoint to receive selected exercise IDs for clipboard copying."""
    data = request.get_json()
    exercise_ids = data.get('ids', [])
    
    # Return the IDs as a space-separated string for clipboard
    ids_string = ' '.join(map(str, exercise_ids))
    return jsonify({'ids_string': ids_string, 'count': len(exercise_ids)})


@app.route('/api/create_pdf', methods=['POST'])
def create_pdf():
    """API endpoint to create a workout PDF from selected exercise IDs."""
    try:
        data = request.get_json()
        print(f"DEBUG: Received request data: {data}")
        exercise_ids = data.get('ids', []) if data else []
        print(f"DEBUG: Exercise IDs: {exercise_ids}")
        
        if not exercise_ids:
            print("DEBUG: No exercise IDs provided")
            return jsonify({'error': 'No exercise IDs provided'}), 400
    except Exception as e:
        print(f"DEBUG: Error parsing request: {e}")
        return jsonify({'error': f'Invalid request data: {str(e)}'}), 400
    
    try:
        # Create temporary file for exercise export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_txt_path = Path(temp_file.name)
        
        # Export exercises to temp file
        export_exercises(exercise_ids, temp_txt_path)
        
        # Read exercises from temp file using the same function as make_workout_pdf.py
        exercises = load_exercises_from_file(temp_txt_path)
        
        # Debug: log the exercises to help troubleshoot
        print(f"DEBUG: Exported {len(exercises)} exercises:")
        for i, ex in enumerate(exercises):
            print(f"  {i+1}: {ex}")
        
        if not exercises:
            return jsonify({'error': 'No exercises were exported from the database'}), 500
        
        # Create PDF filename with current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        pdf_filename = f"{date_str} Workout.pdf"
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Generate PDF
        sheet_title = f"{date_str} - Workout"
        create_workout_pdf(exercises, temp_pdf_path, sheet_title)
        
        # Clean up temp text file
        os.unlink(temp_txt_path)
        
        # Send PDF file - Flask will handle cleanup of temp file
        return send_file(
            temp_pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        # Clean up temp files on error
        try:
            if 'temp_txt_path' in locals():
                os.unlink(temp_txt_path)
            if 'temp_pdf_path' in locals():
                os.unlink(temp_pdf_path)
        except:
            pass
        
        return jsonify({'error': f'Failed to create PDF: {str(e)}'}), 500


if __name__ == '__main__':
    if not DB_PATH.exists():
        print(f"Error: Database file {DB_PATH} not found")
        print("Run 'python3 exercise_database.py init' to create the database")
        exit(1)
    
    print("Starting Exercise Selection GUI...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)