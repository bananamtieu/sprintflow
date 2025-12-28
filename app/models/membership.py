import enum
from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class MembershipRole(enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_user_project"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    role: Mapped[MembershipRole] = mapped_column(
        Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False
    )

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="memberships")
