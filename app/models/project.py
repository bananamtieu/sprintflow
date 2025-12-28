from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    memberships = relationship(
        "Membership",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    sprints = relationship(
        "Sprint",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    stories = relationship(
        "Story",
        back_populates="project",
        cascade="all, delete-orphan"
    )