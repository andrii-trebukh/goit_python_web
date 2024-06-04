from pathlib import Path
from run_sql_script import run_script


def main():
    path = Path()
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() == ".sql":
            print(f"Running script file: {file}")
            print(run_script(file))


if __name__ == "__main__":
    main()
