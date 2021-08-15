"""
CRUD operations on `QuestionOrderItem` model instances.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    async def get_by_question_number(
        db_session: AsyncSession, *, question_number: int
    ) -> Optional[QuestionOrderItem]:
        """
        Obtain question order item by question number.
        """

        statement = select(QuestionOrderItem).where(
            QuestionOrderItem.question_number == question_number
        )

        return (await db_session.execute(statement)).scalar_one_or_none()

    @staticmethod
    async def get_by_question_id(
        db_session: AsyncSession, *, question_id: int
    ) -> Optional[QuestionOrderItem]:
        """
        Obtain question order item by question ID.
        """

        statement = select(QuestionOrderItem).where(
            QuestionOrderItem.question_id == question_id
        )
        return (await db_session.execute(statement)).scalar_one_or_none()


question_order_item = CRUDQuestionOrderItem(QuestionOrderItem)
