#!/usr/bin/env python3
"""
Import exercise data from CSV file to SQLite database.
Handles CSV format with semicolon-separated values for weights and reps.
"""

import csv
import sqlite3
import argparse
import sys
from pathlib import Path
from datetime import datetime


def parse_date(date_str):
    """Parse date from various formats to YYYY-MM-DD."""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def validate_body_part(body_part):
    """Validate body part against known values."""
    valid_body_parts = [
        'Chest', 'Upper Back', 'Lower Back', 'Shoulders', 'Calves', 'Glutes', 'Core',
        'Biceps', 'Triceps', 'Rotator Cuff', 'Neck', 'Forearm', 'Hamstrings',
        'Quads', 'Traps', 'Tibia Dorsi', 'Knee', 'Hip', 'Legs'
    ]
    return body_part in valid_body_parts


def validate_laterality(laterality):
    """Validate laterality value."""
    return laterality.lower() in ['unilateral', 'bilateral']


def import_csv_to_database(csv_path, db_path, skip_duplicates=True):
    """
    Import CSV data to SQLite database.
    """
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure the database table exists
    cursor.execute('''
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
    ''')
    
    with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row_num, row in enumerate(reader, 2):  # Start at 2 since header is row 1
            try:
                # Parse and validate data
                date_completed = parse_date(row['date_completed'])
                body_part = row['body_part'].strip()
                exercise_name = row['exercise_name'].strip()
                laterality = row['laterality'].strip().lower()
                sets = int(row['sets'])
                
                # Validate required fields
                if not validate_body_part(body_part):
                    print(f"Warning row {row_num}: Unknown body part '{body_part}', proceeding anyway")
                
                if not validate_laterality(laterality):
                    print(f"Error row {row_num}: Invalid laterality '{laterality}', skipping")
                    error_count += 1
                    continue
                
                if sets <= 0:
                    print(f"Error row {row_num}: Invalid sets value '{sets}', skipping")
                    error_count += 1
                    continue
                
                # Handle weight and rep fields (may be empty or contain semicolon-separated values)
                # Convert semicolons to commas for database storage
                weight_left = row['weight_left'].strip().replace(';', ',') if row['weight_left'].strip() else None
                reps_left = row['reps_left'].strip().replace(';', ',') if row['reps_left'].strip() else None
                
                # For unilateral exercises, set right-side fields to NULL
                if laterality == 'unilateral':
                    weight_right = None
                    reps_right = None
                else:
                    weight_right = row['weight_right'].strip().replace(';', ',') if row['weight_right'].strip() else None
                    reps_right = row['reps_right'].strip().replace(';', ',') if row['reps_right'].strip() else None
                
                # Check for duplicates if requested
                if skip_duplicates:
                    cursor.execute('''
                        SELECT COUNT(*) FROM exercises 
                        WHERE date_completed = ? AND exercise_name = ? AND 
                              weight_left = ? AND weight_right = ? AND 
                              reps_left = ? AND reps_right = ?
                    ''', (date_completed, exercise_name, weight_left, weight_right, reps_left, reps_right))
                    
                    if cursor.fetchone()[0] > 0:
                        print(f"Skipping row {row_num}: Duplicate entry for {exercise_name} on {date_completed}")
                        skipped_count += 1
                        continue
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO exercises (
                        date_completed, body_part, exercise_name, laterality, sets,
                        weight_left, weight_right, reps_left, reps_right
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date_completed, body_part, exercise_name, laterality, sets,
                      weight_left, weight_right, reps_left, reps_right))
                
                imported_count += 1
                
            except Exception as e:
                print(f"Error processing row {row_num}: {e}")
                error_count += 1
                continue
    
    conn.commit()
    conn.close()
    
    return imported_count, skipped_count, error_count


def main():
    parser = argparse.ArgumentParser(description='Import exercise data from CSV to SQLite database')
    parser.add_argument('csv_file', help='Path to CSV file to import')
    parser.add_argument('--database', '-d', default='exercise_log.db', help='SQLite database path (default: exercise_log.db)')
    parser.add_argument('--allow-duplicates', action='store_true', help='Allow duplicate entries (default: skip duplicates)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without actually importing')
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: CSV file {csv_path} not found")
        return 1
    
    db_path = Path(args.database)
    
    print(f"CSV file: {csv_path}")
    print(f"Database: {db_path}")
    print(f"Skip duplicates: {not args.allow_duplicates}")
    print()
    
    if args.dry_run:
        print("DRY RUN - No data will be imported")
        # Read CSV and show what would be imported
        with open(csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                count += 1
                print(f"Row {count}: {row['date_completed']} - {row['exercise_name']}")
            print(f"\nWould import {count} rows")
        return 0
    
    try:
        imported, skipped, errors = import_csv_to_database(
            csv_path, 
            db_path, 
            skip_duplicates=not args.allow_duplicates
        )
        
        print(f"Import complete:")
        print(f"  Imported: {imported} rows")
        print(f"  Skipped:  {skipped} rows (duplicates)")
        print(f"  Errors:   {errors} rows")
        
        if errors > 0:
            print(f"\nSome rows had errors. Check output above for details.")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Import failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())