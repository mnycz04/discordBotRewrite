"""
A collection of several useful functions, as well as variables from the config
"""

import configparser
import logging
import socket

import praw

config = configparser.ConfigParser()
config.read('config.ini')

ADMINS: frozenset = frozenset(config['ADMIN']['admins'].split(', '))

logger = logging.getLogger()
_logFormatter = logging.Formatter("[%(name)s - %(levelname)s - %(asctime)s]: %(message)s",
                                  datefmt="%a %d-%b-%Y %H:%M:%S")
_fileHandler = logging.FileHandler(f"bot_log.txt")
_fileHandler.setFormatter(_logFormatter)
logger.addHandler(_fileHandler)
_consoleHandler = logging.StreamHandler()
_consoleHandler.setFormatter(_logFormatter)
logger.addHandler(_consoleHandler)
logger.setLevel(20)

r = praw.Reddit(client_id='X0VJq7wE00FEYQ',
                client_secret='oQ09GcBauKxPxN2su0o18Xb_EqC6vw',
                user_agent='windows:mnycz04.discord:v1.5.3 (by /u/mnycz04; mnycz04@gmail.com)')


class ConfigEdit:

    @staticmethod
    def read(section_name, value_name) -> str:
        """
        :param section_name: The section of the ini
        :param value_name: The key name
        :returns: A string of the requested key's value
        """
        return config.get(section_name, value_name)

    @staticmethod
    def set(section_name, value_name, new_value) -> None:
        """
        :param section_name: The section of the ini file
        :param value_name: The value which will be changed
        :param new_value: The new value
        """
        config.set(section_name, value_name, new_value)
        with open('config.ini', 'w') as file:
            config.write(file)


async def _purge(ctx, limit) -> None:
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit + 1, bulk=True)


async def check_for_officer(ctx) -> bool:
    """
    Checks for an officer in Officer Channel
    :return: If there is an officer, returns True, else returns False
    """
    for channel in ctx.guild.voice_channels:
        for member in channel.members:
            if member.name in ADMINS and channel.name == "Director's Channel":
                return True
    return False


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


async def get_reddit_post(subreddit):
    """
    Gets a random submission in a given subreddit
    :param subreddit: The subreddit's name to search for
    :returns object: Returns a post object.
    """
    subs = r.subreddits.search_by_name(subreddit)
    if not subs:
        raise LookupError
    else:
        pass

    post = subs[0].random()
    if post is None:
        raise ConnectionRefusedError
    else:
        return post
