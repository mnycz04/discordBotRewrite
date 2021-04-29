"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""

import discord
from discord.ext import commands

import directorCommands
import memberCommands
import mytoken
import randomCommands
from utilities import ConfigEdit, logger

# Sets up intents of bot
# Bot requires the .member and .messages intent
intents = discord.Intents.default()
intents.messages = True
intents.members = True

# Creates the bot with configured intents and assigns prefix
client = commands.Bot(command_prefix=ConfigEdit.read("DEFAULT", "commandprefix"), intents=intents)


@client.event
async def on_ready() -> None:
    """
    Event on_ready:
    called when the bot has successfully connected to discord API,
    and is also ready for commands and to retrieve events.
    :returns: None
    """
    logger.info("Bot connected, and ready.")
    return


# Adds all cogs to bot
client.add_cog(directorCommands.AdminCommands())
client.add_cog(randomCommands.RandomCommands())
client.add_cog(memberCommands.MemberCommands())

# Runs the bot with private token from token.TOKEN
client.run(mytoken.TOKEN)
