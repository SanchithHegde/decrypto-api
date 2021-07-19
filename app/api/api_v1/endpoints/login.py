"""
API endpoints for handling login access tokens, testing access tokens and password
recovery.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import dependencies
from app.core import security
from app.core.config import settings
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post(
    "/login/access-token",
    response_model=schemas.Token,
    summary="Obtain a login access token",
)
def login_access_token(
    db_session: Session = Depends(dependencies.get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Obtain an OAuth2 compatible access token, which can be used for future requests.
    """

    user = crud.user.authenticate(
        db_session, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post(
    "/login/test-token",
    response_model=schemas.User,
    summary="Test the obtained access token",
)
def test_token(
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Test the obtained access token.

    If the access token sent with the request is correct, returns the user's details.
    """

    return current_user


@router.post(
    "/password-recovery/{email}",
    response_model=schemas.Message,
    summary="Send a password recovery email",
)
def recover_password(
    email: str, db_session: Session = Depends(dependencies.get_db_session)
) -> Any:
    """
    Send a password recovery email to the provided email address.
    """

    user = crud.user.get_by_email(db_session, email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )

    assert user.email is not None

    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return {"message": "Password recovery email sent"}


@router.post(
    "/reset-password/",
    response_model=schemas.Message,
    summary="Reset a user's password",
)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db_session: Session = Depends(dependencies.get_db_session),
) -> Any:
    """
    Reset a user's password with the provided password.

    The token would be included as part of the "reset password" link sent by email to
    the user.
    """

    email = verify_password_reset_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = crud.user.get_by_email(db_session, email=email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system.",
        )

    current_user_data = jsonable_encoder(user)
    user_in = schemas.UserUpdate(**current_user_data)
    user_in.password = new_password
    user = crud.user.update(db_session, db_obj=user, obj_in=user_in)

    return {"message": "Password updated successfully"}
