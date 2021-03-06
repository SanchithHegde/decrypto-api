# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.config import settings
from app.tests.utils.question import create_random_question
from app.tests.utils.question_order_item import create_random_question_order_item
from app.tests.utils.utils import random_int

pytestmark = pytest.mark.asyncio


async def test_create_question_order_item(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question = await create_random_question(db_session)
    assert question.id  # Required for mypy
    question_id = question.id
    question_number = random_int()
    data = {"question_id": question_id, "question_number": question_number}
    response = await client.post(
        f"{settings.API_V1_STR}/questions_order/",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    created_item = response.json()
    question_order_item1 = await crud.question_order_item.get_by_question_id(
        db_session, question_id=question_id
    )
    question_order_item2 = await crud.question_order_item.get_by_question_number(
        db_session, question_number=question_number
    )

    assert question_order_item1
    assert question_order_item2

    assert "question_id" in created_item
    assert "question_number" in created_item
    assert created_item["question_id"] == question_id
    assert created_item["question_number"] == question_number
    assert question_order_item1.dict() == question_order_item2.dict()


async def test_create_question_order_item_existing_question_id(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_id = question_order_item.question_id
    question_number = random_int()
    data = {"question_id": question_id, "question_number": question_number}
    response = await client.post(
        f"{settings.API_V1_STR}/questions_order/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_create_question_order_item_existing_question_number(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_order_item = await create_random_question_order_item(db_session)
    question_number = question_order_item.question_number
    data = {"question_id": question_id, "question_number": question_number}
    response = await client.post(
        f"{settings.API_V1_STR}/questions_order/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_create_question_order_item_not_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_id = -1
    question_number = random_int()
    data = {"question_id": question_id, "question_number": question_number}
    response = await client.post(
        f"{settings.API_V1_STR}/questions_order/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


async def test_get_existing_question_order_item(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id
    response = await client.get(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300

    api_question_order_item = response.json()
    assert question_order_item.question_id
    existing_question_order_item = await crud.question_order_item.get_by_question_id(
        db_session, question_id=question_order_item.question_id
    )

    assert existing_question_order_item
    assert (
        existing_question_order_item.question_id
        == api_question_order_item["question_id"]
    )
    assert (
        existing_question_order_item.question_number
        == api_question_order_item["question_number"]
    )


async def test_get_not_existing_question_order_item(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_order_item_id = -1
    response = await client.get(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404


async def test_retrieve_question_order_items(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    await create_random_question_order_item(db_session)
    await create_random_question_order_item(db_session)
    await create_random_question_order_item(db_session)

    response = await client.get(
        f"{settings.API_V1_STR}/questions_order/", headers=superuser_token_headers
    )
    all_items = response.json()

    assert len(all_items) > 1
    for item in all_items:
        assert "question_id" in item
        assert "question_number" in item


async def test_update_existing_question_order_item_new_question_number(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id
    new_question_number = random_int()
    data = {"question_number": new_question_number}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    updated_question_order_item = response.json()

    assert updated_question_order_item
    assert "question_id" in updated_question_order_item
    assert "question_number" in updated_question_order_item
    assert updated_question_order_item["question_number"] == new_question_number


async def test_update_existing_question_order_item_new_question_id(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id
    question = await create_random_question(db_session)
    new_question_id = question.id
    data = {"question_id": new_question_id}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    updated_question_order_item = response.json()

    assert updated_question_order_item
    assert "question_id" in updated_question_order_item
    assert "question_number" in updated_question_order_item
    assert updated_question_order_item["question_id"] == new_question_id


async def test_update_existing_question_order_item_not_existing_question_id(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id
    new_question_id = -1
    data = {"question_id": new_question_id}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


async def test_update_not_existing_question_order_item(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_order_item_id = -1
    new_question_number = random_int()
    data = {"question_number": new_question_number}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


async def test_update_existing_question_order_item_duplicate_question_number(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id

    question_order_item2 = await create_random_question_order_item(db_session)
    new_question_number = question_order_item2.question_number

    data = {"question_number": new_question_number}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_update_existing_question_order_item_duplicate_question_id(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id

    question_order_item2 = await create_random_question_order_item(db_session)
    new_question_id = question_order_item2.question_id

    data = {"question_id": new_question_id}
    response = await client.put(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_delete_existing_question_order_item(
    client: AsyncClient,
    superuser_token_headers: Dict[str, str],
    db_session: AsyncSession,
) -> None:
    question_order_item = await create_random_question_order_item(db_session)
    question_order_item_id = question_order_item.id
    response = await client.delete(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300


async def test_delete_not_existing_question_order_item(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_order_item_id = -1
    response = await client.delete(
        f"{settings.API_V1_STR}/questions_order/{question_order_item_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404
