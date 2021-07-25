"""
Pydantic schemas for handling the order of questions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.question import QuestionListItem


class QuestionOrderItemBase(BaseModel):
    """
    Pydantic question order item schema containing common attributes of all schemas.
    """

    question_number: Optional[int]
    question_id: Optional[int]


class QuestionOrderItemCreate(QuestionOrderItemBase):
    """
    Pydantic question order item schema containing attributes received via the API for
    creating a new question order item.
    """

    question_number: int
    question_id: int


class QuestionOrderItemUpdate(QuestionOrderItemBase):
    """
    Pydantic question order item schema containing attributes received via the API for
    updating question order item details.
    """


class QuestionOrderItemInDBBase(QuestionOrderItemCreate):
    """
    Pydantic question order item schema containing common attributes of all schemas
    representing a question order item stored in the database.
    """

    id: Optional[int] = None

    class Config:  # pylint: disable=too-few-public-methods
        """
        Class used to control the behavior of pydantic for the parent class
        (`QuestionOrderItemInDBBase`).

        `orm_mode` allows serializing and deserializing to and from ORM objects.
        """

        orm_mode = True


class QuestionOrderItem(QuestionOrderItemInDBBase):
    """
    Pydantic question order item schema containing attributes returned via the API.
    """

    question: QuestionListItem


class QuestionOrderItemInDB(QuestionOrderItemInDBBase):
    """
    Pydantic question order item schema containing attributes for a question order item
    stored in the database.
    """

    updated_at: datetime
