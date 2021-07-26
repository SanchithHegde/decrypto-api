"""
CRUD operations on `QuestionOrderItem` model instances.
"""

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question_order_item import QuestionOrderItem
from app.schemas.question_order_item import (
    QuestionOrderItemCreate,
    QuestionOrderItemUpdate,
)


class CRUDQuestionOrderItem(
    CRUDBase[QuestionOrderItem, QuestionOrderItemCreate, QuestionOrderItemUpdate]
):
    """
    Encapsulates CRUD operations on `QuestionOrderItem` model instances.
    """

    @staticmethod
    def get_by_question_number(
        db_session: Session, *, question_number: int
    ) -> Optional[QuestionOrderItem]:
        """
        Obtain question order item by question number.
        """

        return (
            db_session.query(QuestionOrderItem)
            .filter(QuestionOrderItem.question_number == question_number)
            .first()
        )

    @staticmethod
    def get_by_question_id(
        db_session: Session, *, question_id: int
    ) -> Optional[QuestionOrderItem]:
        """
        Obtain question order item by question ID.
        """

        return (
            db_session.query(QuestionOrderItem)
            .filter(QuestionOrderItem.question_id == question_id)
            .first()
        )

    def update(  # pylint: disable=no-self-use
        self,
        db_session: Session,
        *,
        db_obj: QuestionOrderItem,
        obj_in: Union[QuestionOrderItemUpdate, Dict[str, Any]]
    ) -> QuestionOrderItem:
        """
        Update question order item with fields and values specified by `obj_in`.
        """

        # Using db_obj.dict() method since jsonable_encoder() tries to encode raw image
        # bytes as UTF-8, which would fail for obvious reasons.
        obj_data = db_obj.dict()

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


question_order_item = CRUDQuestionOrderItem(QuestionOrderItem)
