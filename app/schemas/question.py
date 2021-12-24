"""
Pydantic schemas for handling questions.
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


def process_answer(answer: str) -> str:
    """
    Converts answers to lowercase and removes any non-alphanumeric characters.
    """

    return re.sub(r"[^a-z0-9]", "", answer.lower())


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

    # Validators
    _process_answer = validator("answer", allow_reuse=True)(process_answer)


class QuestionUpdate(BaseModel):
    """
    Pydantic question schema containing attributes received via the API for updating
    question details.
    """

    answer: str

    # Validators
    _process_answer = validator("answer", allow_reuse=True)(process_answer)


class QuestionInDBBase(BaseModel):
    """
    Pydantic question schema containing common attributes of all schemas representing a
    question stored in the database.
    """

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

    id: Optional[int] = None


class QuestionAnswer(QuestionBase, QuestionListItem):
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

    # Validators
    _process_answer = validator("answer", allow_reuse=True)(process_answer)
