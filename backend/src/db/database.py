from sqlalchemy import Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r})"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    contents: Mapped[str] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"Chat(id={self.id!r})"


def get_session(db_pathstring: str):
    engine = create_engine(db_pathstring)
