"""
CRUD operations on `User` model instances.
"""

from typing import Any, Dict, List, Optional, Union

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Encapsulates CRUD operations on `User` model instances.
    """

    @staticmethod
    async def get_by_email(db_session: AsyncSession, *, email: str) -> Optional[User]:
        """
        Obtain user by email address.
        """

        statement = select(User).where(User.email == email)
        return (await db_session.execute(statement)).scalar_one_or_none()

    async def create(self, db_session: AsyncSession, *, obj_in: UserCreate) -> User:
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
        await db_session.commit()

        # Update the rank for the newly added user
        await self.update_ranks(db_session)
        await db_session.refresh(user_obj)

        return user_obj

    async def update(
        self,
        db_session: AsyncSession,
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

        # If password is to be updated, calculate password hash and add it to
        # `update_data`, while deleting password from `update_data`
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        # If question number is to be updated, also update `question_number_updated_at`
        if update_data.get("question_number"):
            update_data["question_number_updated_at"] = func.now()

        user_obj = await super().update(
            db_session,
            db_obj=db_obj,
            obj_in=update_data,
            use_jsonable_encoder=use_jsonable_encoder,
        )

        # If question number was updated, update the ranks after the user object was
        # updated.
        if update_data.get("question_number"):
            await self.update_ranks(db_session)
            await db_session.refresh(user_obj)

        return user_obj

    async def remove(self, db_session: AsyncSession, *, identifier: int) -> User:
        """
        Delete user by ID.
        """

        user_obj = await super().remove(db_session, identifier=identifier)

        # Update the ranks for the remaining users
        await self.update_ranks(db_session)

        return user_obj

    async def authenticate(
        self, db_session: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Verifies that email address and password provided are correct.

        Returns `None` if either the email address or the password are incorrect, the
        `User` instance if the details are correct.
        """

        user_obj = await self.get_by_email(db_session, email=email)

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
    async def update_ranks(db_session: AsyncSession) -> None:
        """
        Updates ranks of all non-superusers.
        """

        # Using the `dense_rank()` window function
        # Reference: https://www.postgresql.org/docs/current/tutorial-window.html

        # WITH id_ranks AS (
        #   SELECT id, dense_rank() OVER (
        #     ORDER BY question_number DESC, question_number_updated_at ASC
        #   ) AS dense_rank
        #   FROM decrypto_user
        #   WHERE is_superuser = 'false'
        # )
        # UPDATE decrypto_user
        #   SET rank = id_ranks.dense_rank
        #   FROM id_ranks
        #   WHERE decrypto_user.is_superuser = 'false'
        #     AND decrypto_user.id = id_ranks.id;

        id_ranks = (
            select(
                User.id,
                func.dense_rank()
                .over(
                    order_by=[  # type: ignore
                        User.question_number.desc(),
                        User.question_number_updated_at.asc(),
                    ]
                )
                .label("dense_rank"),
            )
            .where(User.is_superuser == False)  # pylint: disable=singleton-comparison
            .cte(name="id_ranks")
        )
        statement = (
            update(User)
            .where(
                User.is_superuser == False,  # pylint: disable=singleton-comparison
                User.id == id_ranks.c.id,
            )
            .values({User.rank: id_ranks.c.dense_rank})
            .execution_options(synchronize_session=False)
        )
        await db_session.execute(statement)

        await db_session.commit()

    @staticmethod
    async def get_leaderboard(
        db_session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Returns a list of users in decreasing order of question numbers and increasing
        order of question number update timestamp, starting at offset `skip` and
        containing a maximum of `limit` number of elements.
        """

        statement = (
            select(User)
            .where(User.is_superuser == False)  # pylint: disable=singleton-comparison
            .order_by(
                User.question_number.desc(), User.question_number_updated_at.asc()
            )
            .offset(skip)
            .limit(limit)
        )
        return (await db_session.execute(statement)).scalars().all()


user = CRUDUser(User)
