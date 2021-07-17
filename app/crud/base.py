"""
Base class for all CRUD operations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

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

    def get(self, db_session: Session, identifier: Any) -> Optional[ModelType]:
        """
        Obtain model instance by `identifier`.

        Returns `None` on unsuccessful search.
        """

        return db_session.get(self.model, identifier)

    def get_multi(
        self, db_session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Obtain a list of model instances starting at offset `skip` and containing a
        maximum of `limit` number of elements.
        """

        return db_session.query(self.model).offset(skip).limit(limit).all()

    def create(self, db_session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create an instance of the model and insert it into the database.
        """

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore

        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)

        return db_obj

    def update(  # pylint: disable=no-self-use
        self,
        db_session: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update model instance `db_obj` with fields and values specified by `obj_in`.
        """

        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in

        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)

        return db_obj

    def remove(self, db_session: Session, *, identifier: int) -> ModelType:
        """
        Delete model instance by `identifier`.
        """

        obj = db_session.get(self.model, identifier)

        db_session.delete(obj)
        db_session.commit()

        return obj
