from typing import List
import uuid
from flask import jsonify
from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    Uuid,
    create_engine,
    select,
)
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

    # id: Mapped[int] = mapped_column(primary_key=True, init=False)
    issuer: Mapped[str] = mapped_column(String(255), primary_key=True)
    sub: Mapped[str] = mapped_column(String(255), primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    chats: Mapped[List["Chat"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        # foreign_keys=lambda: [Chat.user_issuer, Chat.user_sub],
    )

    def __repr__(self) -> str:
        return f"User(issuer={self.issuer!r}, sub={self.sub!r}, email={self.email!r})"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[Uuid] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4, init=False
    )
    # user: Mapped["User"] = relationship(
    #     back_populates="chats", init=False, foreign_keys=lambda: [User.issuer, User.sub]
    # )

    user: Mapped["User"] = relationship(back_populates="chats", init=False)

    user_issuer: Mapped[str] = mapped_column(String(255))
    user_sub: Mapped[str] = mapped_column(String(255))

    # Apparently there is no ORM only version of this?
    __table_args__ = (
        ForeignKeyConstraint(["user_issuer", "user_sub"], ["user.issuer", "user.sub"]),
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, user={self.user!r}, user_issuer={self.user_issuer!r}, user_sub={self.user_sub!r}, messages={self.messages!r})"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    contents: Mapped[str] = mapped_column(Text)
    chat: Mapped["Chat"] = relationship(back_populates="messages", init=False)
    chat_id: Mapped[Uuid] = mapped_column(ForeignKey("chat.id"), default=None)

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, chat={self.chat!r}, chat_id={self.chat_id!r}, contents={self.contents!r})"


def add_test_user(db_url: str):
    engine = create_engine(db_url, echo=True)

    with Session(engine) as session:
        test_user = User(
            issuer="test_idp",
            sub="123456abcd",
            email="test_email@example.com",
            chats=[],
        )

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
        try:
            test_email_addr = "test_email@example.com"
            user_id = session.execute(
                select(User.issuer, User.sub).where(User.email == test_email_addr)
            ).all()[0]

            session.add(
                Chat(
                    messages=[Message(contents="Test message please ignore")],
                    user_issuer=user_id[0],
                    user_sub=user_id[1],
                )
            )

            session.commit()

            return "ok", 200

        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Could not create example chat"}), 409


def add_example_message_to_chat(db_url: str):
    engine = create_engine(db_url, echo=True)

    with Session(engine) as session:
        try:
            test_email_addr = "test_email@example.com"
            chat_id = session.execute(
                select(Chat.id).join(User).where(User.email == test_email_addr).limit(1)
            ).scalar_one()

            session.add(Message(chat_id=chat_id, contents="New test message!"))

            session.commit()

            return "ok", 200

        except IntegrityError:
            session.rollback()
            return jsonify(
                {"error": "Could not add example message to example chat"}
            ), 409
