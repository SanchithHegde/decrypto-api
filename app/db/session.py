"""
Provides an SQLAlchemy `Session` which can be used for accessing the database.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

assert settings.SQLALCHEMY_DATABASE_URI is not None

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, future=True
)
SessionLocal = sessionmaker(
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    future=True,
)
