import datetime
from sqlalchemy import create_engine, Integer, String, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, \
    Mapped, mapped_column


engine = create_engine(
    "postgresql://postgres:eUSeCteRICtubeNA@localhost:5432/postgres",
    echo=False
)
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String)


class Student(Base):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[int] = mapped_column(
        'group_id',
        Integer,
        ForeignKey('groups.id'),
        default=1
    )


class Lecturer(Base):
    __tablename__ = 'lecturers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Subject(Base):
    __tablename__ = 'subjects'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lecturer_id: Mapped[int] = mapped_column(
        'lecturer_id',
        Integer,
        ForeignKey('lecturers.id'),
        default=1
    )


class Mark(Base):
    __tablename__ = 'marks'
    id: Mapped[int] = mapped_column(primary_key=True)
    mark: Mapped[int] = mapped_column(Integer)
    student_id: Mapped[int] = mapped_column(
        'student_id',
        Integer,
        ForeignKey('students.id'),
        default=1
    )
    subject_id: Mapped[int] = mapped_column(
        'subject_id',
        Integer,
        ForeignKey('subjects.id'),
        default=1
    )
    date: Mapped[datetime.date] = mapped_column(server_default=func.now())


if __name__ == "__main__":
    Base.metadata.create_all(engine)
