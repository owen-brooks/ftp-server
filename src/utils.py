"""
Owen Brooks
utils.py

This module provides helper functions
"""
import socket


def is_num(num):
    """check if num is a digit

    :param num: string
    :return : boolean
    """
    try:
        int(num)
    except ValueError:
        return False
    return True


def parse_args(args):
    """parse command line args

    :param args: list of command line args
    :return : tuple (log file, port)
    """
    if len(args) != 2:
        raise ValueError(
            f"Incorrect args usage is python run.py <logfile> <port> | args: {args}")

    log_file = args[0]
    if not is_num(args[1]):
        raise ValueError(f"Not a valid port number | port: {args[2]}")

    port = int(args[1])
    return log_file, port


def parse_client_request(resp):
    """parse response from ftp server

    :param resp: full text of request
    :return: 
    """
    resp = resp.decode()
    resp = resp.rstrip()
    return resp.split(" ")


def parse_port_cmd(cmd):
    """parse cmd string for port cmd

    :param cmd: cmd
    :return: port
    """

    cmd = (cmd.split(","))  # make host comma delimited
    return (int(cmd[-2]) * 256) + int(cmd[-1])


def parse_eprt_cmd(cmd):
    """parse cmd string for eprt cmd

    :param cmd: cmd
    :return: port
    """
    c = cmd.split("|")[::-1]
    for i in c:
        if is_num(i):
            return int(i)


def build_pasv_resp(port):
    """build pasv resp from port #

    :param resp: response from ftp server
    :return: port number
    """
    (_, _, ip) = socket.gethostbyaddr(socket.gethostname())
    ip = ",".join(ip[0].split("."))
    p1 = port // 256
    p2 = port - (256*p1)
    return f"Entering PASV mode ({ip},{p1},{p2})."


def build_epsv_resp(port):
    """build epsv resp from port #

    :param resp: response from ftp server
    :return: port number
    """
    return f"Entering EPSV mode (|||{port}|)"
