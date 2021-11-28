"""
SQLAlchemy models for handling user operations.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, relationship

from app.db.base_class import Base
from app.utils import project_name_lowercase_no_spaces

if TYPE_CHECKING:  # pragma: no cover
    from app.models import Question


class User(Base):  # pylint: disable=too-few-public-methods
    """
    SQLAlchemy user model.
    """

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_superuser = Column(Boolean(), default=False)
    question_number = Column(Integer, nullable=False, default=1)
    question_number_updated_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )  # Used to sort users, when generating leaderboard
    rank = Column(Integer, nullable=False, default=0)

    # SQLAlchemy relationship.
    # This doesn't add an attribute/column to the table in the database, but provides an
    # attribute in the model instance whose value is populated (by SQLAlchemy) eagerly
    # (we can't use lazy loading with async SQLAlchemy dialects). The value is populated
    # by using the foreign key and performing a suitable JOIN operation.
    # In this case, we explicitly specify the foreign keys and the JOIN conditions that
    # SQLAlchemy should use to populate the value.
    question: Mapped["Question"] = relationship(
        "Question",
        secondary=f"{project_name_lowercase_no_spaces()}_questionorderitem",
        primaryjoin="User.question_number == QuestionOrderItem.question_number",
        secondaryjoin="QuestionOrderItem.question_id == foreign(Question.id)",
        lazy="selectin",
        uselist=False,
        viewonly=True,
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__} ("
            f"id: {self.id}, "
            f"full_name: {self.full_name}, "
            f"email: {self.email}, "
            f"is_superuser: {self.is_superuser}, "
            f"question_number: {self.question_number}, "
            f"rank: {self.rank}, "
            f"question: {repr(self.question)}"
            f")>"
        )

    # We are NOT setting a FOREIGN KEY constraint referencing
    # `QuestionOrderItem.question_number` as it causes inconsistencies in the situations
    # outlined below:
    # * Q: What would the question number of the first user created (the first superuser
    #      usually) be?
    #   A: To solve this, we can allow `question_number` to be NULL, but we'd have to
    #      add an extra condition check while serving a question to the user, to return
    #      the first question if `question_number` is NULL.
    #
    # * Q: What do we do when the `QuestionOrderItem` record that this refers to is
    #      updated/ What should we set ON UPDATE as?
    #   A: Since updating the `question_number` on the `QuestionOrderItem` instance can
    #      end up increasing or decreasing the user's "level" to the new value, we
    #      definitely don't want CASCADE. We can't set to NULL either, that would drop
    #      all affected users to level 1 and they'd have to start all over again.
    #
    # * Q: Same question with ON DELETE.
    #   A: We definitely don't want to drop `User` records, so we don't want CASCADE.
    #      Setting to NULL causes the same issue outlined above.
    #
    # * Q: What happens when a user reaches "the end"? The `question_number` would refer
    #      to say question 101, but question 101 does not exist in `QuestionOrderItem`,
    #      so the database wouldn't allow setting the value in this table to 101, to
    #      maintain consistency.
    #   A: When this happens, the user would end up seeing the last question over and
    #      over again, even if they got the answer for it right. (expected outcome)
