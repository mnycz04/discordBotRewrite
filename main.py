"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""
import logging
import random

import discord
from discord.ext import commands
import random_word
import configparser

import mytoken
from reddit import get_reddit_post
from schedule import check_time
from serverPing import ping as tcp_ping

__version__ = '1.0'

config = configparser.ConfigParser()
config.read('config.ini')

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


async def check_for_officer(ctx):
    """
    Checks for an officer in Officer Channel
    :return: If there is an officer, returns True, else returns False
    """
    _officer_list = ["SeatedEquation", "mnycz04"]
    for channel in ctx.guild.voice_channels:
        for member in channel.members:
            if member.name in _officer_list and channel.name == "Officer Channel":
                return True
    return False


def setconfig(section_name, value_name, new_value):
    config.set(section_name, value_name, new_value)
    with open('config.ini', 'w') as file:
        config.write(file)


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


@client.command()
async def sentence(ctx, length):
    await ctx.message.delete()
    try:
        length = int(length)
        if length > 20:
            raise OverflowError
    except ValueError:
        await ctx.send("Invalid 'length parameter'!", delete_after=5)
        return
    except OverflowError:
        await ctx.send("Length is too large, keep it under 20.", delete_after=5)
        return
    logger.info(f"{ctx.author.name} in guild {ctx.guild.name}, id {ctx.guild.id} used the 'sentence command'")
    randomwords = random_word.RandomWords()

    random_sentence = ""
    for i in range(length):
        pos = random.choice(["noun", "verb", "adjective", "adverb"])
        random_sentence += f'{randomwords.get_random_word(includePartOfSpeech=pos)} '
    await ctx.send(f"{random_sentence.strip()}!", delete_after=15)


@client.command()
async def officer(ctx):
    await ctx.message.delete()
    logger.info(f"{ctx.message.author} used the officer command in guild {ctx.guild.name}, id {ctx.guild.id}.")
    _whitelisted_members = config['OFFICER']['whitelistedpeople'].split(', ')
    restrictionlevel = config['OFFICER']['restrictionlevel']

    for channel in ctx.guild.voice_channels:  # Find the officer channel's discord object
        if channel.name == "Officer Channel":
            _officer_channel = channel

    if restrictionlevel == 'closed':
        await ctx.send("**The Officer Channel is currently closed, ask an Operator to move you.**", delete_after=5)
        return

    elif restrictionlevel == 'restricted':
        if ctx.author.name in _whitelisted_members and await check_for_officer(ctx):
            await ctx.send("**The Officer Channel is restricted, and an operator is in there, ask them to move you.**",
                           delete_after=5)
        elif ctx.author.name in _whitelisted_members:
            await ctx.send("Moved!", delete_after=2)
            await ctx.author.move_to(_officer_channel)
        else:
            await ctx.send("**The Officer Channel is currently closed, ask an Operator to move you.**", delete_after=5)
        return

    elif restrictionlevel == 'whitelist':
        if ctx.author.name in _whitelisted_members:
            await ctx.author.move_to(_officer_channel)
            await ctx.send("Moved!", delete_after=2)
        else:
            await ctx.send("**The Officer Channel is currently closed, ask an Operator to move you.**", delete_after=5)
        return

    elif restrictionlevel == 'open':
        await ctx.send("Moved!", delete_after=3)
        await ctx.author.move_to(_officer_channel)


@client.command()
async def offres(ctx, restriction_level='closed'):
    """
    :param obj ctx:
    :param str restriction_level:
    :return:
    """
    await ctx.message.delete()
    admins = ['mnycz04', 'SeatedEquation']
    if ctx.author.name not in admins:
        return

    restriction_level = restriction_level.lower()

    if restriction_level == 'closed':
        setconfig('OFFICER', 'restrictionlevel', 'closed')
        await ctx.send(":x: The Officer Channel access is now **__Closed__**", delete_after=5)
    elif restriction_level == 'res':
        setconfig('OFFICER', 'restrictionlevel', 'restricted')
        await ctx.send(":exclamation: The Officer Channel access is now **__Restricted__**", delete_after=5)
    elif restriction_level == 'wl':
        setconfig('OFFICER', 'restrictionlevel', 'whitelist')
        await ctx.send(":warning: The Officer Channel access is now **__Whitelist Only__**", delete_after=5)
    elif restriction_level == 'open':
        setconfig('OFFICER', 'restrictionlevel', 'open')
        await ctx.send(":white_check_mark: The Officer Channel access is now **__Open__**", delete_after=5)
    else:
        setconfig('OFFICER', 'restrictionlevel', 'closed')
        await ctx.send(":x: The Officer Channel access is now **__Closed__**", delete_after=5)


@client.command()
async def addwl(ctx, member_name):
    """
    :param ctx:
    :param str member_name:
    :return:
    """
    await ctx.message.delete()
    if ctx.author.name != 'mnycz04':
        await ctx.send("**You can't use that!**")

    current_wl = config['OFFICER']['whitelistedpeople'].split(', ')
    for member in ctx.guild.members:
        if str(member_name) == f'<@!{member.id}>':
            current_wl.append(member.name)
            break
    else:
        await ctx.send('**Error in adding member, make sure you @ them.**', delete_after=5)
        return
    current_wl = list(set(current_wl))
    setconfig('OFFICER', 'whitelistedpeople', ', '.join(current_wl))


@client.command()
async def remwl(ctx, member_name):
    """
    :param ctx:
    :param str member_name:
    :return:
    """
    await ctx.message.delete()
    if ctx.author.name != 'mnycz04':
        await ctx.send("**You can't use that!**")

    current_wl = config['OFFICER']['whitelistedpeople'].split(', ')

    for member in ctx.guild.members:
        if str(member_name) == f'<@!{member.id}>':
            guild_members_name = member.name
            break
    else:
        await ctx.send('**Error in adding member, make sure you @ them.**', delete_after=5)
        return

    for name in current_wl:
        if name == guild_members_name:
            current_wl.remove(name)

    current_wl = list(set(current_wl))
    setconfig('OFFICER', 'whitelistedpeople', ', '.join(current_wl))


# Runs the bot with private token from token.TOKEN
client.run(mytoken.TOKEN)
