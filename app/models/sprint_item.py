from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class SprintItem(Base):
    __tablename__ = "sprint_items"
    __table_args__ = (
        UniqueConstraint("sprint_id", "story_id", name="uix_sprint_story"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sprint_id: Mapped[int] = mapped_column(ForeignKey("sprints.id"), nullable=False)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), nullable=False)

    sprint = relationship("Sprint", back_populates="items")
    story = relationship("Story", back_populates="sprint_items")
