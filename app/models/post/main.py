from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.tag.association import Association

if TYPE_CHECKING:
    from app.models.tag import Tag
    from app.models.user import User


class Post(Base):
    __tablename__ = "post"
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="posts", lazy="select")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=Association.__tablename__, back_populates="posts", lazy="select"
    )
