from multiprocessing import Process
from http_server import httpd_run
from socket_server import socket_receive, check_data_file


def run_app():
    check_data_file()
    http_server = Process(target=httpd_run, kwargs={"port": 3000})
    http_server.start()
    socket_server = Process(target=socket_receive)
    socket_server.start()
    http_server.join()
    socket_server.join()


if __name__ == "__main__":
    run_app()
