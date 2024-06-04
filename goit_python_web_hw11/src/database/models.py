import datetime
from sqlalchemy import String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


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
