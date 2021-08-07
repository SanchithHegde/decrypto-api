"""
API endpoints for user operations.
"""

import base64
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from structlog.contextvars import bind_contextvars, unbind_contextvars

from app import LOGGER, crud, models, schemas
from app.api import dependencies
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User], summary="Obtain a list of users")
async def read_users(
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

    await LOGGER.info("Superuser listed users", skip=skip, limit=limit)
    users = crud.user.get_multi(db_session, skip=skip, limit=limit)

    return users


@router.post(
    "/", response_model=schemas.User, summary="Create a new user as a superuser"
)
async def create_user(
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
        await LOGGER.error("User with email already exists", email=user_in.email)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email address already exists in the system.",
        )

    user = crud.user.create(db_session, obj_in=user_in)
    await LOGGER.info("Superuser created new user", user=user)

    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )

    return user


@router.put("/me", response_model=schemas.User, summary="Update own user")
async def update_user_me(
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

    temp_password = "[REDACTED]" if password is not None else None
    await LOGGER.info(
        "User initiated an update of their own details",
        email=email,
        full_name=full_name,
        password=temp_password,
    )
    user = crud.user.update(db_session, db_obj=current_user, obj_in=user_in)
    await LOGGER.info("User updated their own details", user=user)

    return user


@router.get(
    "/me", response_model=schemas.User, summary="Obtain the details of the user"
)
async def read_user_me(
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Obtain the details of the user.
    """

    await LOGGER.info("User accessed their own details")

    return current_user


@router.post(
    "/open",
    response_model=schemas.User,
    summary="Create a new user without the need to be logged in",
)
async def create_user_open(
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
        await LOGGER.error("Open user registration is not allowed")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server",
        )

    await LOGGER.info(
        "New user registration initiated",
        email=email,
        full_name=full_name,
        password="[REDACTED]",
    )
    user = crud.user.get_by_email(db_session, email=email)

    if user:
        await LOGGER.error("User with email already exists", email=email)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email address already exists in the system",
        )

    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db_session, obj_in=user_in)
    await LOGGER.info("New user registered", user=user)

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
        },
        307: {"description": "User completed answering all questions"},
    },
    summary="Obtain the current question for the user",
)
async def read_user_question(
    image: Optional[bool] = None,
    current_user: models.User = Depends(dependencies.get_current_user),
) -> Any:
    """
    Obtain the current question for the user.

    If `image` is `true`, returns the image with the appropriate `Content-Type` header.

    Redirects with a `307` status code if the user completed answering all questions.
    """

    await LOGGER.info("User accessed their question")
    question = current_user.question

    if question is None:
        await LOGGER.info("Question not found, redirecting to 'game_over'")

        return RedirectResponse(f"{settings.API_V1_STR}{router.prefix}/game_over")

    if image:
        return Response(content=question.content, media_type=question.content_type)

    question.content = base64.b64encode(question.content)

    return question


@router.post(
    "/answer",
    response_model=schemas.Message,
    summary="Verify the answer provided by the user for the current question",
)
async def verify_user_answer(
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
        await LOGGER.info("User provided incorrect answer", answer=answer)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect answer",
        )

    await LOGGER.info("User provided correct answer", answer=answer)

    # Update user's question number, and update ranks of all users
    assert current_user.question_number
    new_question_number = current_user.question_number + 1
    user_update = schemas.UserUpdate(question_number=new_question_number)
    user = crud.user.update(db_session, db_obj=current_user, obj_in=user_update)
    await LOGGER.info(
        "User advanced to next question", question_number=new_question_number, user=user
    )

    return {"message": "Correct answer!"}


@router.get(
    "/leaderboard",
    response_model=List[schemas.UserLeaderboard],
    summary="Obtain the leaderboard",
)
async def read_leaderboard(
    skip: int = 0,
    limit: int = 100,
    db_session: Session = Depends(dependencies.get_db_session),
) -> Any:
    """
    Obtain the leaderboard starting at offset `skip` and containing a maximum of `limit`
    number of instances.

    **NOTE:** All superusers are excluded from the leaderboard.
    """

    await LOGGER.debug("Leaderboard was accessed", skip=skip, limit=limit)
    leaderboard = crud.user.get_leaderboard(db_session, skip=skip, limit=limit)

    return leaderboard


@router.get(
    "/game_over",
    response_model=schemas.Message,
    summary="User completed answering all questions",
)
async def game_over(_: models.User = Depends(dependencies.get_current_user)) -> Any:
    """
    User completed answering all questions.
    """

    await LOGGER.info("User completed answering all questions")

    return {"message": "Congratulations, you have answered all questions!"}


@router.get(
    "/{user_id}",
    response_model=schemas.User,
    summary="Obtain a user's details given the user ID",
)
async def read_user_by_id(
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
        await LOGGER.info("User accessed their details by ID")

        return user

    if not crud.user.is_superuser(current_user):
        await LOGGER.error(
            "User tried to access another user's details by ID", user_id=user_id
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )

    # Remove the user from `structlog`'s context and add superuser.
    unbind_contextvars("user")
    bind_contextvars(superuser=current_user)

    if not user:
        await LOGGER.error("User does not exist", user_id=user_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    await LOGGER.info("Superuser accessed user's details by ID", user=user)

    # Remove the superuser from `structlog`'s context.
    # Have to explicitly remove since we're explicitly adding superuser to context.
    unbind_contextvars("superuser")

    return user


@router.put(
    "/{user_id}",
    response_model=schemas.User,
    summary="Update a user's details given the user ID",
)
async def update_user(
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
        await LOGGER.error("User does not exist", user_id=user_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    user_in_temp = user_in.copy(
        update={"password": "[REDACTED]" if user_in.password is not None else None},
        deep=True,
    )
    await LOGGER.info(
        "Superuser initiated user details update", user=user, **user_in_temp.dict()
    )
    user = crud.user.update(db_session, db_obj=user, obj_in=user_in)
    await LOGGER.info("Superuser updated user's details by ID", user=user)

    return user


@router.delete(
    "/{user_id}",
    response_model=schemas.Message,
    summary="Delete a user given the user ID",
)
async def delete_user(
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
        await LOGGER.error("User does not exist", user_id=user_id)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this user ID does not exist in the system",
        )

    await LOGGER.info("Superuser initiated user deletion", user=user)
    user = crud.user.remove(db_session, identifier=user_id)
    await LOGGER.info("Superuser deleted user by ID", user=user)

    return {"message": "User deleted successfully"}
