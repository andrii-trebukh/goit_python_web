import argparse
from sqlalchemy import select, inspect
import sqlalchemy.orm
from create_tables import Group, Lecturer, Mark, Student, Subject, session


COMMANDS = {}
MODELS = {}


def command_handler(command):
    def outer_func(func):
        def wrapper(**kwargs):
            return func(**kwargs)

        COMMANDS[command] = wrapper

        return wrapper
    return outer_func


def make_nice_table(header, body, column_width=25):
    str_tbline = f'+{"+".join(f"{chr(45):-^{column_width}}" for _ in header)}+'
    str_header = f'|{"|".join(f"{title:^{column_width}}" for title in header)}|'

    str_body = ""
    for line in body:
        str_body += f'|{"|".join(f"{str(column):^{column_width}}" for column in line)}|\n'
    return f"{str_tbline}\n{str_header}\n" \
        f"{str_tbline}\n{str_body}{str_tbline}"


@command_handler("list")
def list_command(model, rid, column, value):
    columns = dict(inspect(MODELS[model]).attrs)
    criteria = {"id": rid} if rid else {}
    if column is not None and value is None:
        columns = {column: columns[column]}
    elif column is not None and value is not None:
        criteria[column] = value

    stmt = select(*columns.values()).filter_by(**criteria)
    result = session.execute(stmt)

    return make_nice_table(columns.keys(), result)


@command_handler("create")
def create_command(model, rid, column, value):
    item = MODELS[model](
        **{column: value}
    )
    session.add(item)
    session.commit()

    return f"{model} {column} = {value} has been added"


@command_handler("update")
def update_command(model, rid, column, value):
    stmt = select(MODELS[model]).where(MODELS[model].id == rid)
    try:
        result = session.execute(stmt).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        return f"No row Id {rid} was found"
    setattr(result, column, value)
    session.commit()
    return f"{column} value has been changed to {value} in {model}"


@command_handler("remove")
def remove_command(model, rid, column, value):
    stmt = select(MODELS[model]).where(MODELS[model].id == rid)
    try:
        result = session.execute(stmt).scalar_one()
    except sqlalchemy.exc.NoResultFound:
        return f"No row Id {rid} was found"
    session.delete(result)
    session.commit()
    return f"Row Id {rid} in {model} has been removed"


def main():
    for name, val in globals().items():
        if isinstance(val, sqlalchemy.orm.decl_api.DeclarativeMeta):
            MODELS[name] = val

    columns = set()
    for model in MODELS.values():
        for column in dict(inspect(model).attrs):
            if column != "id":
                columns.add(column)

    parser = argparse.ArgumentParser(
        description='CLI interface of CRUD operations with PostgreSQL database'
    )
    parser.add_argument(
        "-a",
        "--action",
        choices=COMMANDS,
        nargs=1,
        help="Database action",
        required=True
    )
    parser.add_argument(
        "-m",
        "--model",
        choices=MODELS,
        nargs=1,
        help="Database model",
        required=True
    )
    parser.add_argument(
        "--id",
        nargs=1,
        help="Id. Required for update and remove options, "
        "ignored for create option",
        required=False,
    )
    parser.add_argument(
        "-c",
        "--column",
        choices=columns,
        nargs=1,
        help="Column name",
        required=False,
    )
    parser.add_argument(
        "-v",
        "--value",
        nargs=1,
        help="Value",
        required=False,
    )
    args = parser.parse_args()

    action = args.action[0]
    model = args.model[0]
    rid = args.id[0] if args.id else None
    column = args.column[0] if args.column else None
    value = args.value[0] if args.value else None

    if action in ("update", "remove") and rid is None:
        parser.error(f"--id required for {action} option")

    if action in ("create", "update") and (column is None or value is None):
        parser.error(f"-c and -v required for {action} option")

    if column is not None:
        if column not in dict(inspect(MODELS[model]).attrs):
            parser.error(f'There are no column "{column}" in {model}')

    print(COMMANDS[action](model=model, rid=rid, column=column, value=value))


if __name__ == "__main__":
    main()
