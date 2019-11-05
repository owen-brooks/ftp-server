"""
Owen Brooks
ftp_server.py

This module contains the server module, with the main processing loop
    that starts the threads
"""
import socket
import os
import threading

from .utils import *
from .server_thread import *


class Server:
    """ FTP Server object"""

    def __init__(self, user_info, logger):
        """Init method for ftp server object"""
        self._user_info = user_info
        self._logger = logger
        self.cwd = os.getcwd()
        self._control_socket = None

    def _setup_control_socket(self, port):
        """Create control socket

        :param port: port #
        :return: bool based on success
        """
        self._logger.info(
            f"Server::_setup_control_socket: setting up control channel on port {port}.")
        self._control_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._control_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # make socket reusable
        try:
            self._control_socket.bind(("localhost", port))
        except Exception as e:
            self._logger.info(
                f"Server::_setup_control_socket: failed to setup control socket | port: {port}, error: {e}")
            return False
        self._logger.info(
            f"Server::_setup_control_socket: successfully setup control channel.")
        return True

    def run(self, port):
        """Processing loop for server

        :param port: port #
        """
        if not self._setup_control_socket(port):
            print("Error in setting up control channel ... exiting")
            return

        keep_alive = True
        thread_list = []
        self._control_socket.listen(5)
        print("Listening for connections...")
        try:
            while keep_alive:
                connection, address = self._control_socket.accept()
                print(f"New connection: {address}")
                new_thread = ServerThread(
                    connection, address, self._user_info, self._logger)
                new_thread.start()  # activate the thread objects run() method
                thread_list.append(new_thread)
        except Exception as e:
            print(e)
            pass

        self._control_socket.close()
        [thread.join() for thread in thread_list]
        print("Server exiting ...")
