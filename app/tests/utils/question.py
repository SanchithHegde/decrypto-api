# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models.question import Question
from app.schemas.question import QuestionCreate
from app.tests.utils.utils import random_lower_string


def png_content_type() -> str:
    return "image/png"


def jpg_content_type() -> str:
    return "image/jpeg"


def gif_content_type() -> str:
    return "image/gif"


def horse_image_contents() -> bytes:
    with open("app/tests/img/horse.png", "rb") as file:
        contents = file.read()

    return contents


async def create_random_question(db_session: AsyncSession) -> Question:
    answer = random_lower_string()
    content = horse_image_contents()
    question_in = QuestionCreate(
        answer=answer,
        content=content,
        content_type=png_content_type(),
    )
    question = await crud.question.create(db_session, obj_in=question_in)

    return question
