"""
CRUD operations on `User` model instances.
"""

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Encapsulates CRUD operations on `User` model instances.
    """

    @staticmethod
    def get_by_email(db_session: Session, *, email: str) -> Optional[User]:
        """
        Obtain user by email address.
        """

        return db_session.query(User).filter(User.email == email).first()

    def create(self, db_session: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user and insert it into the database.
        """

        user_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )

        db_session.add(user_obj)
        db_session.commit()
        db_session.refresh(user_obj)

        return user_obj

    def update(
        self,
        db_session: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update user `db_obj` by fields and values specified by `obj_in`.
        """

        if isinstance(obj_in, dict):
            update_data = obj_in

        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db_session, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db_session: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        Verifies that email address and password provided are correct.

        Returns `None` if either the email address or the password are incorrect, the
        `User` instance if the details are correct.
        """

        user_obj = self.get_by_email(db_session, email=email)

        # User not found / incorrect email address
        if not user_obj:
            return None

        # Incorrect password
        assert user_obj.hashed_password is not None
        if not verify_password(password, user_obj.hashed_password):
            return None

        return user_obj

    @staticmethod
    def is_superuser(user_obj: User) -> bool:
        """
        Returns `True` if the user is a superuser.
        """

        if user_obj.is_superuser is None:
            return False

        return user_obj.is_superuser


user = CRUDUser(User)
