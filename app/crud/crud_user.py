"""
CRUD operations on `User` model instances.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import func
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
        self.update_ranks(db_session)
        db_session.refresh(user_obj)

        return user_obj

    def update(
        self,
        db_session: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
        use_jsonable_encoder: bool = False
    ) -> User:
        """
        Update user `db_obj` by fields and values specified by `obj_in`.
        """

        if isinstance(obj_in, dict):
            update_data = obj_in

        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        if update_data.get("question_number"):
            update_data["question_number_updated_at"] = func.now()

        user_obj = super().update(
            db_session,
            db_obj=db_obj,
            obj_in=update_data,
            use_jsonable_encoder=use_jsonable_encoder,
        )

        if update_data.get("question_number"):
            self.update_ranks(db_session)
            db_session.refresh(user_obj)

        return user_obj

    def remove(self, db_session: Session, *, identifier: int) -> User:
        """
        Delete user by ID.
        """

        user_obj = super().remove(db_session, identifier=identifier)

        self.update_ranks(db_session)

        return user_obj

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

    @staticmethod
    def update_ranks(db_session: Session) -> None:
        """
        Updates ranks of all users.
        """

        # Using the `dense_rank()` window function
        # Reference: https://www.postgresql.org/docs/current/tutorial-window.html

        # WITH id_ranks AS (
        #   SELECT id, dense_rank() OVER (
        #     ORDER BY question_number DESC, question_number_updated_at ASC
        #   ) AS dense_rank
        #   FROM decrypto_user
        # )
        # UPDATE decrypto_user
        #   SET rank = id_ranks.dense_rank
        #   FROM id_ranks
        #   WHERE decrypto_user.id = id_ranks.id;

        id_ranks = db_session.query(
            User.id,
            func.dense_rank()
            .over(
                order_by=[  # type: ignore
                    User.question_number.desc(),
                    User.question_number_updated_at.asc(),
                ]
            )
            .label("dense_rank"),
        ).cte(name="id_ranks")
        db_session.query(User).filter(User.id == id_ranks.c.id).update(
            {User.rank: id_ranks.c.dense_rank}, synchronize_session=False
        )

        db_session.commit()

    @staticmethod
    def get_leaderboard(
        db_session: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Returns a list of users in decreasing order of question numbers and increasing
        order of question number update timestamp, starting at offset `skip` and
        containing a maximum of `limit` number of elements.
        """

        return (
            db_session.query(User)
            .order_by(
                User.question_number.desc(), User.question_number_updated_at.asc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


user = CRUDUser(User)
