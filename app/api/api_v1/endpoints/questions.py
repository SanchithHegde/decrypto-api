"""
API endpoints for question operations.
"""

import base64
from typing import Any, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app import LOGGER, crud, models, schemas
from app.api import dependencies

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get(
    "/",
    response_model=List[schemas.QuestionListItem],
    summary="Obtain a list of questions",
)
async def read_questions(
    skip: int = 0,
    limit: int = 100,
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Obtain a list of questions starting at offset `skip` and containing a maximum of
    `limit` number of instances.

    **Needs superuser privileges.**
    """

    await LOGGER.info("Superuser listed questions", skip=skip, limit=limit)
    questions = await crud.question.get_multi(db_session, skip=skip, limit=limit)

    return questions


@router.post(
    "/",
    response_model=schemas.QuestionListItem,
    summary="Add a new question",
)
async def create_question(
    *,
    answer: str = Form(...),
    image: UploadFile = Depends(dependencies.get_image),
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Create a new question with the provided details.

    **Needs superuser privileges.**
    """

    question = await crud.question.get_by_answer(db_session, answer=answer)

    if question:
        await LOGGER.error("Question with answer already exists", answer=answer)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The question with this answer already exists in the system",
        )

    question_data = {
        "content": await image.read(),
        "content_type": image.content_type,
        "answer": answer,
    }
    question_in = schemas.QuestionCreate(**question_data)
    question = await crud.question.create(db_session, obj_in=question_in)
    await LOGGER.info("Superuser created new question", question=question)

    return question


@router.get(
    "/{question_id}",
    response_model=schemas.QuestionAnswer,
    responses={
        200: {
            "content": {"image/jpeg": {}, "image/png": {}},
        }
    },
    summary="Obtain a questions's details given the question ID",
)
async def read_question_by_id(
    question_id: int,
    image: Optional[bool] = None,
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Obtain a question's details given the question ID.

    If `image` is `true`, returns the image with the appropriate `Content-Type` header.

    **Needs superuser privileges.**
    """

    question = await crud.question.get(db_session, identifier=question_id)

    if not question:
        await LOGGER.error("Question does not exist", question_id=question_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The question with this question ID does not exist in the system",
        )

    assert question.content is not None

    await LOGGER.info("Superuser accessed question by ID", question=question)

    # Return image directly with appropriate `Content-Type` header
    if image:
        return Response(content=question.content, media_type=question.content_type)

    # Base64 encode image and return response as JSON
    question.content = base64.b64encode(question.content)

    return question


# Using PATCH since we're only updating the answer, or in other words, applying a
# partial modification to a resource.
# Reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
@router.patch(
    "/{question_id}",
    response_model=schemas.QuestionListItem,
    summary="Update a question's details given the question ID",
)
async def update_question(
    *,
    question_id: int,
    question_in: schemas.QuestionUpdate,
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Update a question's details given the question ID.

    **Needs superuser privileges.**
    """

    question = await crud.question.get(db_session, identifier=question_id)

    if not question:
        await LOGGER.error("Question does not exist", question_id=question_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The question with this question ID does not exist in the system",
        )

    assert question_in.answer is not None
    duplicate_answer = await crud.question.get_by_answer(
        db_session, answer=question_in.answer
    )

    if duplicate_answer:
        await LOGGER.error(
            "Question with answer already exists", answer=question_in.answer
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The question with this answer already exists in the system",
        )

    await LOGGER.info(
        "Superuser initiated answer update",
        question=question,
        answer=question_in.answer,
    )
    question = await crud.question.update(
        db_session, db_obj=question, obj_in=question_in, use_jsonable_encoder=False
    )
    await LOGGER.info("Superuser updated question's answer by ID", question=question)

    return question


@router.delete(
    "/{question_id}",
    response_model=schemas.Message,
    summary="Delete a questions given the question ID",
)
async def delete_question(
    question_id: int,
    db_session: AsyncSession = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Delete a question given the question ID.

    **Needs superuser privileges.**
    """

    question = await crud.question.get(db_session, identifier=question_id)

    if not question:
        await LOGGER.error("Question does not exist", question_id=question_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The question with this question ID does not exist in the system",
        )

    await LOGGER.info("Superuser initiated question deletion", question=question)
    await crud.question.remove(db_session, identifier=question_id)
    await LOGGER.info("Superuser deleted question by ID", question=question)

    return {"message": "Question deleted successfully"}
