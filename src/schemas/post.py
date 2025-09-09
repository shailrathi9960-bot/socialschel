import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# --- ContentAsset Schemas ---
class ContentAssetBase(BaseModel):
    media_type: str
    filename: str
    storage_key: str

class ContentAssetCreate(ContentAssetBase):
    pass

class ContentAsset(ContentAssetBase):
    id: uuid.UUID
    post_id: Optional[uuid.UUID]
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# --- PostTarget Schemas ---
# This schema is mainly for reading data, as targets are created via ScheduledPostCreate
class PostTarget(BaseModel):
    profile_id: uuid.UUID
    platform_post_id: Optional[str]
    status: str

    class Config:
        from_attributes = True

# --- ScheduledPost Schemas ---
class ScheduledPostBase(BaseModel):
    content_text: Optional[str]
    scheduled_at: datetime

class ScheduledPostCreate(ScheduledPostBase):
    # When creating a post, we specify the IDs of the profiles to target
    target_profile_ids: List[uuid.UUID]
    # We might also associate already uploaded asset IDs
    asset_ids: Optional[List[uuid.UUID]] = []


class ScheduledPost(ScheduledPostBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    error_message: Optional[str]
    celery_task_id: Optional[str]
    created_at: datetime

    # When reading a post, we get the full target and asset objects
    targets: List[PostTarget] = []
    assets: List[ContentAsset] = []

    class Config:
        from_attributes = True
