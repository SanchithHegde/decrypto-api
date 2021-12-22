"""
Pydantic schemas for timestamps.
"""

from datetime import datetime

from pydantic import BaseModel


class Timestamp(BaseModel):
    """
    Pydantic timestamp schema, represents the times in ISO 8601 format.
    """

    timestamp: datetime
