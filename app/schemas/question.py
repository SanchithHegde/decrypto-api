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

    answer: str


class QuestionInDBBase(BaseModel):
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


class Question(QuestionBase, QuestionInDBBase):
    """
    Pydantic question schema containing attributes returned via the API.
    """


class QuestionListItem(QuestionInDBBase, QuestionUpdate):
    """
    Pydantic question schema containing attributes returned via the API when a list of
    questions is returned.
    """


class QuestionAnswer(Question, QuestionUpdate):
    """
    Pydantic question schema containing attributes returned via the API for superuser
    interaction only.
    """


class QuestionInDB(QuestionAnswer):
    """
    Pydantic question schema containing attributes for a question stored in the
    database.
    """

    updated_at: datetime


class Answer(BaseModel):
    """
    Pydantic answer schema containing attributes received via the API for users to
    answer a particular question.
    """

    answer: str
