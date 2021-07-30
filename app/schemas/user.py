"""
Pydantic schemas for user operations.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Pydantic user schema containing common attributes of all schemas.
    """

    email: Optional[EmailStr] = None
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Pydantic user schema containing attributes received via the API for creating a new
    user.
    """

    email: EmailStr
    password: str
    full_name: str


class UserUpdate(UserBase):
    """
    Pydantic user schema containing attributes received via the API for updating user
    details.
    """

    password: Optional[str] = None
    question_number: Optional[int] = None


class UserInDBBase(UserBase):
    """
    Pydantic user schema containing common attributes of all schemas representing a user
    stored in the database.
    """

    id: Optional[int] = None
    question_number: Optional[int] = None

    class Config:  # pylint: disable=too-few-public-methods
        """
        Class used to control the behavior of pydantic for the parent class
        (`UserInDBBase`).

        `orm_mode` allows serializing and deserializing to and from ORM objects.
        """

        orm_mode = True


class User(UserInDBBase):
    """
    Pydantic user schema containing attributes returned via the API.
    """


class UserInDB(UserInDBBase):
    """
    Pydantic user schema containing attributes for a user stored in the database.
    """

    hashed_password: str
