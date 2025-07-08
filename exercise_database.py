import argparse
import sqlite3
from pathlib import Path
from typing import List, Optional

DB_PATH = Path('exercise_log.db')

BODY_PARTS = [
    'Chest', 'Upper Back', 'Lower Back', 'Shoulders', 'Calves', 'Glutes', 'Core',
    'Biceps', 'Triceps', 'Rotator Cuff', 'Neck', 'Forearm', 'Hamstrings',
    'Quads', 'Traps', 'Tibia Dorsi', 'Knee', 'Hip', 'Legs'
]

LATERALITY = ['unilateral', 'bilateral']

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path)

def initialize_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_completed TEXT NOT NULL,
            body_part TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            laterality TEXT NOT NULL,
            weight_left INTEGER,
            weight_right INTEGER,
            reps_left INTEGER,
            reps_right INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

def add_exercise(
    date_completed: str,
    body_part: str,
    exercise_name: str,
    laterality: str,
    weights: List[int],
    reps: List[int],
    db_path: Path = DB_PATH
) -> None:
    if body_part not in BODY_PARTS:
        raise ValueError(f"Invalid body part: {body_part}")
    if laterality not in LATERALITY:
        raise ValueError(f"Invalid laterality: {laterality}")

    if laterality == 'unilateral':
        if len(weights) != 1 or len(reps) != 1:
            raise ValueError('Unilateral exercises require one weight and one rep value')
        weight_left, weight_right = weights[0], None
        reps_left, reps_right = reps[0], None
    else:
        if len(weights) != 2 or len(reps) != 2:
            raise ValueError('Bilateral exercises require two weight and two rep values')
        weight_left, weight_right = weights
        reps_left, reps_right = reps

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO exercises (
            date_completed, body_part, exercise_name, laterality,
            weight_left, weight_right, reps_left, reps_right
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date_completed,
            body_part,
            exercise_name,
            laterality,
            weight_left,
            weight_right,
            reps_left,
            reps_right,
        )
    )
    conn.commit()
    conn.close()

def list_exercises(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM exercises ORDER BY date_completed')
    rows = cur.fetchall()
    conn.close()
    for row in rows:
        print(row)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Manage exercise log database.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    init_parser = subparsers.add_parser('init', help='Initialize the database')

    add_parser = subparsers.add_parser('add', help='Add an exercise entry')
    add_parser.add_argument('--date', required=True, help='Date completed (YYYY-MM-DD)')
    add_parser.add_argument('--body-part', required=True, choices=BODY_PARTS)
    add_parser.add_argument('--name', required=True, help='Exercise name')
    add_parser.add_argument('--laterality', required=True, choices=LATERALITY)
    add_parser.add_argument('--weight', required=True, nargs='+', type=int)
    add_parser.add_argument('--reps', required=True, nargs='+', type=int)

    list_parser = subparsers.add_parser('list', help='List all exercises')

    return parser.parse_args()

def main() -> None:
    args = parse_args()
    if args.command == 'init':
        initialize_db()
        print(f'Database initialized at {DB_PATH}')
    elif args.command == 'add':
        add_exercise(
            date_completed=args.date,
            body_part=args.body_part,
            exercise_name=args.name,
            laterality=args.laterality,
            weights=args.weight,
            reps=args.reps,
        )
        print('Exercise added.')
    elif args.command == 'list':
        list_exercises()

if __name__ == '__main__':
    main()
