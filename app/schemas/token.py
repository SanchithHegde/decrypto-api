"""
Pydantic schemas for auth tokens.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Pydantic token schema.

    When the client requests for an access token, the response is serialized into this
    schema.
    """

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Pydantic token payload schema.

    This schema is used to deserialize the access token and obtain the user ID from it.
    The `sub` attribute typically contains the user ID after deserializing the access
    token.
    """

    sub: Optional[int] = None
