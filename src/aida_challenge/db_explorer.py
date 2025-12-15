"""Database explorer utilities."""

import duckdb
from pathlib import Path


def explore_db():
    """Launch DuckDB UI explorer in browser."""
    root = Path(__file__).parent.parent.parent
    db_path = root / "data" / "aida_challenge.duckdb"

    if not db_path.exists():
        print(f"ERROR: Database not found at: {db_path}")
        print("Run 'uv run load-raw-data' first to create the database.")
        return 1

    print(f"Opening DuckDB UI for: {db_path}")
    print("The browser should open automatically...")
    print("Press Ctrl+C to stop the server when done.\n")

    try:
        con = duckdb.connect(str(db_path))
        con.execute("CALL start_ui()")

        # Keep the script running to keep the UI server alive
        import time

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDuckDB UI server stopped.")
        return 0
    except Exception as e:
        print(f"\nERROR: Failed to start DuckDB UI: {e}")
        return 1

    return 0
