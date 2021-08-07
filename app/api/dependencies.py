"""
Dependencies used by FastAPI for its dependency injection system.
"""

from typing import AsyncGenerator, Generator

from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt  # type: ignore
from pydantic import ValidationError
from sqlalchemy.orm import Session
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app import LOGGER, crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db_session() -> Generator:
    """
    Provides a database session instance.
    """

    try:
        db_session = SessionLocal()
        yield db_session

    finally:
        db_session.close()


async def get_current_user(
    db_session: Session = Depends(get_db_session), token: str = Depends(reusable_oauth2)
) -> AsyncGenerator[models.User, None]:
    """
    Provides the current logged in user.

    Returns an `HTTPException` if credential validation failed or user does not exist in
    database.
    """

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.JWT_SIGNATURE_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)

    except (jwt.JWTError, ValidationError):
        await LOGGER.error("Could not validate credentials")

        raise HTTPException(  # pylint: disable=raise-missing-from
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    assert token_data.sub is not None

    user = crud.user.get(db_session, identifier=token_data.sub)
    if not user:
        await LOGGER.error("User not found")

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Include the user in every log record until the response is delivered by including
    # it in `structlog`'s context.
    bind_contextvars(user=user)

    yield user

    # Remove the user from `structlog`'s context.
    unbind_contextvars("user")


async def get_current_superuser(
    current_user: models.User = Depends(get_current_user),
) -> AsyncGenerator[models.User, None]:
    """
    Provides the current logged in superuser.

    Returns an `HTTPException` if the user does not have sufficient privileges.
    """

    if not crud.user.is_superuser(current_user):
        await LOGGER.error("The user doesn't have enough privileges")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )

    # Include the superuser in every log record until the response is delivered by
    # including it in `structlog`'s context.
    unbind_contextvars("user")
    bind_contextvars(superuser=current_user)

    yield current_user

    # Remove the superuser from `structlog`'s context.
    unbind_contextvars("superuser")


async def get_image(image: UploadFile = File(...)) -> UploadFile:
    """
    Provides the file if it has a MIME type corresponding to an image.

    Returns an `HTTPException` if the MIME type does not correspond to an image.
    """

    # Accept only JPEG and PNG images
    # Reference: https://en.wikipedia.org/wiki/Media_type
    image_mime_types = ["image/jpeg", "image/png"]

    if image.content_type not in image_mime_types:
        await LOGGER.error(
            "File rejected", filename=image.filename, content_type=image.content_type
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a JPEG or a PNG image",
        )

    return image
