# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_create_user(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name, email=email, username=username, password=password
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.email == email
    assert hasattr(user, "hashed_password")


async def test_authenticate_user_with_email(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name, email=email, username=username, password=password
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    authenticated_user = await crud.user.authenticate(
        db_session, username=email, password=password
    )

    assert authenticated_user
    assert user.email == authenticated_user.email


async def test_authenticate_user_with_username(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name, email=email, username=username, password=password
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    authenticated_user = await crud.user.authenticate(
        db_session, username=username, password=password
    )

    assert authenticated_user
    assert user.username == authenticated_user.username


async def test_not_authenticate_user(db_session: AsyncSession) -> None:
    email = random_email()
    password = random_lower_string()

    user = await crud.user.authenticate(db_session, username=email, password=password)

    assert user is None


async def test_check_if_user_is_superuser(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        username=username,
        password=password,
        is_superuser=True,
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    is_superuser = crud.user.is_superuser(user)

    assert is_superuser is True


async def test_check_if_user_is_superuser_normal_user(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name, email=email, username=username, password=password
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    is_superuser = crud.user.is_superuser(user)

    assert is_superuser is False


async def test_get_user(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        username=username,
        password=password,
        is_superuser=True,
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.id  # Required for mypy
    user_2 = await crud.user.get(db_session, identifier=user.id)

    assert user_2
    assert user.email == user_2.email
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


async def test_update_user(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        username=username,
        password=password,
        is_superuser=True,
    )
    user = await crud.user.create(db_session, obj_in=user_in)
    new_password = random_lower_string()

    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    await crud.user.update(db_session, db_obj=user, obj_in=user_in_update)

    assert user.id  # Required for mypy
    user_2 = await crud.user.get(db_session, identifier=user.id)

    assert user_2
    assert user_2.hashed_password  # Required for mypy
    assert user.email == user_2.email
    assert user.username == user_2.username
    assert verify_password(new_password, user_2.hashed_password)


async def test_delete_user(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name,
        email=email,
        username=username,
        password=password,
        is_superuser=True,
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.id
    deleted_user = await crud.user.remove(db_session, identifier=user.id)

    assert deleted_user.id == user.id
    assert deleted_user.email == user.email
    assert deleted_user.username == user.username
    assert deleted_user.full_name == user.full_name
    assert deleted_user.is_superuser == user.is_superuser
    assert deleted_user.dict() == user.dict()

    result = await crud.user.get(db_session, identifier=user.id)

    assert result is None


async def test_user_positive_rank_on_creation(db_session: AsyncSession) -> None:
    full_name = random_lower_string()
    email = random_email()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(
        full_name=full_name, email=email, username=username, password=password
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.rank and user.rank > 0


# pylint: disable=too-many-locals
async def test_user_higher_rank_on_question_number_increase(
    db_session: AsyncSession,
) -> None:
    # "Higher rank" considering rank 1 is higher than rank 2

    full_name1 = random_lower_string()
    email1 = random_email()
    username1 = random_lower_string()
    password1 = random_lower_string()
    user_in1 = UserCreate(
        full_name=full_name1, email=email1, username=username1, password=password1
    )
    user1 = await crud.user.create(db_session, obj_in=user_in1)
    assert user1.id
    assert user1.question_number
    assert user1.rank

    # This test uses 2 users because if user1's previous rank was 1, then it will remain
    # as rank 1 after updating. So, we ensure there's at least one user above user1 in
    # the leaderboard.
    full_name2 = random_lower_string()
    email2 = random_email()
    username2 = random_lower_string()
    password2 = random_lower_string()
    user_in2 = UserCreate(
        full_name=full_name2, email=email2, username=username2, password=password2
    )
    user2 = await crud.user.create(db_session, obj_in=user_in2)
    assert user2.id

    # Update user2 to have higher question number and rank than user1
    user2_in_update1 = UserUpdate(question_number=user1.question_number + 1)
    await crud.user.update(db_session, db_obj=user2, obj_in=user2_in_update1)
    updated_user2 = await crud.user.get(db_session, identifier=user2.id)

    updated_user1_1 = await crud.user.get(db_session, identifier=user1.id)
    assert updated_user1_1
    assert updated_user1_1.question_number
    assert updated_user1_1.question_number_updated_at
    assert updated_user1_1.rank
    old_question_number = updated_user1_1.question_number
    old_question_number_updated_at = updated_user1_1.question_number_updated_at
    old_rank = updated_user1_1.rank

    assert updated_user2
    assert updated_user2.rank and updated_user2.rank < old_rank

    new_question_number = old_question_number + 1
    user_in_update = UserUpdate(question_number=new_question_number)
    await crud.user.update(db_session, db_obj=updated_user1_1, obj_in=user_in_update)
    updated_user1_2 = await crud.user.get(db_session, identifier=user1.id)

    assert updated_user1_2
    assert (
        updated_user1_2.question_number
        and updated_user1_2.question_number == old_question_number + 1
    )
    assert (
        updated_user1_2.question_number_updated_at
        and updated_user1_2.question_number_updated_at > old_question_number_updated_at
    )
    assert updated_user1_2.rank and updated_user1_2.rank < old_rank


async def test_user_lower_rank_on_another_user_same_rank_question_number_increase(
    db_session: AsyncSession,
) -> None:
    full_name1 = random_lower_string()
    email1 = random_email()
    username1 = random_lower_string()
    password1 = random_lower_string()
    user_in1 = UserCreate(
        full_name=full_name1, email=email1, username=username1, password=password1
    )
    user1 = await crud.user.create(db_session, obj_in=user_in1)
    assert user1.id
    assert user1.question_number
    assert user1.rank
    user1_rank = user1.rank

    full_name2 = random_lower_string()
    email2 = random_email()
    username2 = random_lower_string()
    password2 = random_lower_string()
    user_in2 = UserCreate(
        full_name=full_name2, email=email2, username=username2, password=password2
    )
    user2 = await crud.user.create(db_session, obj_in=user_in2)
    assert user2.id

    # Update user2 to have same question number as user1
    user2_in_update1 = UserUpdate(question_number=user1.question_number)
    await crud.user.update(db_session, db_obj=user2, obj_in=user2_in_update1)
    updated_user2_1 = await crud.user.get(db_session, identifier=user2.id)

    assert updated_user2_1
    assert updated_user2_1.question_number
    assert updated_user2_1.question_number == user1.question_number
    assert updated_user2_1.rank
    assert updated_user2_1.rank > user1_rank

    # Increment user2's question number by 1
    new_question_number = updated_user2_1.question_number + 1
    user2_in_update2 = UserUpdate(question_number=new_question_number)
    await crud.user.update(db_session, db_obj=updated_user2_1, obj_in=user2_in_update2)
    updated_user2_2 = await crud.user.get(db_session, identifier=user2.id)

    # User1 should have lower rank than user2
    assert updated_user2_2
    assert updated_user2_2.rank
    assert user1_rank > updated_user2_2.rank


# pylint: enable=too-many-locals
