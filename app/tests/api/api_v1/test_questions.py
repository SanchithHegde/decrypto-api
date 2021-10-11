# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from typing import Dict

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.question import QuestionCreate
from app.tests.utils.question import (
    create_random_question,
    gif_content_type,
    horse_image_contents,
    jpg_content_type,
    png_content_type,
)
from app.tests.utils.utils import random_lower_string

pytestmark = pytest.mark.asyncio


async def test_create_question_accept_png(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"answer": random_lower_string()}
    files = {
        "image": (random_lower_string(), horse_image_contents(), png_content_type())
    }
    response = await client.post(
        f"{settings.API_V1_STR}/questions/",
        headers=superuser_token_headers,
        data=data,
        files=files,
    )

    assert 200 <= response.status_code < 300


async def test_create_question_accept_jpeg(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"answer": random_lower_string()}
    files = {
        "image": (random_lower_string(), horse_image_contents(), jpg_content_type())
    }
    response = await client.post(
        f"{settings.API_V1_STR}/questions/",
        headers=superuser_token_headers,
        data=data,
        files=files,
    )

    assert 200 <= response.status_code < 300


async def test_create_question_not_accept_gif(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    data = {"answer": random_lower_string()}
    files = {
        "image": (random_lower_string(), horse_image_contents(), gif_content_type())
    }
    response = await client.post(
        f"{settings.API_V1_STR}/questions/",
        headers=superuser_token_headers,
        data=data,
        files=files,
    )

    assert response.status_code == 400


async def test_create_question_new_answer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    answer = random_lower_string()
    data = {"answer": answer}
    files = {
        "image": (random_lower_string(), horse_image_contents(), png_content_type())
    }
    response = await client.post(
        f"{settings.API_V1_STR}/questions/",
        headers=superuser_token_headers,
        data=data,
        files=files,
    )

    assert 200 <= response.status_code < 300

    created_question = response.json()
    question = crud.question.get_by_answer(db_session, answer=answer)

    assert question
    assert "id" in created_question
    assert "answer" in created_question
    assert question.answer == created_question["answer"]


async def test_create_question_existing_answer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    answer = random_lower_string()
    question_in = QuestionCreate(
        answer=answer,
        content=horse_image_contents(),
        content_type=png_content_type(),
    )
    crud.question.create(db_session, obj_in=question_in)
    data = {"answer": answer}
    files = {
        "image": (random_lower_string(), horse_image_contents(), png_content_type())
    }
    response = await client.post(
        f"{settings.API_V1_STR}/questions/",
        headers=superuser_token_headers,
        data=data,
        files=files,
    )

    assert response.status_code == 400


async def test_get_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    response = await client.get(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300

    api_question = response.json()
    assert question.answer
    existing_question = crud.question.get_by_answer(db_session, answer=question.answer)

    assert existing_question
    assert existing_question.answer == api_question["answer"]


async def test_get_existing_question_image(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    params = {"image": True}
    response = await client.get(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
        params=params,
    )

    assert 200 <= response.status_code < 300

    content_type_header = "content-type"
    assert content_type_header in response.headers
    assert response.headers[content_type_header] == png_content_type()


async def test_get_not_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_id = -1
    response = await client.get(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404


async def test_retrieve_questions(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    create_random_question(db_session)
    create_random_question(db_session)
    create_random_question(db_session)

    response = await client.get(
        f"{settings.API_V1_STR}/questions/", headers=superuser_token_headers
    )
    all_questions = response.json()

    assert len(all_questions) > 1
    for item in all_questions:
        assert "answer" in item


async def test_update_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    new_answer = random_lower_string()
    data = {"answer": new_answer}
    response = await client.patch(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert 200 <= response.status_code < 300

    updated_question = response.json()

    assert updated_question
    assert "id" in updated_question
    assert "answer" in updated_question
    assert updated_question["answer"] == new_answer


async def test_update_not_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_id = -1
    new_answer = random_lower_string()
    data = {"answer": new_answer}
    response = await client.patch(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 404


async def test_update_existing_question_duplicate_answer(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    question = create_random_question(db_session)
    question2 = create_random_question(db_session)
    question_id = question.id
    new_answer = question2.answer
    data = {"answer": new_answer}
    response = await client.patch(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 400


async def test_delete_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str], db_session: Session
) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    response = await client.delete(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
    )

    assert 200 <= response.status_code < 300


async def test_delete_not_existing_question(
    client: AsyncClient, superuser_token_headers: Dict[str, str]
) -> None:
    question_id = -1
    response = await client.delete(
        f"{settings.API_V1_STR}/questions/{question_id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404
