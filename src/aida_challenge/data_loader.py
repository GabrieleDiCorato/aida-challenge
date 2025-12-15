"""Data loading utilities."""

import duckdb
from pathlib import Path


def load_raw_data():
    """Load CSV files into DuckDB database."""

    # Project root
    root = Path(__file__).parent.parent.parent
    db_path = root / "data" / "aida_challenge.duckdb"

    print(f"Creating database at: {db_path}")

    # Connect to DuckDB (creates file if doesn't exist)
    con = duckdb.connect(str(db_path))

    # Define data sources
    data_files = {
        "clienti": "data/raw/clienti.csv",
        "polizze": "data/raw/polizze.csv",
        "sinistri": "data/raw/sinistri.csv",
        "reclami": "data/raw/reclami.csv",
        "abitazioni": "data/raw/abitazioni.csv",
        "interazioni_clienti": "data/raw/interazioni_clienti.csv",
        "competitor_prodotti": "data/raw/competitor_prodotti.csv",
    }

    print("\nLoading CSV files into DuckDB...")

    # Load each CSV into DuckDB
    for table_name, file_path in data_files.items():
        full_path = root / file_path
        if not full_path.exists():
            print(f"WARNING: File not found: {full_path}")
            continue

        # Drop table if exists to recreate
        con.execute(f"DROP TABLE IF EXISTS {table_name}")

        con.execute(
            f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{full_path}')
        """
        )

        # Get row count
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"OK Loaded {table_name}: {count:,} rows")

    print("\n" + "=" * 60)
    print("Tables in database:")
    print("=" * 60)
    tables = con.execute("SHOW TABLES").df()
    print(tables.to_string(index=False))

    con.close()
    print(f"\n[OK] Database created successfully at: {db_path}")
    return 0  # Success exit code
