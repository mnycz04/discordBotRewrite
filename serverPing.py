"""
Contains function to ping a given IP on a specific port
"""

import socket


async def ping(ip, port):
    """
    Creates TCP connection to given IP on specific port
    :param str ip: The IP to connect to, as a string
    :param int port: The port to create connection through
    :returns bool: If connection is made, returns True, else, returns False
    """
    try:
        socket.create_connection((ip, port), 5)
        return True
    except Exception:
        return False
