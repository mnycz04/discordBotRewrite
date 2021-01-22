"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""

import discord
from discord.ext import commands

import token

__version__ = '0.1'

# Sets up intents of bot
# Bot requires the .member and .messages intent
intents = discord.Intents.default()
intents.messages = True
intents.members = True

# Creates the bot with configured intents and assigns prefix
client = commands.Bot(command_prefix='$', intents=intents)


@client.event
async def on_ready():
    """
    Event on_ready:
    called when the bot has successfully connected to discord API,
    and is also ready for commands and to retrieve events.
    :returns: None
    """
    print('Bot Connected, and ready.')
    return None


# Server issued commands:


# Runs the bot with private token from token.TOKEN
client.run(token.TOKEN)
