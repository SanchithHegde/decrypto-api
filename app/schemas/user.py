"""
Pydantic schemas for user operations.
"""

import re
from datetime import datetime
from typing import Optional

import pydantic
from pydantic import BaseModel, ConstrainedStr, EmailStr


class Username(ConstrainedStr):
    """
    Pydantic username schema, only to return a more user-friendly error message.
    """

    strip_whitespace = True
    min_length = 5
    max_length = 32
    regex = re.compile(r"^[a-zA-Z]\w{4,31}$")

    @classmethod
    def validate(cls, value: str) -> str:
        """
        Custom validation function to return a more user-friendly error message.
        """

        try:
            super(Username, cls).validate(value)

        except pydantic.errors.StrRegexError as error:
            error_msg = (
                "Invalid username: "
                "Must be 5-32 characters long, "
                "can contain only alphabets, digits and underscores, "
                "and must begin with an alphabet."
            )
            raise ValueError(error_msg) from error

        return value


class UserBase(BaseModel):
    """
    Pydantic user schema containing common attributes of all schemas.
    """

    username: Optional[Username] = None


class UserCreate(UserBase):
    """
    Pydantic user schema containing attributes received via the API for creating a new
    user.
    """

    full_name: str
    email: EmailStr
    username: Username
    password: str
    is_superuser: bool = False


class UserUpdate(UserBase):
    """
    Pydantic user schema containing attributes received via the API for updating user
    details.
    """

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    question_number: Optional[int] = None
    is_superuser: bool = False


class UserInDBBase(UserBase):
    """
    Pydantic user schema containing common attributes of all schemas representing a user
    stored in the database.
    """

    question_number: Optional[int] = None
    rank: Optional[int] = None

    class Config:  # pylint: disable=too-few-public-methods
        """
        Class used to control the behavior of pydantic for the parent class
        (`UserInDBBase`).

        * `anystr_strip_whitespace` strips leading and trailing whitespace for str and
        byte types.
        * `orm_mode` allows serializing and deserializing to and from ORM objects.
        """

        anystr_strip_whitespace = True
        orm_mode = True


class UserLeaderboard(UserInDBBase):
    """
    Pydantic user schema containing attributes returned via the API when the leaderboard
    is accessed.
    """


class User(UserInDBBase):
    """
    Pydantic user schema containing attributes returned via the API.
    """

    id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_superuser: bool = False


class UserInDB(User):
    """
    Pydantic user schema containing attributes for a user stored in the database.
    """

    hashed_password: str
    question_number_updated_at: datetime
