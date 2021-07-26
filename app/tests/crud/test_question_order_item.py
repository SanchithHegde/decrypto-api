# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from sqlalchemy.orm import Session

from app import crud
from app.schemas.question_order_item import (
    QuestionOrderItemCreate,
    QuestionOrderItemUpdate,
)
from app.tests.utils.question import create_random_question
from app.tests.utils.utils import random_int


def test_create_question_order_item(db_session: Session) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.question_id == question_id
    assert question_order_item.question_number == question_number
    assert question_order_item.question.dict() == question.dict()


def test_get_question_order_item(db_session: Session) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.id  # Required for mypy
    question_order_item_2 = crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert question_order_item_2
    assert question_order_item.id == question_order_item_2.id
    assert question_order_item.question_id == question_order_item_2.question_id
    assert question_order_item.question_number == question_order_item_2.question_number
    assert question_order_item.dict() == question_order_item_2.dict()


def test_update_question_order_item_question_id(db_session: Session) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    new_question = create_random_question(db_session)
    new_question_id = new_question.id
    question_order_item_in_update = QuestionOrderItemUpdate(question_id=new_question_id)
    crud.question_order_item.update(
        db_session, db_obj=question_order_item, obj_in=question_order_item_in_update
    )

    assert question_order_item.id
    updated_question_order_item = crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert updated_question_order_item
    assert updated_question_order_item.id == updated_question_order_item.id
    assert updated_question_order_item.question_id == new_question_id
    assert (
        updated_question_order_item.question_number
        == question_order_item.question_number
    )


def test_update_question_order_item_question_number(db_session: Session) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    new_question_number = random_int()
    question_order_item_in_update = QuestionOrderItemUpdate(
        question_number=new_question_number
    )
    crud.question_order_item.update(
        db_session, db_obj=question_order_item, obj_in=question_order_item_in_update
    )

    assert question_order_item.id
    updated_question_order_item = crud.question_order_item.get(
        db_session, identifier=question_order_item.id
    )

    assert updated_question_order_item
    assert updated_question_order_item.id == updated_question_order_item.id
    assert (
        updated_question_order_item.question_id
        == updated_question_order_item.question_id
    )
    assert updated_question_order_item.question_number == new_question_number


def test_delete_question_order_item(db_session: Session) -> None:
    question = create_random_question(db_session)
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    assert question_order_item.id
    deleted_question_order_item = crud.question_order_item.remove(
        db_session, identifier=question_order_item.id
    )

    assert deleted_question_order_item.id == question_order_item.id
    assert deleted_question_order_item.question_id == question_order_item.question_id
    assert (
        deleted_question_order_item.question_number
        == question_order_item.question_number
    )
    assert deleted_question_order_item.dict() == question_order_item.dict()

    result = crud.question_order_item.get(db_session, identifier=question_order_item.id)

    assert result is None
