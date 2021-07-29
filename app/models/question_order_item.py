"""
SQLAlchemy models for handling the order of questions.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, relationship

from app.core.config import settings
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models import Question


class QuestionOrderItem(Base):  # pylint: disable=too-few-public-methods
    """
    SQLAlchemy model associating a question with a question number.
    """

    id = Column(Integer, primary_key=True, index=True)
    question_number = Column(Integer, unique=True, index=True, nullable=False)
    question_id = Column(
        Integer,
        ForeignKey(
            f"{settings.PROJECT_NAME.strip().lower().replace(' ', '')}_question.id",
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    question: Mapped["Question"] = relationship(
        "Question", uselist=False, viewonly=True
    )
