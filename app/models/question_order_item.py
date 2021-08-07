"""
SQLAlchemy models for handling the order of questions.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from app.utils import project_name_lowercase_no_spaces

if TYPE_CHECKING:  # pragma: no cover
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
            f"{project_name_lowercase_no_spaces()}_question.id",  # table_name.attribute
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # SQLAlchemy relationship.
    # This doesn't add an attribute/column to the table in the database, but provides an
    # attribute in the model instance whose value is populated (by SQLAlchemy) when it
    # is first accessed. The value is populated by using the foreign key and performing
    # a suitable JOIN operation.
    # In this case, `question` is an instance of `Question` which has the same `id` as
    # the `question_id` in `self`.
    question: Mapped["Question"] = relationship(
        "Question", uselist=False, viewonly=True
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__} ("
            f"id: {self.id}, "
            f"question_number: {self.question_number}, "
            f"question_id: {self.question_id}, "
            f"question: {repr(self.question)}"
            f")>"
        )
