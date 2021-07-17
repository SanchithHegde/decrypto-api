"""
Pydantic schemas for status messages.
"""

from pydantic import BaseModel


class Message(BaseModel):
    """
    Pydantic message schema.
    """

    message: str
