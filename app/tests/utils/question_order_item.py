# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models.question_order_item import QuestionOrderItem
from app.schemas.question_order_item import QuestionOrderItemCreate
from app.tests.utils.question import create_random_question
from app.tests.utils.utils import random_int


async def create_random_question_order_item(
    db_session: AsyncSession,
) -> QuestionOrderItem:
    question = await create_random_question(db_session)
    assert question.id  # Required for mypy
    question_id = question.id
    question_number = random_int()
    question_order_item_in = QuestionOrderItemCreate(
        question_id=question_id, question_number=question_number
    )
    question_order_item = await crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    return question_order_item
