"""
Base class for all SQLAlchemy model definitions.
"""

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped

from app.core.config import settings


@as_declarative()
class Base:  # pylint: disable=too-few-public-methods
    """
    Base class for all SQLAlchemy model definitions.
    """

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> Mapped[str]:  # pylint: disable=no-self-argument
        """
        Generate __tablename__ automatically.
        """

        project_name = settings.PROJECT_NAME.strip().lower().replace(" ", "")
        class_name = cls.__name__.lower()

        return f"{project_name}_{class_name}"
