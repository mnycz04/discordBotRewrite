"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""
import logging

import discord
from discord.ext import commands

import mytoken

__version__ = '0.1'

# Sets up intents of bot
# Bot requires the .member and .messages intent
intents = discord.Intents.default()
intents.messages = True
intents.members = True

# Creates the bot with configured intents and assigns prefix
client = commands.Bot(command_prefix='$', intents=intents)


# Creates Logger to log events, exceptions, and errors
logFormatter = logging.Formatter("[%(name)s - %(levelname)s - %(asctime)s]: %(message)s",
                                 datefmt="%a %d-%b-%Y %H:%M:%S")
logger = logging.getLogger()

fileHandler = logging.FileHandler(f"bot_log.txt")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(20)


@client.event
async def on_ready():
    """
    Event on_ready:
    called when the bot has successfully connected to discord API,
    and is also ready for commands and to retrieve events.
    :returns: None
    """
    logger.info("Bot connected, and ready.")
    return None


# Server issued commands:


# Runs the bot with private token from token.TOKEN
client.run(mytoken.TOKEN)
