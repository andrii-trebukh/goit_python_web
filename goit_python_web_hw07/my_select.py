from sqlalchemy import select, desc, func
from create_tables import Group, Lecturer, Mark, Student, Subject, session


def select_1():
    print("Select 1:")
    stmt = select(
        Student.name,
        func.round(func.avg(Mark.mark), 2).label("avg_mark")
    ).join(Student).group_by(Student.name) \
        .order_by(desc("avg_mark")).limit(5)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_2():
    print("Select 2:")
    subq = select(
        Subject.name.label("subject"),
        Student.name.label("student"),
        func.round(func.avg(Mark.mark), 2)
            .label("avg_mark"),
        func.max(func.round(func.avg(Mark.mark), 2))
            .over(partition_by=Subject.name).label("avg_max")
    ).join(Subject).join(Student).group_by(Subject.name, Student.name) \
        .subquery()
    stmt = select(subq.c.subject, subq.c.student, subq.c.avg_mark) \
        .where(subq.c.avg_mark == subq.c.avg_max)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_3():
    print("Select 3:")
    stmt = select(
        Group.number,
        Subject.name,
        func.round(func.avg(Mark.mark), 2).label("avg_mark")
    ).join(Subject).join(Student).join(Group) \
        .group_by(Group.number, Subject.name) \
        .order_by(Group.number, Subject.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_4():
    print("Select 4:")
    stmt = select(func.round(func.avg(Mark.mark), 2))
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_5():
    print("Select 5:")
    stmt = select(Lecturer.name, Subject.name) \
        .where(Lecturer.id == Subject.lecturer_id) \
        .order_by(Lecturer.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_6():
    print("Select 6:")
    stmt = select(Group.number, Student.name) \
        .where(Student.group_id == Group.id) \
        .order_by(Group.number, Student.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_7():
    print("Select 7:")
    stmt = select(
        Group.number,
        Subject.name,
        Student.name,
        Mark.mark
    ).join(Subject).join(Student).join(Group) \
        .order_by(Group.number, Subject.name, Student.name)
    print(stmt)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_8():
    print("Select 8:")
    stmt = select(
        Lecturer.name,
        Subject.name,
        func.round(func.avg(Mark.mark), 2)
    ).join_from(Mark, Subject).join(Lecturer) \
        .group_by(Lecturer.name, Subject.name) \
        .order_by(Lecturer.name, Subject.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_9():
    print("Select 9:")
    stmt = select(
        Student.name,
        Subject.name
    ).join_from(Mark, Student).join(Subject) \
        .group_by(Student.name, Subject.name) \
        .order_by(Student.name, Subject.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def select_10():
    print("Select 10:")
    stmt = select(
        Student.name,
        Lecturer.name,
        Subject.name
    ).join_from(Mark, Student).join(Subject).join(Lecturer) \
        .group_by(Student.name, Lecturer.name, Subject.name) \
        .order_by(Student.name, Lecturer.name, Subject.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def adv_select_1():
    print("Adv select 1:")
    stmt = select(
        Lecturer.name,
        Student.name,
        func.round(func.avg(Mark.mark), 2)
    ).join(Student).join(Subject).join(Lecturer) \
        .group_by(Lecturer.name, Student.name) \
        .order_by(Lecturer.name, Student.name)
    result = session.execute(stmt)
    for res in result:
        print(res)


def adv_select_2():
    print("Adv select 2:")
    subq = select(
        Group.number.label("group"),
        Subject.name.label("subject"),
        Student.name.label("student"),
        Mark.date.label("date"),
        Mark.mark.label("mark"),
        func.max(Mark.date)
            .over(partition_by=(Group.number, Subject.name)).label("max_date")
    ).join(Subject).join(Student).join(Group).subquery()
    stmt = select(
        subq.c.group,
        subq.c.subject,
        subq.c.student,
        subq.c.date,
        subq.c.mark
    ).where(subq.c.date == subq.c.max_date) \
        .order_by(subq.c.group, subq.c.subject, subq.c.student)
    result = session.execute(stmt)
    for res in result:
        print(res)


def main():
    select_1()
    select_2()
    select_3()
    select_4()
    select_5()
    select_6()
    select_7()
    select_8()
    select_9()
    select_10()

    adv_select_1()
    adv_select_2()


if __name__ == "__main__":
    main()
