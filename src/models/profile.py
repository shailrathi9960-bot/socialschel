from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel

class SocialProfile(BaseModel):
    __tablename__ = "social_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String, nullable=False)
    platform_user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    profile_image_url = Column(String)

    # Storing encrypted tokens as binary data is more secure
    encrypted_access_token = Column(LargeBinary, nullable=False)
    encrypted_refresh_token = Column(LargeBinary)

    # Note: timezone=True is removed for SQLite compatibility
    token_expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="social_profiles")
    post_targets = relationship("PostTarget", back_populates="profile", cascade="all, delete-orphan")
