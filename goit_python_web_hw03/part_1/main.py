import sys
from sorter import Sorter


def usage():
    print("Usage: python3 main.py DIR_PATH")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        usage()

    try:
        sorter = Sorter(sys.argv[1])
    except FileNotFoundError as err:
        print(err)
        usage()

    sorter.sort_it_out()


if __name__ == "__main__":
    main()
