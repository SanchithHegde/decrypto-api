# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_email, random_lower_string


def test_create_user(db_session: Session) -> None:
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=email, password=password, full_name=full_name)
    user = crud.user.create(db_session, obj_in=user_in)

    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db_session: Session) -> None:
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=email, password=password, full_name=full_name)
    user = crud.user.create(db_session, obj_in=user_in)

    authenticated_user = crud.user.authenticate(
        db_session, email=email, password=password
    )

    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db_session: Session) -> None:
    email = random_email()
    password = random_lower_string()

    user = crud.user.authenticate(db_session, email=email, password=password)

    assert user is None


def test_check_if_user_is_superuser(db_session: Session) -> None:
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(
        email=email, password=password, full_name=full_name, is_superuser=True
    )
    user = crud.user.create(db_session, obj_in=user_in)

    is_superuser = crud.user.is_superuser(user)

    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user(db_session: Session) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_in = UserCreate(email=username, password=password, full_name=full_name)
    user = crud.user.create(db_session, obj_in=user_in)

    is_superuser = crud.user.is_superuser(user)

    assert is_superuser is False


def test_get_user(db_session: Session) -> None:
    password = random_lower_string()
    username = random_email()
    full_name = random_lower_string()
    user_in = UserCreate(
        email=username, password=password, full_name=full_name, is_superuser=True
    )
    user = crud.user.create(db_session, obj_in=user_in)

    assert user.id  # Required for mypy
    user_2 = crud.user.get(db_session, identifier=user.id)

    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db_session: Session) -> None:
    password = random_lower_string()
    email = random_email()
    full_name = random_lower_string()
    user_in = UserCreate(
        email=email, password=password, full_name=full_name, is_superuser=True
    )
    user = crud.user.create(db_session, obj_in=user_in)
    new_password = random_lower_string()

    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    crud.user.update(db_session, db_obj=user, obj_in=user_in_update)

    assert user.id  # Required for mypy
    user_2 = crud.user.get(db_session, identifier=user.id)

    assert user_2
    assert user_2.hashed_password  # Required for mypy
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)


def test_delete_user(db_session: Session) -> None:
    password = random_lower_string()
    username = random_email()
    full_name = random_lower_string()
    user_in = UserCreate(
        email=username, password=password, full_name=full_name, is_superuser=True
    )
    user = crud.user.create(db_session, obj_in=user_in)

    assert user.id
    deleted_user = crud.user.remove(db_session, identifier=user.id)

    assert deleted_user.id == user.id
    assert deleted_user.email == user.email
    assert deleted_user.full_name == user.full_name
    assert deleted_user.is_superuser == user.is_superuser
    assert deleted_user.dict() == user.dict()

    result = crud.user.get(db_session, identifier=user.id)

    assert result is None
