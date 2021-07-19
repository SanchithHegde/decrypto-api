"""
CRUD operations on `Question` model instances.
"""

from typing import Any, Dict, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):
    """
    Encapsulates CRUD operations on `Question` model instances.
    """

    @staticmethod
    def get_by_answer(db_session: Session, *, answer: str) -> Optional[Question]:
        """
        Obtain question by answer.
        """

        return db_session.query(Question).filter(Question.answer == answer).first()

    def create(self, db_session: Session, *, obj_in: QuestionCreate) -> Question:
        """
        Create a new question and insert it into the database.
        """

        # Excluding "content" because `jsonable_encoder` tries to interpret bytes as
        # text and raises an exception.
        obj_in_data = jsonable_encoder(obj_in, exclude={"content"})

        # Copy "content" to `obj_in_data` as is
        obj_in_data["content"] = obj_in.content
        question_obj = Question(**obj_in_data)

        db_session.add(question_obj)
        db_session.commit()
        db_session.refresh(question_obj)

        return question_obj

    def update(
        self,
        db_session: Session,
        *,
        db_obj: Question,
        obj_in: Union[QuestionUpdate, Dict[str, Any]]
    ) -> Question:
        """
        Update question with fields and values specified by `obj_in`.
        """

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


question = CRUDQuestion(Question)
