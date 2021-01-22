"""
Discord Bot Rewrite

For a list of commands, and how to use them, see the README

"""
import logging

import discord
from discord.ext import commands

import mytoken
from reddit import get_reddit_post
from schedule import check_time

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
    await ctx.channel.purge(limit=limit, bulk=True)

# Server issued commands:


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


# Runs the bot with private token from token.TOKEN
client.run(mytoken.TOKEN)
