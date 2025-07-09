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
            sets INTEGER NOT NULL,
            weight_left TEXT,
            weight_right TEXT,
            reps_left TEXT,
            reps_right TEXT
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
    sets: int,
    weights: Optional[List[int]] = None,
    reps: Optional[List[int]] = None,
    weights_left: Optional[List[int]] = None,
    weights_right: Optional[List[int]] = None,
    reps_left: Optional[List[int]] = None,
    reps_right: Optional[List[int]] = None,
    db_path: Path = DB_PATH
) -> None:
    if body_part not in BODY_PARTS:
        raise ValueError(f"Invalid body part: {body_part}")
    if laterality not in LATERALITY:
        raise ValueError(f"Invalid laterality: {laterality}")

    if sets <= 0:
        raise ValueError('Sets must be a positive integer')

    if laterality == 'unilateral':
        if weights is None or reps is None:
            raise ValueError('Unilateral exercises require --weight and --reps')
        if len(weights) != sets or len(reps) != sets:
            raise ValueError('Number of weight and rep values must equal sets')
        weight_left = ','.join(map(str, weights))
        weight_right = None
        reps_left = ','.join(map(str, reps))
        reps_right = None
    else:
        for arg, name in [
            (weights_left, 'weight-left'),
            (weights_right, 'weight-right'),
            (reps_left, 'reps-left'),
            (reps_right, 'reps-right'),
        ]:
            if arg is None:
                raise ValueError(f'Bilateral exercises require --{name}')
            if len(arg) != sets:
                raise ValueError(f'--{name} must have {sets} values')

        weight_left = ','.join(map(str, weights_left))
        weight_right = ','.join(map(str, weights_right))
        reps_left = ','.join(map(str, reps_left))
        reps_right = ','.join(map(str, reps_right))

    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO exercises (
            date_completed, body_part, exercise_name, laterality, sets,
            weight_left, weight_right, reps_left, reps_right
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            date_completed,
            body_part,
            exercise_name,
            laterality,
            sets,
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
    add_parser.add_argument('--sets', required=True, type=int)

    add_parser.add_argument('--weight', nargs='+', type=int)
    add_parser.add_argument('--reps', nargs='+', type=int)

    add_parser.add_argument('--weight-left', nargs='+', type=int)
    add_parser.add_argument('--weight-right', nargs='+', type=int)
    add_parser.add_argument('--reps-left', nargs='+', type=int)
    add_parser.add_argument('--reps-right', nargs='+', type=int)

    list_parser = subparsers.add_parser('list', help='List all exercises')

    return parser.parse_args()

def main() -> None:
    args = parse_args()
    if args.command == 'init':
        initialize_db()
        print(f'Database initialized at {DB_PATH}')
    elif args.command == 'add':
        add_kwargs = dict(
            date_completed=args.date,
            body_part=args.body_part,
            exercise_name=args.name,
            laterality=args.laterality,
            sets=args.sets,
        )
        if args.laterality == 'unilateral':
            add_kwargs.update(weights=args.weight, reps=args.reps)
        else:
            add_kwargs.update(
                weights_left=args.weight_left,
                weights_right=args.weight_right,
                reps_left=args.reps_left,
                reps_right=args.reps_right,
            )
        add_exercise(**add_kwargs)
        print('Exercise added.')
    elif args.command == 'list':
        list_exercises()

if __name__ == '__main__':
    main()
