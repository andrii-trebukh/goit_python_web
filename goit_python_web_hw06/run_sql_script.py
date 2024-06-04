import argparse
from pathlib import Path
import sqlite3


DB_FILE_PATH = "./hw06.sqlite"


def run_script(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        sql = fh.read()

    with sqlite3.connect(DB_FILE_PATH) as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(
        description='Run SQL script'
    )

    parser.add_argument(
        "path",
        help="Path to script file"
    )

    path = Path(parser.parse_args().path)
    print(run_script(path))


if __name__ == "__main__":
    main()
