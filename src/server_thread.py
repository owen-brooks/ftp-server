"""
Owen Brooks
server_thread.py

This module contains the server thread module, with the dfa for the 
    server client interatction
"""
import socket
import os
import threading

from .utils import *
import random


class ServerThread(threading.Thread):
    def __init__(self, conn, conn_info, user_info, logger):
        """sInit method for server thread."""
        threading.Thread.__init__(self)
        self._client_ip = conn_info[0]
        self._client_port = conn_info[1]
        self._user_info = user_info
        self._logger = logger
        self._conn = conn
        self._username = None
        self._auth = False
        self._data_conn = None
        self._logger.info(
            f"ServerThread::__init__: starting thread for client | ip: {self._client_ip}, port: {self._client_port}")

    def login_required(func):
        """Decorator that protects resources that need authentication"""

        def wrapper(self, *args):
            if self._auth:
                return func(self, *args)
            return 530, "Please login with USER and PASS"
        return wrapper

    def data_conn_required(func):
        """Decorator that checks for data connection"""

        def wrapper(self, *args):
            if self._data_conn:
                return func(self, *args)
            return 425, "Use PORT or PASV first."
        return wrapper

    def _send(self, code, msg):
        """Sends data on control channel

        :param code: ftp code
        :param msg: ftp msg
        :return: None
        """
        code = str(code)
        self._logger.info(
            f"ServerThread::_send: | ip: {self._client_ip}, port: {self._client_port} response: {code} {msg}")
        self._conn.send(f"{code} {msg}\r\n".encode())

    def _send_data(self, data):
        """Handles sending data, and closing data channel

        :param data:
        :return: Bool based on result of transfer
        """
        self._logger.info(
            f"ServerThread::_send_data: | ip: {self._client_ip}, port: {self._client_port}")
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(self._data_conn)
            if self._data_conn[1]:
                data_socket.connect((self._client_ip, self._data_conn[0]))
            else:
                (data_socket, _) = self._data_conn[0].accept()
        except Exception as e:
            self._logger.info(e)
            self._data_conn = None
            return False

        data_socket.sendall((data + "\r\n").encode())
        data_socket.close()
        self._data_conn = None
        return True

    def _get_data(self):
        """Handles getting data, and closing data channel

        :param data:
        :return: Data or None
        """
        self._logger.info(
            f"ServerThread::_send_data: | ip: {self._client_ip}, port: {self._client_port}")
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(self._data_conn)
            if self._data_conn[1]:
                data_socket.connect((self._client_ip, self._data_conn[0]))
            else:
                (data_socket, _) = self._data_conn[0].accept()
        except Exception as e:
            self._logger.info(e)
            self._data_conn = None
            return None
        data = ""
        temp = data_socket.recv(2048)
        while temp:
            data += temp.decode()
            temp = data_socket.recv(2048)
        data_socket.close()
        self._data_conn = None
        return data

    def _user(self, request):
        """Handles USER cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 2:
            return 501, "Invalid args."
        if self._auth:
            return 331, "Can't change to another user."
        self._username = request[1]
        if not self._auth:
            return 331, "Specify the password."
        else:
            raise ValueError(self._auth)

    def _pass(self, request):
        """Handles PASS cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 2:
            return 501, "Invalid args."
        if not self._user:
            return 503, "Login with USER first"
        if self._auth:
            return 230, "Already logged in."
        try:
            if self._user_info[self._username] == request[1]:
                self._auth = True
                return 230, "Login successfull."
        except:
            pass
        return 530, "Login incorrect."

    @login_required
    def _cwd(self, request):
        """Handles CWD cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        try:
            os.chdir(" ".join(request[1:]))
            return 250, "Dir changed."
        except:
            pass
        return 550, "Failed to change dir."

    @login_required
    def _pwd(self, request):
        """Handles PWD cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 1:
            return 501, "Invalid args."
        return 257, f"'{os.getcwd()}' is the current dir."

    @login_required
    def _cdup(self, request):
        """Handles CDUP cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 1:
            return 501, "Invalid args."
        try:
            os.chdir("..")  # move back one folder
        except Exception as e:
            self._logger(e)
            return 550, "Failed to change dir."
        return 200, "OK"

    @login_required
    def _pasv_epsv(self, request):
        """Handles PASV and EPSV cmds

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 1:
            return 501, "Invalid args."
        port = random.randint(1024, 65000)
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(("localhost", port))
        data_socket.listen(1)
        self._data_conn = (data_socket, False)
        if request[0].upper() == "PASV":
            return 227, build_pasv_resp(port)
        else:
            return 229, build_epsv_resp(port)

    @login_required
    def _port_eprt(self, request):
        """Handles PORT and EPRT cmds

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) == 2:
            if request[0].upper() == "PORT":
                port = parse_port_cmd(request[1])
                self._data_conn = (port, True)
                return 200, "PORT cmd successfull."
            else:
                port = parse_eprt_cmd(request[1])
                self._data_conn = (port, True)
                return 200, "EPRT cmd successfull"
        return 501, "Invalid args."

    @data_conn_required
    @login_required
    def _retr(self, request):
        """Handles RETR cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) == 1:
            return 501, "Invalid args."
        try:
            file_data = open(" ".join(request[1:]), 'r').read()
        except Exception as e:
            return 550, "Failed to open file."
        self._send(150, "Sending file.")
        if self._send_data(file_data):
            return 226, "Transfer complete."
        return 426, "Data transfer failed."

    @data_conn_required
    @login_required
    def _stor(self, request):
        """Handles STOR cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) == 1:
            return 501, "Invalid args."
        f = open(" ".join(request[1:]), 'w')
        self._send(150, "OK to send data.")
        data = self._get_data()
        if data:
            f.write(data)
            f.close()
            return 226, "Transfer complete."
        return 426, "Data transfer failed."

    @data_conn_required
    @login_required
    def _list(self, request):
        """Handles LIST cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        dir_list = ""
        try:
            if len(request) > 1:
                dir_list = "\n".join(os.listdir(" ".join(request[1:])))
            else:
                dir_list = "\n".join(os.listdir())
        except Exception as e:
            self._logger.info(e)
            pass
        self._send(150, "Sending dir listing.")
        if self._send_data(dir_list):
            return 226, "Transfer complete."
        return 426, "Data transfer failed."

    def _quit(self, request):
        """Handles QUIT cmd

        :param request: list of words in request
        :return: tuple (code, msg)
        """
        if len(request) != 1:
            return 501, "Invalid args."
        return 221, "Goodbye"

    def _run_ftp_cmd(self, request):
        self._logger.info(
            f"ServerThread::_run_ftp_cmd: | ip: {self._client_ip}, port: {self._client_port} request: {request}")

        fns = {"USER": self._user, "PASS": self._pass,
               "QUIT": self._quit, "LIST": self._list,
               "STOR": self._stor, "RETR": self._retr,
               "PORT": self._port_eprt, "EPRT": self._port_eprt,
               "PASV": self._pasv_epsv, "EPSV": self._pasv_epsv,
               "CWD": self._cwd, "PWD": self._pwd,
               "CDUP": self._cdup}
        request = parse_client_request(request)
        try:
            return fns[request[0].upper()](request)
        except KeyError:
            return 500, "Command unknown."

    def run(self):
        """Contains the thread’s activity.

        See https://docs.python.org/3/library/threading.html#threading.Thread.run
        """
        keep_alive = True
        print
        self._send(220, "Welcome to Owen's FTP Server")
        while keep_alive:
            data = self._conn.recv(2048)
            if data:
                code, msg = self._run_ftp_cmd(data)
                if code:
                    self._send(code, msg)
                if code == 221:
                    keep_alive = False
        self._conn.close()
        if self._data_conn:
            self._data_conn.close()
        self._logger.info(
            f"ServerThread::run: closing thread | ip: {self._client_ip}, port: {self._client_port}")
