"""
SQLAlchemy models for handling questions.
"""

from sqlalchemy import Column, DateTime, Integer, LargeBinary, String, func

from app.db.base_class import Base


class Question(Base):  # pylint: disable=too-few-public-methods
    """
    SQLAlchemy question model.
    """

    id = Column(Integer, primary_key=True, index=True)
    answer = Column(String, unique=True, index=True, nullable=False)
    content = Column(LargeBinary, nullable=False)  # PostgreSQL's BYTEA type
    content_type = Column(String, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
