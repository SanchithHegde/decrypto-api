# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = response.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    return headers


def create_random_user(db_session: Session) -> User:
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(
        username=email, email=email, password=password, full_name=full_name
    )
    user = crud.user.create(db_session=db_session, obj_in=user_in)

    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db_session: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with the provided email.

    If the user doesn't exist, it is created first.
    """

    password = random_lower_string()
    user = crud.user.get_by_email(db_session, email=email)

    if not user:
        full_name = random_lower_string()
        user_in_create = UserCreate(
            username=email, email=email, password=password, full_name=full_name
        )
        user = crud.user.create(db_session, obj_in=user_in_create)

    else:
        user_in_update = UserUpdate(password=password)
        user = crud.user.update(db_session, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
