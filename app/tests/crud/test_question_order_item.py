# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.schemas.question_order_item import (
    QuestionOrderItemCreate,
    QuestionOrderItemUpdate,
)
from app.tests.utils.question import create_random_question
from app.tests.utils.utils import random_int

pytestmark = pytest.mark.asyncio


async def test_create_question_order_item(db_session: AsyncSession) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.question_id == question_id
    assert question_order_item.question_number == question_number
    assert question_order_item.question.dict() == question.dict()


async def test_get_question_order_item(db_session: AsyncSession) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.id  # Required for mypy
    question_order_item_2 = await crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert question_order_item_2
    assert question_order_item.id == question_order_item_2.id
    assert question_order_item.question_id == question_order_item_2.question_id
    assert question_order_item.question_number == question_order_item_2.question_number
    assert question_order_item.dict() == question_order_item_2.dict()


async def test_update_question_order_item_question_id(db_session: AsyncSession) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    new_question = await create_random_question(db_session)
    new_question_id = new_question.id
    question_order_item_in_update = QuestionOrderItemUpdate(question_id=new_question_id)
    await crud.question_order_item.update(
        db_session,
        db_obj=question_order_item,
        obj_in=question_order_item_in_update,
        use_jsonable_encoder=False,
    )

    assert question_order_item.id
    updated_question_order_item = await crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert updated_question_order_item
    assert updated_question_order_item.id == updated_question_order_item.id
    assert updated_question_order_item.question_id == new_question_id
    assert (
        updated_question_order_item.question_number
        == question_order_item.question_number
    )


async def test_update_question_order_item_question_number(
    db_session: AsyncSession,
) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    new_question_number = random_int()
    question_order_item_in_update = QuestionOrderItemUpdate(
        question_number=new_question_number
    )
    await crud.question_order_item.update(
        db_session,
        db_obj=question_order_item,
        obj_in=question_order_item_in_update,
        use_jsonable_encoder=False,
    )

    assert question_order_item.id
    updated_question_order_item = await crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert updated_question_order_item
    assert updated_question_order_item.id == updated_question_order_item.id
    assert (
        updated_question_order_item.question_id
        == updated_question_order_item.question_id
    )
    assert updated_question_order_item.question_number == new_question_number


async def test_delete_question_order_item(db_session: AsyncSession) -> None:
    question = await create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.id
    deleted_question_order_item = await crud.question_order_item.remove(
        db_session, identifier=question_order_item.id
    )

    assert deleted_question_order_item.id == question_order_item.id
    assert deleted_question_order_item.question_id == question_order_item.question_id
    assert (
        deleted_question_order_item.question_number
        == question_order_item.question_number
    )
    assert deleted_question_order_item.dict() == question_order_item.dict()

    result = await crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert result is None
