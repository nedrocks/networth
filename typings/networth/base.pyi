"""
This type stub file was generated by pyright.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class NWBase(BaseModel):
    id: UUID = ...
    created_at: datetime = ...
    updated_at: datetime = ...
    deleted_at: datetime | None = ...


