"""Database engine and session factory (created once, shared by the app)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_database_url

# pool_pre_ping re-opens connections that MySQL closed after being idle.
engine = create_engine(get_database_url(), pool_pre_ping=True, pool_recycle=1800)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
