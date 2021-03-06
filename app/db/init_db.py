"""
Creates initial data (first superuser) in the database.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app import LOGGER, crud, schemas
from app.core.config import settings
from app.db import base  # pylint: disable=unused-import

# Make sure all SQLAlchemy models are imported (app.db.base) before initializing DB
# otherwise, SQLAlchemy might fail to initialize relationships properly.
# For more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db_session: AsyncSession) -> None:
    """
    Adds the first superuser to the database if it doesn't exist already.
    """

    # Tables should be created with Alembic migrations.
    # But if you don't want to use migrations, create the tables by un-commenting the
    # following line:
    # Base.metadata.create_all(bind=engine)

    user = await crud.user.get_by_email(db_session, email=settings.FIRST_SUPERUSER)

    if not user:
        user_in = schemas.UserCreate(
            full_name=settings.FIRST_SUPERUSER_NAME,
            email=settings.FIRST_SUPERUSER,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.user.create(db_session, obj_in=user_in)
        LOGGER.info(
            "Added first superuser to the database", email=settings.FIRST_SUPERUSER
        )
