"""
API endpoints for sending test emails and returning timestamps.
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic.networks import EmailStr

from app import LOGGER, models, schemas
from app.api import dependencies
from app.core.config import settings
from app.utils import send_test_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    response_model=schemas.Message,
    status_code=status.HTTP_201_CREATED,
    summary="Send a test email",
)
async def test_email(
    email_to: EmailStr,
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Sends a test email to the provided email address.

    **Needs superuser privileges.**
    """

    await LOGGER.info("Superuser initiated test email", email=email_to)
    await send_test_email(email_to=email_to)

    return {"message": "Test email sent"}


@router.get(
    "/start-time",
    response_model=schemas.Timestamp,
    summary="Returns the contest start time",
)
async def start_time() -> Any:
    """
    Returns the contest start time.
    """

    return schemas.Timestamp(timestamp=settings.EVENT_START_TIME)


@router.get(
    "/end-time",
    response_model=schemas.Timestamp,
    summary="Returns the contest end time",
)
async def end_time() -> Any:
    """
    Returns the contest end time.
    """

    return schemas.Timestamp(timestamp=settings.EVENT_END_TIME)
