import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Uuid, ForeignKey, text #, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass # empty placeholder

class TabGroup(Base):
    __tablename__ = "tab_group"

    # TODO: switch default=uuid.uuid4 to server_default=func.gen_random_uuid() if using Postgres - keep for SQLite locally for now
    id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"), # text() breaks out to actual SQL and puts a real timestamp
        init=False, # makes sure that this cannot be updated via the constructor
        onupdate=text("CURRENT_TIMESTAMP")
    )
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    tabs: Mapped[List["Tab"]] = relationship(back_populates="group", cascade="all, delete-orphan", init=False)

class Tab(Base):
    __tablename__ = "tab"

    # TODO: switch default=uuid.uuid4 to server_default=func.gen_random_uuid() if using Postgres - keep for SQLite locally for now
    id: Mapped[uuid.UUID] = mapped_column(Uuid, default=uuid.uuid4, primary_key=True, init=False)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tab_group.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        init=False,
        onupdate=text("CURRENT_TIMESTAMP")
    )

    group: Mapped["TabGroup"] = relationship(back_populates="tabs", init=False)