"""
SQLAlchemy models for handling user operations.
"""

from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):  # pylint: disable=too-few-public-methods
    """
    SQLAlchemy user model.
    """

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean(), default=False)
