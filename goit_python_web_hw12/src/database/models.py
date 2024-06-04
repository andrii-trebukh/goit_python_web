import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey


Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    birthday: Mapped[datetime.date] = mapped_column(nullable=False)
    miscellaneous: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        default=None
    )


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.date] = mapped_column(
        default=func.now(),
        nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
