from random import choice, randint, sample, shuffle
from sqlalchemy import select
from faker import Faker
from create_tables import Group, Lecturer, Mark, Student, Subject, session

SUBJECTS_LIST = (
    "English",
    "math",
    "art",
    "science",
    "history",
    "music",
    "geography",
    "drama",
    "biology",
    "chemistry",
    "physics",
    "foreign languages",
    "social studies",
    "technology",
    "philosophy",
    "graphic design",
    "literature",
    "algebra",
    "geometry"
)


def generate_groups(number: int) -> None:
    for _ in range(number):
        group = Group(number=randint(100, 999))
        session.add(group)
    session.commit()


def generate_students(
        groups_list: list,
        number: int
) -> None:
    fake = Faker()
    for _ in range(number):
        student = Student(
            name=fake.name(),
            group_id=choice(groups_list)
        )
        session.add(student)
    session.commit()


def generate_lecturers(number: int) -> None:
    fake = Faker()
    for _ in range(number):
        lecturer = Lecturer(
            name=fake.name()
        )
        session.add(lecturer)
    session.commit()


def generate_subjects(
        lecturers_list: list,
        number: int
) -> None:
    subjects_list = sample(SUBJECTS_LIST, number)
    shuffle(lecturers_list)
    while len(lecturers_list) < number:
        lecturers = lecturers_list.copy()
        shuffle(lecturers)
        lecturers_list += lecturers
    lecturers_list = lecturers_list[:number]
    for subj, lecrurer in zip(subjects_list, lecturers_list):
        subject = Subject(
            name=subj,
            lecturer_id=lecrurer
        )
        session.add(subject)
    session.commit()


def generate_marks(
        students_list: list,
        subjects_list: list,
        number_min_per_student: int,
        number_max_per_student: int
) -> None:
    fake = Faker()
    for student in students_list:
        number = randint(
            number_min_per_student,
            number_max_per_student
        )
        i = 0
        while i <= number:
            mark = Mark(
                mark=randint(1, 12),
                student_id=student,
                subject_id=subjects_list[i % len(subjects_list)],
                date=fake.date_this_year().strftime("%Y-%m-%d")
            )
            session.add(mark)
            i += 1
    session.commit()


def main():
    generate_groups(3)

    stmt = select(Group)
    result = session.execute(stmt)

    generate_students(
        tuple(val.id for val in result.scalars()),
        40
    )

    generate_lecturers(4)

    stmt = select(Lecturer)
    result = session.execute(stmt)

    generate_subjects(
        [val.id for val in result.scalars()],
        6
    )

    stmt = select(Student)
    result = session.execute(stmt)
    students = tuple(val.id for val in result.scalars())

    stmt = select(Subject)
    result = session.execute(stmt)
    subjects = tuple(val.id for val in result.scalars())

    generate_marks(
        students,
        subjects,
        15,
        20
    )


if __name__ == "__main__":
    main()
