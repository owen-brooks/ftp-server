"""
Owen Brooks
run.py

This module provides command line connection for the ftp_client module
"""
import json
import sys
import logging

from src.utils import parse_args
from src.ftp_server import Server


log_file, port = parse_args(sys.argv[1:])  # exclude filename

logging.basicConfig(
    filename=log_file, format="%(asctime)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger()

creds = json.load(open('credentials.json', 'r'))


ftp_client = Server(creds, logger)
exit_msg = ftp_client.run(port)
print(exit_msg)
