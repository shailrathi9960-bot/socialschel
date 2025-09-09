import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SocialProfileBase(BaseModel):
    platform: str
    username: str
    profile_image_url: Optional[str] = None

class SocialProfileCreate(SocialProfileBase):
    platform_user_id: str
    # The tokens will be handled internally, not passed in an API call
    # so they are not part of the create schema.

class SocialProfile(SocialProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool

    class Config:
        from_attributes = True
