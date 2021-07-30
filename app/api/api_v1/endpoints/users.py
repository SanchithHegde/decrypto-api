"""
API endpoints for user operations.
"""

import base64
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import dependencies
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User], summary="Obtain a list of users")
def read_users(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Obtain a list of users starting at offset `skip` and containing a maximum of `limit`
    number of instances.

    **Needs superuser privileges.**
    """

    users = crud.user.get_multi(db_session, skip=skip, limit=limit)

    return users


@router.post(
    "/", response_model=schemas.User, summary="Create a new user as a superuser"
)
def create_user(
    *,
    user_in: schemas.UserCreate,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Create a new user with the provided details.

    **Needs superuser privileges.**
    """

    user = crud.user.get_by_email(db_session, email=user_in.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email address already exists in the system.",
        )

    user = crud.user.create(db_session, obj_in=user_in)

    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )

    return user


@router.put("/me", response_model=schemas.User, summary="Update own user")
def update_user_me(
    *,
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    db_session: Session = Depends(dependencies.get_db_session),
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Update own user.
    """

    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)

    if password is not None:
        user_in.password = password

    if full_name is not None:
        user_in.full_name = full_name

    if email is not None:
        user_in.email = email

    user = crud.user.update(db_session, db_obj=current_user, obj_in=user_in)

    return user


@router.get(
    "/me", response_model=schemas.User, summary="Obtain the details of the user"
)
def read_user_me(
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Obtain the details of the user.
    """

    return current_user


@router.post(
    "/open",
    response_model=schemas.User,
    summary="Create a new user without the need to be logged in",
)
def create_user_open(
    *,
    full_name: str = Body(...),
    email: EmailStr = Body(...),
    password: str = Body(...),
    db_session: Session = Depends(dependencies.get_db_session),
) -> Any:
    """
    Create a new user without the need to be logged in.
    """

    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server",
        )

    user = crud.user.get_by_email(db_session, email=email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email address already exists in the system",
        )

    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db_session, obj_in=user_in)

    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )

    return user


@router.get(
    "/question",
    response_model=schemas.Question,
    responses={
        200: {
            "content": {"image/jpeg": {}, "image/png": {}},
        }
    },
    summary="Obtain the current question for the user",
)
def read_user_question(
    image: Optional[bool] = None,
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Obtain the current question for the user.

    If `image` is `true`, returns the image with the appropriate `Content-Type` header.
    """

    question = current_user.question

    if image:
        return Response(content=question.content, media_type=question.content_type)

    question.content = base64.b64encode(question.content)

    return question


@router.post(
    "/answer",
    response_model=schemas.Message,
    summary="Verify the answer provided by the user for the current question",
)
def verify_user_answer(
    answer_in: schemas.Answer,
    db_session: Session = Depends(dependencies.get_db_session),
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Verify the answer provided by the user for the current question.
    """

    question = current_user.question
    answer = answer_in.answer

    if answer != question.answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect answer",
        )

    # Update user's question number, and update ranks of all users
    assert current_user.question_number
    new_question_number = current_user.question_number + 1
    user_update = schemas.UserUpdate(question_number=new_question_number)
    crud.user.update(db_session, db_obj=current_user, obj_in=user_update)

    return {"message": "Correct answer!"}


@router.get(
    "/leaderboard",
    response_model=List[schemas.UserLeaderboard],
    summary="Obtain the leaderboard",
)
def read_leaderboard(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(dependencies.get_db_session),
) -> Any:
    """
    Obtain the leaderboard starting at offset `skip` and containing a maximum of `limit`
    number of instances.
    """

    leaderboard = crud.user.get_leaderboard(db_session, skip=skip, limit=limit)

    return leaderboard


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    summary="Obtain a user's details given the user ID",
)
def read_user_by_id(
    user_id: int,
    db_session: Session = Depends(dependencies.get_db_session),
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Obtain a user's details given the user ID.

    The behavior can be explained as follows:

    * If the user is not a superuser, they can only obtain their own details.
    * If the user is a superuser, they can obtain any user's details.
    """

    user = crud.user.get(db_session, identifier=user_id)

    if user == current_user:
        return user

    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    return user


@router.put(
    "/{user_id}",
    response_model=schemas.User,
    summary="Update a user's details given the user ID",
)
def update_user(
    *,
    user_id: int,
    user_in: schemas.UserUpdate,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Update a user's details given the user ID.

    **Needs superuser privileges.**
    """

    user = crud.user.get(db_session, identifier=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    user = crud.user.update(db_session, db_obj=user, obj_in=user_in)

    return user


@router.delete(
    "/{user_id}",
    response_model=schemas.Message,
    summary="Delete a user given the user ID",
)
def delete_user(
    *,
    user_id: int,
    db_session: Session = Depends(dependencies.get_db_session),
    _: models.User = Depends(dependencies.get_current_superuser),
) -> Any:
    """
    Delete a user given the user ID.

    **Needs superuser privileges.**
    """

    user = crud.user.get(db_session, identifier=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    user = crud.user.remove(db_session, identifier=user_id)

    return {"message": "User deleted successfully"}
