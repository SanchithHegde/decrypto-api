"""
Imports all the models, so that `Base` has them before being imported by Alembic.
"""

# pylint: disable=unused-import

from app.db.base_class import Base
from app.models.user import User
