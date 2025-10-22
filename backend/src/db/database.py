from typing import List
from sqlalchemy import ForeignKey, Text, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    chats: Mapped[List["Chat"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped["User"] = relationship(back_populates="chats")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    messages: Mapped[List["Message"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, user={self.user!r}, user_id={self.user_id!r}, messages={self.messages!r})"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat: Mapped["Chat"] = relationship(back_populates="messages")
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    contents: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, chat={self.chat!r}, chat_id={self.chat_id!r}, contents={self.contents!r})"


def get_session(db_pathstring: str):
    engine = create_engine(db_pathstring)
