import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class TabBase(BaseModel):
    title: str = Field(..., max_length=500, description="Human-readable title of the tab")
    url: str = Field(..., max_length=2000, description="Tab URL")
    position: int = Field(..., ge=0, description="Positive int value for the position of the tab in its group")

class TabCreate(TabBase):
    group_id: uuid.UUID

class TabUpdate(TabBase):
    group_id: uuid.UUID

class TabRead(TabBase):
    id: uuid.UUID
    group_id: uuid.UUID
    updated_at: datetime

    class ConfigDict:
        from_attributes = True # this is so that Pydantic can read db objects directly

class TabGroupCreate(BaseModel):
    user_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=150) # ... indicates there is no default value and user input is required
    color: str = Field(..., min_length=1, max_length=50)
    device_id: str = Field(..., min_length=1, max_length=100)

class TabGroupUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=150) # ... indicates there is no default value and user input is required
    color: Optional[str] = Field(default=None, min_length=1, max_length=50)
    device_id: Optional[str] = Field(default=None, min_length=1, max_length=100)
    deleted: Optional[bool] = None

class TabGroupRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    color: str
    device_id: str
    updated_at: datetime
    deleted: bool
    tabs: list[TabRead] = []

    class ConfigDict:
        from_attributes = True