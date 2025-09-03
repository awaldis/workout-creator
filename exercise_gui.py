#!/usr/bin/env python3
"""
Web-based GUI for exercise selection and workout planning.
Shows most recent exercises grouped by body part with drag-and-drop workout builder.
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
from pathlib import Path
from collections import defaultdict

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
    ORDER BY e.body_part, e.exercise_name
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


if __name__ == '__main__':
    if not DB_PATH.exists():
        print(f"Error: Database file {DB_PATH} not found")
        print("Run 'python3 exercise_database.py init' to create the database")
        exit(1)
    
    print("Starting Exercise Selection GUI...")
    print("Open your browser to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)