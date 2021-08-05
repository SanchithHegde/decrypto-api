# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from sqlalchemy.orm import Session

from app import crud
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.tests.utils.question import horse_image_contents, png_content_type
from app.tests.utils.utils import random_lower_string


def test_create_question(db_session: Session) -> None:
    answer = random_lower_string()
    content = horse_image_contents()
    question_in = QuestionCreate(
        answer=answer,
        content=content,
        content_type=png_content_type(),
    )
    question = crud.question.create(db_session, obj_in=question_in)

    assert question.answer == answer
    assert question.content_type == png_content_type()
    assert question.content == content


def test_get_question(db_session: Session) -> None:
    answer = random_lower_string()
    question_in = QuestionCreate(
        answer=answer,
        content=horse_image_contents(),
        content_type=png_content_type(),
    )
    question = crud.question.create(db_session, obj_in=question_in)

    assert question.id  # Required for mypy
    question_2 = crud.question.get(db_session, identifier=question.id)

    assert question_2
    assert question.content == question_2.content
    assert question.content_type == question_2.content_type
    assert question.answer == question_2.answer
    assert question.dict() == question_2.dict()


def test_update_question(db_session: Session) -> None:
    answer = random_lower_string()
    question_in = QuestionCreate(
        answer=answer,
        content=horse_image_contents(),
        content_type=png_content_type(),
    )
    question = crud.question.create(db_session, obj_in=question_in)

    new_answer = random_lower_string()
    question_in_update = QuestionUpdate(answer=new_answer)
    crud.question.update(
        db_session,
        db_obj=question,
        obj_in=question_in_update,
        use_jsonable_encoder=False,
    )

    assert question.id
    updated_question = crud.question.get(db_session, identifier=question.id)

    assert updated_question
    assert updated_question.content == question.content
    assert updated_question.content_type == question.content_type
    assert updated_question.answer == new_answer


def test_delete_question(db_session: Session) -> None:
    answer = random_lower_string()
    question_in = QuestionCreate(
        answer=answer,
        content=horse_image_contents(),
        content_type=png_content_type(),
    )
    question = crud.question.create(db_session, obj_in=question_in)

    assert question.id
    deleted_question = crud.question.remove(db_session, identifier=question.id)

    assert deleted_question.id == question.id
    assert deleted_question.answer == question.answer
    assert deleted_question.content_type == question.content_type
    assert deleted_question.content == question.content
    assert deleted_question.dict() == question.dict()

    result = crud.question.get(db_session, identifier=question.id)

    assert result is None
