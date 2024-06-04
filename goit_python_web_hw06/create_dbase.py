from random import randint, choice, sample, shuffle
import sqlite3
from faker import Faker


DB_FILE_PATH = "./hw06.sqlite"

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


class Table():
    def __init__(
            self,
            name: str,
            columns: dict,
            constraints: str | None = None,
            drop_if_exist: bool = True
    ) -> None:
        self.name = name
        if drop_if_exist:
            sql_start = f"DROP TABLE IF EXISTS {name}; CREATE TABLE {name}"
        else:
            sql_start = f"CREATE TABLE IF NOT EXISTS {name}"
        sql_columns = ", ".join(f"{key} {val}" for key, val in columns.items())
        sql_constraints = f", {constraints}" if constraints else ""
        sql = f"{sql_start} ({sql_columns}{sql_constraints});"
        with sqlite3.connect(DB_FILE_PATH) as conn:
            cur = conn.cursor()
            cur.executescript(sql)

    def insert(self, data: dict) -> None:
        sql_fields = ", ".join(data.keys())
        sql_val_fields = ", ".join("?" for _ in data.keys())
        sql = f"INSERT INTO {self.name}({sql_fields}) " \
            f"VALUES ({sql_val_fields})"

        sql_val = []
        index = 0
        while True:
            try:
                sql_val.append([val[index] for val in data.values()])
            except IndexError:
                break
            index += 1

        with sqlite3.connect(DB_FILE_PATH) as conn:
            cur = conn.cursor()
            cur.executemany(sql, sql_val)

    def select(self, column: str = "*") -> list[tuple]:
        sql = f"SELECT {column} FROM {self.name}"

        with sqlite3.connect(DB_FILE_PATH) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()


class Groups(Table):
    def __init__(self, drop_if_exist: bool = True) -> None:
        super().__init__(
            "groups",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "number": "VARCHAR(3) NOT NULL"
            },
            drop_if_exist=drop_if_exist
        )


class Students(Table):
    def __init__(self, drop_if_exist: bool = True) -> None:
        super().__init__(
            "students",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "VARCHAR(30) NOT NULL",
                "group_id": "INTEGER"
            },
            "FOREIGN KEY (group_id) REFERENCES groups (id) "
            "ON DELETE SET NULL ON UPDATE CASCADE",
            drop_if_exist=drop_if_exist
        )


class Lecturers(Table):
    def __init__(self, drop_if_exist: bool = True) -> None:
        super().__init__(
            "lecturers",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "VARCHAR(30) NOT NULL"
            },
            drop_if_exist=drop_if_exist
        )


class Subjects(Table):
    def __init__(self, drop_if_exist: bool = True) -> None:
        super().__init__(
            "subjects",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "name": "VARCHAR(30) NOT NULL",
                "lecturer_id": "INTEGER"
            },
            "FOREIGN KEY (lecturer_id) REFERENCES lecturers (id) "
            "ON DELETE SET NULL ON UPDATE CASCADE",
            drop_if_exist=drop_if_exist
        )


class Marks(Table):
    def __init__(self, drop_if_exist: bool = True) -> None:
        super().__init__(
            "marks",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "mark": "INTEGER",
                "student_id": "INTEGER",
                "subject_id": "INTEGER",
                "date": "DATE DEFAULT CURRENT_DATE"
            },
            "FOREIGN KEY (student_id) REFERENCES students (id) "
            "ON DELETE CASCADE ON UPDATE CASCADE, "
            "FOREIGN KEY (subject_id) REFERENCES subjects (id) "
            "ON DELETE CASCADE ON UPDATE CASCADE",
            drop_if_exist=drop_if_exist
        )


def generate_groups(groups: Groups, number: int) -> None:
    numbers = tuple(randint(100, 999) for _ in range(number))
    groups.insert({"number": numbers})


def generate_students(
        students: Students,
        groups_list: list,
        number: int
) -> None:
    fake = Faker()
    students_list = []
    groups = []
    for _ in range(number):
        students_list.append(fake.name())
        groups.append(choice(groups_list))
    students.insert(
        {
            "name": students_list,
            "group_id": groups
        }
    )


def generate_lecturers(lecturers: Lecturers, number: int) -> None:
    fake = Faker()
    lecturers.insert(
        {
            "name": tuple(fake.name() for _ in range(number))
        }
    )


def generate_subjects(
        subjects: Subjects,
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
    subjects.insert(
        {
            "name": subjects_list,
            "lecturer_id": lecturers_list
        }
    )


def generate_marks(
        marks: Marks,
        students_list: list,
        subjects_list: list,
        number_min_per_student: int,
        number_max_per_student: int
) -> None:
    fake = Faker()
    marks_list = []
    students = []
    subjects = []
    dates = []
    for student in students_list:
        number = randint(
            number_min_per_student,
            number_max_per_student
        )
        i = 0
        while i <= number:
            marks_list.append(randint(1, 12))
            students.append(student)
            subjects.append(subjects_list[i % len(subjects_list)])
            dates.append(fake.date_this_year().strftime("%Y-%m-%d"))
            i += 1
    marks.insert(
        {
            "mark": marks_list,
            "student_id": students,
            "subject_id": subjects,
            "date": dates
        }
    )


def main():
    groups = Groups()
    generate_groups(groups, 3)

    students = Students()
    generate_students(
        students,
        tuple(val[0] for val in groups.select("id")),
        40
    )

    lecturers = Lecturers()
    generate_lecturers(lecturers, 4)

    subjects = Subjects()
    generate_subjects(
        subjects,
        [val[0] for val in lecturers.select("id")],
        6
    )

    marks = Marks()
    generate_marks(
        marks,
        tuple(val[0] for val in students.select("id")),
        tuple(val[0] for val in subjects.select("id")),
        15,
        20
    )


if __name__ == "__main__":
    main()
