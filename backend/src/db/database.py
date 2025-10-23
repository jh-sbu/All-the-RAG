from typing import List
from flask import jsonify
from sqlalchemy import ForeignKey, String, Text, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    Session,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    chats: Mapped[List["Chat"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user: Mapped["User"] = relationship(back_populates="chats", init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    messages: Mapped[List["Message"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, user={self.user!r}, user_id={self.user_id!r}, messages={self.messages!r})"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    chat: Mapped["Chat"] = relationship(back_populates="messages", init=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"), init=False)
    contents: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, chat={self.chat!r}, chat_id={self.chat_id!r}, contents={self.contents!r})"


def add_test_user(db_url: str):
    engine = create_engine(db_url, echo=True)

    with Session(engine) as session:
        test_user = User(email="test_email@example.com", chats=[])

        try:
            session.add(test_user)
            session.commit()

            return "ok", 200

        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Test user already created"}), 409


def create_example_chat(db_url: str):
    engine = create_engine(db_url, echo=True)

    with Session(engine) as session:
        test_email_addr = "test_email@example.com"
        user_id = session.execute(
            select(User.id).where(User.email == test_email_addr)
        ).scalar_one()

        session.add(
            Chat(
                user_id=user_id,
                messages=[Message(contents="Test message please ignore")],
            )
        )
