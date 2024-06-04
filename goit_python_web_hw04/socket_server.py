from datetime import datetime
import json
from pathlib import Path
import pickle
import socket
import sys

DATABASE_FILE_PATH = "./storage/data.json"


def socket_receive(ip: str = "127.0.0.1", port: int = 5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    try:
        while True:
            data, _ = sock.recvfrom(1024)
            data = pickle.loads(data)
            write_to_json(data)
    except KeyboardInterrupt:
        print('Destroy socket server')
    finally:
        sock.close()
        sys.exit(0)


def check_data_file(database_path: str = DATABASE_FILE_PATH):
    path = Path(database_path)
    if path.exists():
        return
    if not path.parent.exists():
        path.parent.mkdir()
    with open(path, mode="wt", encoding="utf-8") as fd:
        fd.write("{}")


def write_to_json(data: dict):
    try:
        with open(DATABASE_FILE_PATH, mode="rt", encoding="utf-8") as fd:
            database = json.load(fd)
    except json.decoder.JSONDecodeError:
        print("Database file is corrupted. Making backup and creating new one")
        database = {}
        path = Path(DATABASE_FILE_PATH)
        name = f"{path.stem}-backup-{datetime.now()}{path.suffix}"
        path.rename(path.with_name(name))

    database[str(datetime.now())] = data

    with open(DATABASE_FILE_PATH, mode="wt", encoding="utf-8") as fd:
        json.dump(database, fd, indent=2)
