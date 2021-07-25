"""
API endpoints for question order item operations.
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import dependencies

router = APIRouter(prefix="/questions_order", tags=["questions_order"])


@router.get(
    "/",
    response_model=List[schemas.QuestionOrderItem],
    summary="Obtain a list of question numbers and their corresponding questions.",
)
def read_question_order_items(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Obtain a list of question numbers and their corresponding questions, starting at
    offset `skip` and containing a maximum of `limit` number of instances.

    **Needs superuser privileges.**
    """

    question_order_items = crud.question_order_item.get_multi(
        db_session, skip=skip, limit=limit
    )

    return question_order_items


@router.post(
    "/",
    response_model=schemas.QuestionOrderItem,
    summary="Associate a question with a question number",
)
def create_question_order_item(
    *,
    question_order_item_in: schemas.QuestionOrderItemCreate,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Associate a question with a question number.

    **Needs superuser privileges.**
    """

    question = crud.question.get(
        db_session, identifier=question_order_item_in.question_id
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The question with this question ID does not exist in the system",
        )

    assert question_order_item_in.question_id is not None
    assert question_order_item_in.question_number is not None

    # Question number should be unique
    question_order_item = crud.question_order_item.get_by_question_number(
        db_session, question_number=question_order_item_in.question_number
    )

    if question_order_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Another question is already associated with the question number",
        )

    # Question ID should be unique
    question_order_item = crud.question_order_item.get_by_question_id(
        db_session, question_id=question_order_item_in.question_id
    )

    if question_order_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This question is already associated with a question number",
        )

    question_order_item = crud.question_order_item.create(
        db_session, obj_in=question_order_item_in
    )

    return question_order_item


@router.get(
    "/{question_order_item_id}",
    response_model=schemas.QuestionOrderItem,
    summary=(
        "Obtain the details about a question number and its associated question, "
        "given the ID of their association"
    ),
)
def read_question_order_item_by_id(
    question_order_item_id: int,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Obtain the details about a question and its associated question number, given the ID
    of their association.

    **Needs superuser privileges.**
    """

    question_order_item = crud.question_order_item.get(
        db_session, identifier=question_order_item_id
    )

    if not question_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The association of a question and a question number with this ID "
                "does not exist in the system"
            ),
        )

    return question_order_item


@router.put(
    "/{question_order_item_id}",
    response_model=schemas.QuestionOrderItem,
    summary=(
        "Update the details about a question number and its associated question, "
        "given the ID"
    ),
)
async def update_question_order_item(
    *,
    question_order_item_id: int,
    question_order_item_in: schemas.QuestionOrderItemUpdate,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Update the details about a question number and its associated question, given the
    ID.

    **Needs superuser privileges.**
    """

    question_order_item = crud.question_order_item.get(
        db_session, identifier=question_order_item_id
    )

    if not question_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The association of a question and a question number with this ID "
                "does not exist in the system"
            ),
        )

    if question_order_item_in.question_id:
        question = crud.question.get(
            db_session, identifier=question_order_item_in.question_id
        )

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The question with this question ID does not exist in the system",
            )

        # Question ID should be unique
        duplicate_question = crud.question_order_item.get_by_question_id(
            db_session, question_id=question_order_item_in.question_id
        )

        if duplicate_question and duplicate_question != question_order_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This question is already associated with a question number",
            )

    if question_order_item_in.question_number:
        # Question number should be unique
        duplicate_question_number = crud.question_order_item.get_by_question_number(
            db_session, question_number=question_order_item_in.question_number
        )

        if (
            duplicate_question_number
            and duplicate_question_number != question_order_item
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another question is already associated with the question number",
            )

    question_order_item = crud.question_order_item.update(
        db_session, db_obj=question_order_item, obj_in=question_order_item_in
    )

    return question_order_item


@router.delete(
    "/{question_order_item_id}",
    response_model=schemas.Message,
    summary=(
        "Delete the details about a question number and its associated question, "
        "given the ID"
    ),
)
def delete_question_order_item(
    question_order_item_id: int,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Delete the details about a question number and its associated question, given the
    ID.

    **Needs superuser privileges.**
    """

    question_order_item = crud.question_order_item.get(
        db_session, identifier=question_order_item_id
    )

    if not question_order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "The association of a question and a question number with this ID "
                "does not exist in the system"
            ),
        )

    crud.question_order_item.remove(db_session, identifier=question_order_item_id)

    return {
        "message": (
            "The question and its associated question number have been deleted "
            "successfully"
        )
    }
