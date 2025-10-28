#!/usr/bin/env python3
"""
Read CSV data from clipboard and save it to a CSV file.
Bypasses the need to manually paste into Excel.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def get_clipboard_content():
    """Get text content from clipboard."""
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        print("Error: pyperclip module not found.")
        print("Install it with: pip install pyperclip")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading from clipboard: {e}")
        sys.exit(1)


def clipboard_to_csv(output_file=None, show_preview=False):
    """
    Read CSV data from clipboard and save to a file.

    Args:
        output_file: Path to output CSV file. If None, generates a filename with timestamp.
        show_preview: If True, shows first few lines before saving.

    Returns:
        Path to the created CSV file
    """
    # Get clipboard content
    clipboard_text = get_clipboard_content()

    if not clipboard_text or not clipboard_text.strip():
        print("Error: Clipboard is empty")
        return None

    # Show preview if requested
    if show_preview:
        lines = clipboard_text.strip().split('\n')
        preview_lines = lines[:5]
        print("Preview of clipboard content:")
        print("-" * 60)
        for line in preview_lines:
            print(line)
        if len(lines) > 5:
            print(f"... and {len(lines) - 5} more lines")
        print("-" * 60)
        print()

    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"workout_data_{timestamp}.csv"

    output_path = Path(output_file)

    # Check if file already exists
    if output_path.exists():
        response = input(f"File {output_path} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled")
            return None

    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            # Ensure content ends with newline
            content = clipboard_text.strip() + '\n'
            f.write(content)

        print(f"Success! CSV data saved to: {output_path}")

        # Count lines (minus header)
        line_count = len(clipboard_text.strip().split('\n')) - 1
        print(f"Saved {line_count} data rows")

        return output_path

    except Exception as e:
        print(f"Error writing to file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Read CSV data from clipboard and save to a file',
        epilog='Example: python clipboard_to_csv.py -o workout_2025-01-15.csv'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output CSV filename (default: auto-generated with timestamp)'
    )
    parser.add_argument(
        '-p', '--preview',
        action='store_true',
        help='Show preview of clipboard content before saving'
    )
    parser.add_argument(
        '--import-to-db',
        action='store_true',
        help='Automatically import the CSV to the database after creating it'
    )
    parser.add_argument(
        '--database',
        default='exercise_log.db',
        help='Database path for import (default: exercise_log.db)'
    )

    args = parser.parse_args()

    # Create CSV from clipboard
    csv_path = clipboard_to_csv(args.output, args.preview)

    if csv_path is None:
        return 1

    # Optionally import to database
    if args.import_to_db:
        try:
            from import_csv_to_db import import_csv_to_database

            print(f"\nImporting to database: {args.database}")
            imported, skipped, errors = import_csv_to_database(
                csv_path,
                args.database,
                skip_duplicates=True
            )

            print(f"Import complete:")
            print(f"  Imported: {imported} rows")
            print(f"  Skipped:  {skipped} rows (duplicates)")
            print(f"  Errors:   {errors} rows")

            if errors > 0:
                return 1

        except ImportError:
            print("\nWarning: Could not import to database (import_csv_to_db module not found)")
        except Exception as e:
            print(f"\nError importing to database: {e}")
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
