#!/usr/bin/env python3
"""
Add body_part column to exercise CSV file by looking up exercise names in SQLite database.
Inserts the body_part column between date_completed and exercise_name.
"""

import csv
import sqlite3
import argparse
import sys
from pathlib import Path


def get_body_part_lookup(db_path):
    """
    Create a lookup dictionary mapping exercise names to body parts from the database.
    Uses the first occurrence of each exercise name found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to get unique exercise names and their body parts (first occurrence)
    query = """
    SELECT exercise_name, body_part
    FROM exercises
    GROUP BY exercise_name
    ORDER BY id
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    # Create lookup dictionary
    lookup = {}
    for exercise_name, body_part in results:
        if exercise_name not in lookup:  # Use first occurrence only
            lookup[exercise_name] = body_part
    
    return lookup


def add_body_part_column(input_csv, output_csv, db_path):
    """
    Add body_part column to CSV file between date_completed and exercise_name.
    """
    # Get body part lookup from database
    body_part_lookup = get_body_part_lookup(db_path)
    
    with open(input_csv, 'r', newline='', encoding='utf-8-sig') as infile, \
         open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Process header row
        header = next(reader)
        
        # Find the index of date_completed and exercise_name
        try:
            date_idx = header.index('date_completed')
            exercise_idx = header.index('exercise_name')
        except ValueError as e:
            print(f"Error: Required column not found in CSV: {e}")
            return False
        
        # Create new header with body_part inserted after date_completed
        new_header = header.copy()
        new_header.insert(date_idx + 1, 'body_part')
        writer.writerow(new_header)
        
        # Process data rows
        processed_count = 0
        found_count = 0
        
        for row in reader:
            if len(row) <= exercise_idx:
                # Skip empty or malformed rows
                continue
                
            exercise_name = row[exercise_idx]
            
            # Look up body part
            body_part = body_part_lookup.get(exercise_name, 'Unknown')
            if body_part != 'Unknown':
                found_count += 1
            
            # Insert body_part after date_completed
            new_row = row.copy()
            new_row.insert(date_idx + 1, body_part)
            writer.writerow(new_row)
            
            processed_count += 1
    
    print(f"Processed {processed_count} rows")
    print(f"Found body parts for {found_count} exercises")
    print(f"Unknown body parts: {processed_count - found_count}")
    
    # Show which exercises weren't found
    if processed_count - found_count > 0:
        print("\nExercises not found in database:")
        with open(input_csv, 'r', newline='', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            unknown_exercises = set()
            for row in reader:
                exercise_name = row['exercise_name']
                if exercise_name not in body_part_lookup:
                    unknown_exercises.add(exercise_name)
            
            for exercise in sorted(unknown_exercises):
                print(f"  - {exercise}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Add body_part column to exercise CSV')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('--output', '-o', help='Output CSV file path (default: adds "_with_body_part" to input name)')
    parser.add_argument('--database', '-d', default='exercise_log.db', help='SQLite database path (default: exercise_log.db)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"Error: Input file {input_path} not found")
        return 1
    
    db_path = Path(args.database)
    if not db_path.exists():
        print(f"Error: Database file {db_path} not found")
        return 1
    
    # Generate output filename if not specified
    if args.output:
        output_path = Path(args.output)
    else:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_with_body_part{suffix}"
    
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Database: {db_path}")
    print()
    
    success = add_body_part_column(input_path, output_path, db_path)
    if success:
        print(f"\nSuccess! Updated CSV saved to {output_path}")
        return 0
    else:
        print("\nFailed to process CSV file")
        return 1


if __name__ == '__main__':
    sys.exit(main())