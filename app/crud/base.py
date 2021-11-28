"""
Base class for all CRUD operations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for all CRUD operations.
    """

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to create, read, update, delete (CRUD).

        # Parameters

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """

        self.model = model

    async def get(
        self, db_session: AsyncSession, identifier: int
    ) -> Optional[ModelType]:
        """
        Obtain model instance by `identifier`.

        Returns `None` on unsuccessful search.
        """

        return await db_session.get(self.model, identifier)

    async def get_multi(
        self, db_session: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Obtain a list of model instances starting at offset `skip` and containing a
        maximum of `limit` number of elements.
        """

        statement = select(self.model).offset(skip).limit(limit)
        return (await db_session.execute(statement)).scalars().all()

    async def create(
        self, db_session: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        """
        Create an instance of the model and insert it into the database.
        """

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)

        return db_obj

    async def update(  # pylint: disable=no-self-use
        self,
        db_session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        use_jsonable_encoder: bool = True
    ) -> ModelType:
        """
        Update model instance `db_obj` with fields and values specified by `obj_in`.

        # Parameters

        * `use_jsonable_encoder`: Specifies whether to use FastAPI's built-in
          `jsonable_encoder` which can be used to convert an SQLAlchemy model instance
          into a `dict`.
          Needs to be `False` only in cases where one or more of the attributes of the
          model instance cannot be serialized into a JSON-compatible type, such as the
          raw bytes of a file which cannot be interpreted as text.
          Default: `True`
        """

        if use_jsonable_encoder:
            obj_data = jsonable_encoder(db_obj)

        else:
            obj_data = db_obj.dict()

        if isinstance(obj_in, dict):
            update_data = obj_in

        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)

        return db_obj

    async def remove(self, db_session: AsyncSession, *, identifier: int) -> ModelType:
        """
        Delete model instance by `identifier`.
        """

        obj = await db_session.get(self.model, identifier)

        assert obj

        await db_session.delete(obj)
        await db_session.commit()

        return obj
