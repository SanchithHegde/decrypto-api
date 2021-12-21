# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


async def user_authentication_headers(
    *, client: AsyncClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    response = await client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response_json = response.json()
    auth_token = response_json["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


async def create_random_user(db_session: AsyncSession) -> User:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        username=username,
        password=password,
    )
    user = await crud.user.create(db_session=db_session, obj_in=user_in)

    return user


async def authentication_token_from_email(
    *, client: AsyncClient, email: str, db_session: AsyncSession
) -> Dict[str, str]:
    """
    Return a valid token for the user with the provided email.

    If the user doesn't exist, it is created first.
    """

    password = random_lower_string()
    user = await crud.user.get_by_email(db_session, email=email)

    if not user:
        full_name = random_lower_string()
        username = random_lower_string()
        user_in_create = UserCreate(
            username=username, email=email, password=password, full_name=full_name
        )
        user = await crud.user.create(db_session, obj_in=user_in_create)

    else:
        user_in_update = UserUpdate(password=password)
        user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)

    return await user_authentication_headers(
        client=client, email=email, password=password
    )
