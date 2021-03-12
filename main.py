"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""
import logging
import random

import discord
from discord.ext import commands

import mytoken
from reddit import get_reddit_post
from schedule import check_time
from serverPing import ping as tcp_ping

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
    return


async def _purge(ctx, limit):
    await ctx.message.delete()
    await ctx.channel.purge(limit=limit + 1, bulk=True)


# Server issued commands:

@client.command()
async def h(ctx, command='none'):
    await ctx.message.delete()
    command = command.lower()
    if command == "reddit":
        embed = discord.Embed(title="Command: Reddit")
        embed.description = """Allow user to retrieve a random new post from a subreddit
                            
                            "$reddit [subreddit]"
                            aliases: r, red"""
    elif command == 'purge':
        embed = discord.Embed(title='Command: Purge')
        embed.description = """Bulk deletes a specified number of messages in a text channel
                            
                            "$purge [number to delete]"
                            aliases: delete
                            Requires the manage messages role"""
    elif command == 'ping':
        embed = discord.Embed(title='Command: Ping')
        embed.description = """Pings a specified IP via TCP on a given port.
        
                            "$ping [IP] [port]"
                            """
    elif command == 'schedule':
        embed = discord.Embed(title='Command: Schedule')
        embed.description = """Returns a school schedule and tells you what period your in
                            
                            "$schedule"
                            aliases: shed"""
    else:
        embed = discord.Embed(title='Help')
        embed.description = """List of Commands:
                            
                            reddit
                            purge
                            ping
                            schedule
                            
                            Use "$help [command name] for more detailed descriptions"
                            """

    await ctx.send(embed=embed)


@client.command(aliases=['red', 'r'])
async def reddit(ctx, *, subreddit=None):
    await ctx.message.delete()
    subreddit = ''.join(subreddit).lower().replace(' ', '')
    logger.info(f"""{ctx.author.name} in guild {ctx.guild.name}, \
id {ctx.guild.id} requested a random post from r/{subreddit}.""")
    try:
        post = await client.loop.create_task(get_reddit_post(subreddit))
        e = False
        return
    except LookupError:
        logger.info(f"{subreddit} was an invalid rub name.")
        await ctx.send(f"{subreddit} was an invalid sub-name", delete_after=5)
        e = True
        return
    except ConnectionRefusedError:
        logger.info(f"{subreddit} does not support .random() function")
        await ctx.send(f"{subreddit} doesn't allow bots to retrieve posts.", delete_after=5)
        e = True
        return
    except Exception:
        logger.exception("Unhandled exception in function get_reddit_post():")
        await ctx.send("There was an unhandled exception in retrieving the post.", delete_after=5)
        e = True
        return
    finally:
        if e is False:
            video = False
            embed = discord.Embed(title=post.title, url=post.shortlink)
            if '.jpg' in post.url:
                embed.set_image(url=post.url)
            elif ('v.redd.it' in post.url) or ('youtu' in post.url):
                video = True
            embed.set_author(name=post.author.name)
            embed.set_footer(text=f'r/{subreddit}')
            await ctx.send(embed=embed)
            if video:
                await ctx.send(post.url)


@client.command(aliases=['delete'])
async def purge(ctx, limit="""10"""):
    if ctx.message.author.name != 'mnycz04':
        return
    logger.info(f"{ctx.author.name} has requested a purge of {ctx.channel.name} in guild {ctx.guild.name}, \
id {ctx.guild.id}, for {limit} messages.")
    try:
        limit = int(limit)
        client.loop.create_task(_purge(ctx, limit))
        logger.info(f"{limit} messages purged.")
        await ctx.send(f"Purged {limit} messages!")
    except discord.Forbidden:
        await ctx.send("I do not have the permission to do that!", delete_after=10)
        logger.info("Permission denied")
    except discord.HTTPException:
        await ctx.send("Error in purging messages.", delete_after=10)
        logger.warning("HTTP error in purging messages.")
    except ValueError:
        await ctx.send("Invalid argument. Please use format $purge [integer].")
        logger.info("Invalid argument.")
    except Exception:
        await ctx.send("Unhandled exception in purging messages", delete_after=10)
        logger.exception("Unhandled exception in function purge():")


@client.command(aliases=['shed'])
async def schedule(ctx):
    """Sends a picture of the school schedule"""
    await ctx.message.delete()
    logger.info(f"{ctx.author.name} has requested the school schedule in guild {ctx.guild.name},\
 id {ctx.guild.id}.")

    embed = discord.Embed(title=f'{check_time().current_period}')
    embed.set_image(url="https://i.imgur.com/IdLNJW0.png")
    embed.set_footer(text=f'{check_time().next_period}')

    await ctx.send(embed=embed, delete_after=15)


@client.command()
async def ping(ctx, ip="CalcCraft.us.to", port="25565"):
    await ctx.message.delete()

    try:
        port = int(port)
    except ValueError:
        logger.info("Invalid port argument")
        await ctx.send("Invalid port.", delete_after=5)
        return

    logger.info(f"{ctx.author.name} in guild {ctx.guild.name}, id {ctx.guild.id} pinged {ip}:{port}.")
    if await tcp_ping(ip, port):
        await ctx.send("Connection successful!", delete_after=5)
    else:
        await ctx.send("Connection failed!", delete_after=5)


@client.command()
async def roll(ctx, *, message=None):
    await ctx.message.delete()
    message = ''.join(message)
    await ctx.send(f"{message} {round(random.random() * 100, 2)}%", delete_after=10)


# Runs the bot with private token from token.TOKEN
client.run(mytoken.TOKEN)
