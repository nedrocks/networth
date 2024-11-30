from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class NWBase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: datetime | None = None
