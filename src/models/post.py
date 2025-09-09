from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel, Base

class ScheduledPost(BaseModel):
    __tablename__ = "scheduled_posts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content_text = Column(Text)

    # Note: timezone=True is removed for SQLite compatibility
    scheduled_at = Column(DateTime, nullable=False, index=True)

    status = Column(String, nullable=False, default='scheduled', index=True)
    error_message = Column(Text)
    celery_task_id = Column(String, index=True)

    user = relationship("User", back_populates="scheduled_posts")

    # Association object for many-to-many relationship with SocialProfile
    targets = relationship("PostTarget", back_populates="post", cascade="all, delete-orphan")

    assets = relationship("ContentAsset", back_populates="post", cascade="all, delete-orphan")


class PostTarget(Base):
    """
    Association object between ScheduledPost and SocialProfile.
    This table stores which profiles a post is targeting, and the status of the post for that specific platform.
    """
    __tablename__ = 'post_targets'
    post_id = Column(UUID(as_uuid=True), ForeignKey('scheduled_posts.id'), primary_key=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('social_profiles.id'), primary_key=True)

    # Stores the ID of the post on the social platform after publishing
    platform_post_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default='pending', index=True) # e.g., pending, published, failed

    post = relationship("ScheduledPost", back_populates="targets")
    profile = relationship("SocialProfile", back_populates="post_targets")


class ContentAsset(BaseModel):
    __tablename__ = "content_assets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_posts.id"), nullable=True, index=True)

    storage_key = Column(String, nullable=False) # e.g., S3 object key
    media_type = Column(String, nullable=False) # e.g., 'image', 'video'
    filename = Column(String, nullable=False)

    user = relationship("User", back_populates="content_assets")
    post = relationship("ScheduledPost", back_populates="assets")
