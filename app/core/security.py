"""
Utility functions for handling access tokens and passwords.
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt  # type: ignore
from jose.constants import ALGORITHMS  # type: ignore
from passlib.context import CryptContext  # type: ignore

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


JWT_SIGNATURE_ALGORITHM = ALGORITHMS.HS256


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create an access token with the provided `subject` and an optional `expires_delta`
    duration.
    """

    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=JWT_SIGNATURE_ALGORITHM
    )

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plaintext password against stored password hash.
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Obtain password hash for provided plaintext password.
    """

    return pwd_context.hash(password)
