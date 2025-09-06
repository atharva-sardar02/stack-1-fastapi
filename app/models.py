from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String, Boolean, Integer
from .db import Base

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)