"""
API endpoints for handling login access tokens, testing access tokens and password
recovery.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import LOGGER, crud, models, schemas
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
async def login_access_token(
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Obtain an OAuth2 compatible access token, which can be used for future requests.
    """

    user = await crud.user.authenticate(
        db_session, email=form_data.username, password=form_data.password
    )

    if not user:
        await LOGGER.error(
            "Incorrect email address or password", email=form_data.username
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email address or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    await LOGGER.info("User logged in", user=user)

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
async def test_token(
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Test the obtained access token.

    If the access token sent with the request is correct, returns the user's details.
    """

    await LOGGER.info("User tested their access token")

    return current_user


@router.post(
    "/password-recovery/{email}",
    response_model=schemas.Message,
    summary="Send a password recovery email",
)
async def recover_password(
    email: str, db_session: AsyncSession = Depends(dependencies.get_db_session)
) -> Any:
    """
    Send a password recovery email to the provided email address.
    """

    user = await crud.user.get_by_email(db_session, email=email)

    if not user:
        await LOGGER.error("User not found", email=email)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email address does not exist in the system.",
        )

    assert user.email is not None

    await LOGGER.info("User initiated password recovery", user=user)
    password_reset_token = await generate_password_reset_token(email=email)
    await send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return {"message": "Password recovery email sent"}


@router.post(
    "/reset-password/",
    response_model=schemas.Message,
    summary="Reset a user's password",
)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db_session: AsyncSession = Depends(dependencies.get_db_session),
) -> Any:
    """
    Reset a user's password with the provided password.

    The token would be included as part of the "reset password" link sent by email to
    the user.
    """

    email = await verify_password_reset_token(token)

    if not email:
        await LOGGER.error("Invalid token")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = await crud.user.get_by_email(db_session, email=email)

    if not user:
        await LOGGER.error("User not found", email=email)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email address does not exist in the system.",
        )

    await LOGGER.info("Resetting password for user", user=user)
    current_user_data = jsonable_encoder(user)
    user_in = schemas.UserUpdate(**current_user_data)
    user_in.password = new_password
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in)
    await LOGGER.info("Password for user updated", user=user)

    return {"message": "Password updated successfully"}
