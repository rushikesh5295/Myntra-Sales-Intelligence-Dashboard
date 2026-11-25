"""Central configuration for the Myntra Sales Intelligence dashboard.

Database credentials are read from the `.env` file in the project root so that
no password is hard-coded in the source code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

# Dataset locations (used by the scripts/ folder)
RAW_CSV = BASE_DIR / "data" / "raw" / "Myntra_Dataset.csv"
CLEANED_CSV = BASE_DIR / "data" / "processed" / "myntra_sales_cleaned.csv"

# Name of the MySQL database and table
DB_NAME = os.getenv("DB_NAME", "myntra_sales")


def get_server_url() -> URL:
    """SQLAlchemy URL for the MySQL *server* (no database selected)."""
    return URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
    )


def get_database_url() -> URL:
    """SQLAlchemy URL for the project database."""
    return get_server_url().set(database=DB_NAME)
