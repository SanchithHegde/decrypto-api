# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.question import png_content_type
from app.tests.utils.question_order_item import create_random_question_order_item
from app.tests.utils.user import authentication_token_from_email, create_random_user
from app.tests.utils.utils import random_email, random_int, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_get_users_superuser_me(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    response = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


async def test_get_users_normal_user_me(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    response = await client.get(
        f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


async def test_create_user_new_email(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    response = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    created_user = response.json()
    user = await crud.user.get_by_email(db_session, email=username)

    assert user
    assert user.email == created_user["email"]


async def test_get_existing_user(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await create_random_user(db_session)
    user_id = user.id
    response = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300

    api_user = response.json()
    assert user.email
    existing_user = await crud.user.get_by_email(db_session, email=user.email)

    assert existing_user
    assert existing_user.email == api_user["email"]


async def test_get_not_existing_user(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    response = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404


async def test_get_current_user_normal_user(
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await crud.user.get_by_email(db_session, email=settings.EMAIL_TEST_USER)
    assert user
    user_id = user.id
    response = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=normal_user_token_headers,
    )
    current_user = response.json()

    assert current_user
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


async def test_get_another_user_normal_user(
    client: AsyncClient,
    normal_user_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await crud.user.get_by_email(db_session, email=settings.EMAIL_TEST_USER)
    assert user and user.id
    user_id = user.id - 1  # Any user ID other than current user
    response = await client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 400


async def test_create_user_existing_username(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=username, password=password, full_name=full_name)
    await crud.user.create(db_session, obj_in=user_in)
    data = {"email": username, "password": password, "full_name": full_name}
    response = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = response.json()

    assert response.status_code == 400
    assert "_id" not in created_user


async def test_create_user_by_normal_user(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    response = await client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_retrieve_users(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    await create_random_user(db_session)
    await create_random_user(db_session)
    await create_random_user(db_session)

    response = await client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    all_users = response.json()

    assert len(all_users) > 1
    for user in all_users:
        assert "email" in user


async def test_update_user_normal_user_me(
    client: AsyncClient, normal_user_token_headers: Dict[str, str]
) -> None:
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
    }
    response = await client.put(
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
async def test_create_user_open(client: AsyncClient) -> None:
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
    }
    response = await client.post(
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
async def test_create_user_open_existing_username(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=username, password=password, full_name=full_name)
    await crud.user.create(db_session, obj_in=user_in)
    data = {"email": username, "password": password, "full_name": full_name}
    response = await client.post(
        f"{settings.API_V1_STR}/users/open",
        json=data,
    )

    assert response.status_code == 400


async def test_update_user_existing_user(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await create_random_user(db_session)
    data = {
        "email": random_email(),
        "full_name": random_lower_string(),
        "is_superuser": True,
    }
    response = await client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    api_user = response.json()

    assert api_user
    assert api_user["is_superuser"]
    assert api_user["email"] == data["email"]
    assert api_user["full_name"] == data["full_name"]


async def test_update_user_not_existing_user(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    data = {
        "email": random_email(),
        "password": random_lower_string(),
        "full_name": random_lower_string(),
        "is_superuser": True,
    }
    response = await client.put(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


async def test_delete_user_existing_user(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    user = await create_random_user(db_session)
    user_id = user.id
    response = await client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300


async def test_delete_user_not_existing_user(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    user_id = -1
    response = await client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404


async def test_get_question(client: AsyncClient, db_session: AsyncSession) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_number = question_order_item.question_number
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email  # Required for mypy
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )

    response = await client.get(
        f"{settings.API_V1_STR}/users/question", headers=normal_user_token_headers
    )

    assert 200 <= response.status_code < 300

    question_data = response.json()

    assert "content" in question_data
    assert "content_type" in question_data


async def test_get_question_image(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_number = question_order_item.question_number
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email  # Required for mypy
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )
    params = {"image": True}

    response = await client.get(
        f"{settings.API_V1_STR}/users/question",
        headers=normal_user_token_headers,
        params=params,
    )

    assert 200 <= response.status_code < 300

    content_type_header = "content-type"
    assert content_type_header in response.headers
    assert response.headers[content_type_header] == png_content_type()


async def test_get_question_redirect_if_none(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    question_number = random_int()
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email  # Required for mypy
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )

    response = await client.get(
        f"{settings.API_V1_STR}/users/question",
        headers=normal_user_token_headers,
        follow_redirects=False,
    )

    assert response.status_code == 307


async def test_get_question_redirect_if_none_allow_redirects(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    question_number = random_int()
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email  # Required for mypy
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )

    response = await client.get(
        f"{settings.API_V1_STR}/users/question",
        headers=normal_user_token_headers,
        follow_redirects=True,
    )

    assert 200 <= response.status_code < 300

    message_json = response.json()

    assert "message" in message_json


async def test_verify_answer_correct_answer(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_number = question_order_item.question_number
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )
    answer = question_order_item.question.answer
    data = {"answer": answer}

    response = await client.post(
        f"{settings.API_V1_STR}/users/answer",
        headers=normal_user_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    assert user.id
    assert user.rank
    old_rank = user.rank
    updated_user = await crud.user.get(db_session, identifier=user.id)
    await db_session.refresh(updated_user)

    assert updated_user
    assert updated_user.question_number
    assert updated_user.rank
    assert question_number
    assert updated_user.question_number == question_number + 1
    assert updated_user.rank >= old_rank


async def test_verify_answer_incorrect_answer(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_number = question_order_item.question_number
    user = await create_random_user(db_session)
    user_in_update = UserUpdate(question_number=question_number)
    user = await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)
    assert user.email
    normal_user_token_headers = await authentication_token_from_email(
        client=client, email=user.email, db_session=db_session
    )
    answer = random_lower_string()
    data = {"answer": answer}

    response = await client.post(
        f"{settings.API_V1_STR}/users/answer",
        headers=normal_user_token_headers,
        json=data,
    )

    assert response.status_code == 400

    assert user.id
    assert user.rank
    old_rank = user.rank
    unmodified_user = await crud.user.get(db_session, identifier=user.id)

    assert unmodified_user
    assert unmodified_user.question_number
    assert unmodified_user.rank
    assert question_number
    assert unmodified_user.question_number == question_number
    assert unmodified_user.rank == old_rank


async def test_retrieve_leaderboard(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    await create_random_user(db_session)
    await create_random_user(db_session)
    await create_random_user(db_session)

    response = await client.get(f"{settings.API_V1_STR}/users/leaderboard")
    all_users = response.json()

    assert len(all_users) > 1
    for user in all_users:
        assert "question_number" in user
        assert "rank" in user
        assert "full_name" in user
