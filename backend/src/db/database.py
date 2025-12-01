import re
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
    selectinload,
)


ECHO_SQL: bool = False


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

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, init=False
    )

    user: Mapped["User"] = relationship(back_populates="chats", init=False)

    user_issuer: Mapped[str] = mapped_column(String(255))
    user_sub: Mapped[str] = mapped_column(String(255))

    title: Mapped[str] = mapped_column(String(255))

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
    role: Mapped[str] = mapped_column(String(255))
    chat: Mapped["Chat"] = relationship(back_populates="messages", init=False)
    chat_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chat.id"), default=None
    )

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r}, chat={self.chat!r}, chat_id={self.chat_id!r}, contents={self.contents!r})"


def db_get_all_chats(db_url: str, issuer: str, sub: str) -> list[dict]:
    """Return all chats associated with the given user email.

    Raises:
        NoResultFound: User with the given email does not exist.
    """
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.issuer == issuer, User.sub == sub)
        ).scalar_one()

        chats = (
            session.execute(
                select(Chat)
                .where(Chat.user == user)
                .options(selectinload(Chat.user), selectinload(Chat.messages))
            )
            .scalars()
            .all()
        )

        result = [
            {
                "id": str(chat.id),
                "user_email": str(chat.user.email),
                "title": str(chat.title),
                "messages": [
                    {"id": msg.id, "role": msg.role, "contents": msg.contents}
                    for msg in chat.messages
                ],
            }
            for chat in chats
        ]

        return result


def db_get_all_messages(
    db_url: str, chat_id: uuid.UUID, issuer: str, sub: str
) -> list[dict]:
    """
    Get all chat messages associated with the specified chat
    Raises:
        NoResultFound: Chat with the given UUID does not exist, or
        user with the given email address does not exist
    """
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.issuer == issuer, User.sub == sub)
        ).scalar_one()

        chat = session.execute(select(Chat).where(Chat.id == chat_id)).scalar_one()

        if chat.user != user:
            raise PermissionError("User not authorized to access this chat")

        messages = (
            session.execute(
                select(Message).where(Message.chat_id == chat_id).order_by(Message.id)
            )
            .scalars()
            .all()
        )

        messages = [
            {
                "sender": message.role,
                "text": message.contents,
            }
            for message in messages
        ]

        return messages


def db_create_message(db_url: str, role: str, contents: str, chat_id: uuid.UUID):
    """Store a new message in the specified chat"""
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        new_message = Message(contents=contents, role=role, chat_id=chat_id)

        session.add(new_message)
        session.commit()

        return new_message


def db_get_chat(db_url: str, chat_id: uuid.UUID, user_email: str) -> Chat:
    """Retrieve a specific chat owned by user
    Raises: NoResultFound if user or chat cannot be found"""
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.email == user_email)
        ).scalar_one()

        chat = session.execute(select(Chat).where(Chat.id == chat_id)).scalar_one()

        # User tries to access a chat that is not theirs
        # Don't tell them they hit a real chat that isn't theirs,
        # but leave this logic separate to make identifying potential
        # troublemakers easier
        if user.sub != chat.user_sub or user.issuer != chat.user_issuer:
            raise PermissionError("User is not the owner of the specified chat")

        return chat


def db_get_user(db_url: str, issuer: str, sub: str) -> User:
    """
    Get the user with the given email.
    Raises:
        NoResultFound: If there is no user with the given email.
    """
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        user_stmt = select(User).where(User.issuer == issuer, User.sub == sub)
        user = session.execute(user_stmt).scalar_one()
        return user


def db_create_chat(db_url: str, initial_message: str, user: User):
    """Create a new chat for the given user"""
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        new_chat = Chat(
            user_issuer=user.issuer,
            user_sub=user.sub,
            title="Previous Chat",
            messages=[Message(initial_message, "user")],
        )
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)

        return new_chat


def db_set_chat_title(db_url: str, chat_id: uuid.UUID, chat_title: str):
    """Set the title of an already created chat
    Raises:
        NoResultFound if no chat with the given id can be found
    """
    engine = create_engine(db_url, echo=ECHO_SQL)

    chat_title = chat_title.strip()

    TITLE_PATTERN = re.compile(r"^[^\x00-\x1F\x7F]+$")

    if not TITLE_PATTERN.match(chat_title) or chat_title == "":
        # Default title
        chat_title = "Previous Chat"

    with Session(engine) as session:
        chat = session.execute(select(Chat).where(Chat.id == chat_id)).scalar_one()

        chat.title = chat_title

        session.commit()


def db_delete_user(db_url: str, user_email: str):
    """Delete the specified user.
    Does NOT do any auth checks, that
    should be handled separately.
    """
    engine = create_engine(db_url)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.email == user_email)
        ).scalar_one()
        session.delete(user)

        session.commit()


def db_delete_chat(db_url: str, chat_id: uuid.UUID, issuer: str, sub: str):
    """Delete the specified chat.
    Returns: True if the chat was successfully deleted; false otherwise
    Raises:
        PermissionError: If the user does not own the specified chat
    """
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.issuer == issuer, User.sub == sub)
        ).scalar_one()

        chat_to_delete = session.execute(
            select(Chat).where(Chat.id == chat_id)
        ).scalar_one()

        if (
            chat_to_delete.user_issuer != user.issuer
            or chat_to_delete.user_sub != user.sub
        ):
            raise PermissionError("User is not the owner of the specified chat")

        session.delete(chat_to_delete)
        session.commit()


def add_example_message_to_chat(db_url: str):
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        try:
            test_email_addr = "test_email@example.com"
            chat_id = session.execute(
                select(Chat.id).join(User).where(User.email == test_email_addr).limit(1)
            ).scalar_one()

            session.add(
                Message(
                    chat_id=chat_id,
                    contents="New test message!",
                    role="Test role please ignore",
                )
            )

            session.commit()

            return "ok", 200

        except IntegrityError:
            session.rollback()
            return jsonify(
                {"error": "Could not add example message to example chat"}
            ), 409


def add_test_user(db_url: str):
    engine = create_engine(db_url, echo=ECHO_SQL)

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
    engine = create_engine(db_url, echo=ECHO_SQL)

    with Session(engine) as session:
        try:
            test_email_addr = "test_email@example.com"
            user_id = session.execute(
                select(User.issuer, User.sub).where(User.email == test_email_addr)
            ).all()[0]

            session.add(
                Chat(
                    messages=[
                        Message(
                            contents="Test message please ignore",
                            role="Test role please ignore",
                        )
                    ],
                    title="Previous Chat",
                    user_issuer=user_id[0],
                    user_sub=user_id[1],
                )
            )

            session.commit()

            return "ok", 200

        except IntegrityError:
            session.rollback()
            return jsonify({"error": "Could not create example chat"}), 409
