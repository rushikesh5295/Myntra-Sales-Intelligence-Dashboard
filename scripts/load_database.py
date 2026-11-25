"""Step 2 - create the MySQL database/table and load the cleaned CSV into it.

Run from the project root:  python scripts/load_database.py
(MySQL must be running and the credentials in .env must be correct.)
"""

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.extensions import engine  # noqa: E402
from app.models import Base, Sale  # noqa: E402
from config import CLEANED_CSV, DB_NAME, get_server_url  # noqa: E402


def create_database() -> None:
    """Create the MySQL database if it does not exist yet."""
    server = create_engine(get_server_url(), isolation_level="AUTOCOMMIT")
    with server.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4"))
    server.dispose()


def load_data() -> None:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CLEANED_CSV}. Run scripts/clean_data.py first.")

    columns = [column.name for column in Sale.__table__.columns]
    df = pd.read_csv(CLEANED_CSV)

    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Cleaned CSV is missing columns: {sorted(missing)}")

    df = df[columns].copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"]).dt.date

    # Rebuild the table so the script can be re-run safely.
    Base.metadata.drop_all(engine, tables=[Sale.__table__])
    Base.metadata.create_all(engine, tables=[Sale.__table__])

    print(f"Loading {len(df):,} rows into MySQL ... (this can take a minute)")
    df.to_sql("sales", engine, if_exists="append", index=False, chunksize=5000)

    with engine.connect() as conn:
        total = conn.execute(select(func.count()).select_from(Sale)).scalar()
    print(f"Done. Rows in `{DB_NAME}.sales`: {total:,}")


if __name__ == "__main__":
    try:
        create_database()
        load_data()
    except SQLAlchemyError as exc:
        print("\nCould not connect to / write to MySQL:")
        print(exc)
        print("\nCheck that MySQL is running and DB_USER / DB_PASSWORD in .env are correct.")
        sys.exit(1)
