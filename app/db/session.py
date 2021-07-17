"""
Provides an SQLAlchemy `Session` which can be used for accessing the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

assert settings.SQLALCHEMY_DATABASE_URI is not None

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
