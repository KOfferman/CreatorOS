from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import DatabaseSettings


def get_engine():
    settings = DatabaseSettings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
