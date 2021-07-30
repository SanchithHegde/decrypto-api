"""
CRUD operations on `QuestionOrderItem` model instances.
"""

from typing import Optional

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


question_order_item = CRUDQuestionOrderItem(QuestionOrderItem)
