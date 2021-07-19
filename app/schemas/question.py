"""
Pydantic schemas for handling questions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class QuestionBase(BaseModel):
    """
    Pydantic question schema containing common attributes of all schemas.
    """

    content: bytes
    content_type: str


class QuestionCreate(QuestionBase):
    """
    Pydantic question schema containing attributes received via the API for creating a
    new question.
    """

    answer: str


class QuestionUpdate(BaseModel):
    """
    Pydantic question schema containing attributes received via the API for updating
    question details.
    """

    answer: Optional[str] = None


class QuestionInDBBase(QuestionBase):
    """
    Pydantic question schema containing common attributes of all schemas representing a
    question stored in the database.
    """

    id: Optional[int] = None

    class Config:  # pylint: disable=too-few-public-methods
        """
        Class used to control the behavior of pydantic for the parent class
        (`QuestionInDBBase`).

        `orm_mode` allows serializing and deserializing to and from ORM objects.
        """

        orm_mode = True


class Question(QuestionInDBBase):
    """
    Pydantic question schema containing attributes returned via the API.
    """


class QuestionAnswer(Question):
    """
    Pydantic question schema containing attributes returned via the API for superuser
    interaction only.
    """

    answer: str


class QuestionInDB(QuestionAnswer):
    """
    Pydantic question schema containing attributes for a question stored in the
    database.
    """

    updated_at: datetime
