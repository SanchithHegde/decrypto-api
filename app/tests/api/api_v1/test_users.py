# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    created_user = response.json()
    user = crud.user.get_by_email(db_session, email=username)

    assert user
    assert user.email == created_user["email"]


def test_get_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    user = create_random_user(db_session)
    user_id = user.id
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300

    api_user = response.json()
    assert user.email
    existing_user = crud.user.get_by_email(db_session, email=user.email)

    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_not_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404


def test_get_current_user_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db_session: Session
) -> None:
    user = crud.user.get_by_email(db_session, email=settings.EMAIL_TEST_USER)
    assert user
    user_id = user.id
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=normal_user_token_headers,
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_get_another_user_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str], db_session: Session
) -> None:
    user = crud.user.get_by_email(db_session, email=settings.EMAIL_TEST_USER)
    assert user and user.id
    user_id = user.id - 1  # Any user ID other than current user
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 400


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=username, password=password, full_name=full_name)
    crud.user.create(db_session, obj_in=user_in)
    data = {"email": username, "password": password, "full_name": full_name}
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = response.json()

    assert response.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 400


def test_retrieve_users(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    create_random_user(db_session)
    create_random_user(db_session)
    create_random_user(db_session)

    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    all_users = response.json()

    assert len(all_users) > 1
    for item in all_users:
        assert "email" in item


def test_update_user_normal_user_me(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
    }
    response = client.put(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == data["email"]
    assert current_user["full_name"] == data["full_name"]


@pytest.mark.skipif(
    not settings.USERS_OPEN_REGISTRATION, reason="Open user registration disabled"
)
def test_create_user_open(client: TestClient) -> None:
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/open",
        json=data,
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == data["email"]
    assert current_user["full_name"] == data["full_name"]


@pytest.mark.skipif(
    not settings.USERS_OPEN_REGISTRATION, reason="Open user registration disabled"
)
def test_create_user_open_existing_username(
    client: TestClient, db_session: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=username, password=password, full_name=full_name)
    crud.user.create(db_session, obj_in=user_in)
    data = {"email": username, "password": password, "full_name": full_name}
    response = client.post(
        f"{settings.API_V1_STR}/users/open",
        json=data,
    )

    assert response.status_code == 400


def test_update_user_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    user = create_random_user(db_session)
    data = {
        "email": random_email(),
        "full_name": random_lower_string(),
        "is_superuser": True,
    }
    response = client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    api_user = response.json()

    assert api_user
    assert api_user["is_superuser"]
    assert api_user["email"] == data["email"]
    assert api_user["full_name"] == data["full_name"]


def test_update_user_not_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
        "is_superuser": True,
    }
    response = client.put(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


def test_delete_user_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    user = create_random_user(db_session)
    user_id = user.id
    response = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300


def test_delete_user_not_existing_user(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    response = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404
