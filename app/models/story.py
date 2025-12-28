from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    Enum,
)

from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# -----------------------
# Enums
# -----------------------
class StoryType(str, enum.Enum):
    STORY = "story"
    BUG = "bug"
    TASK = "task"

class StoryStatus(str, enum.Enum):
    BACKLOG = "backlog"
    TODO = "to_do"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

class Priority(str, enum.Enum):
    PO = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"

# -----------------------
# Story Model
# -----------------------
class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    story_type: Mapped[StoryType] = mapped_column(Enum(StoryType), nullable=False, default=StoryType.STORY)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), nullable=False, default=Priority.P2)
    story_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[StoryStatus] = mapped_column(Enum(StoryStatus), nullable=False, default=StoryStatus.BACKLOG)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="stories")
    sprint_items = relationship("SprintItem", back_populates="story", cascade="all, delete-orphan")
