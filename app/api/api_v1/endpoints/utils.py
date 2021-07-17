"""
API endpoints for sending test emails.
"""

from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic.networks import EmailStr

from app import models, schemas
from app.api import dependencies
from app.utils import send_test_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    response_model=schemas.Message,
    status_code=status.HTTP_201_CREATED,
    summary="Send a test email",
)
def test_email(
    email_to: EmailStr,
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Sends a test email to the provided email address.

    **Needs superuser privileges.**
    """

    send_test_email(email_to=email_to)

    return {"message": "Test email sent"}
