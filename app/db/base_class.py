"""
Base class for all SQLAlchemy model definitions.
"""

from typing import Any, Dict

from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, as_declarative, declared_attr

from app.utils import project_name_lowercase_no_spaces


@as_declarative()
class Base:
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

        project_name = project_name_lowercase_no_spaces()
        class_name = cls.__name__.lower()

        return f"{project_name}_{class_name}"

    def dict(self) -> Dict[str, Any]:
        """
        Convert the model instance into a dictionary.
        """

        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
