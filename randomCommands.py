"""
Collection of commands that use a RNG to determine an output

Commands:
roll- sends a percentage from 0%-100%
sentence- random sentence generator
reddit- returns random post from a subreddit
"""

import random

import random_word
from discord import embeds
from discord.ext import commands

from utilities import get_reddit_post, logger


class RandomCommands(commands.Cog, name="Random Commands"):
    """
    Collection of commands that use a RNG to determine an output

    Commands:
    roll- sends a percentage from 0%-100%
    sentence- random sentence generator
    reddit- returns random post from a subreddit
    """

    @commands.command()
    async def roll(self, ctx, *, message=None):
        """
        Sends a random percentage between 0 and 100, along with a message.
        """
        await ctx.message.delete()
        message = ''.join(message)
        await ctx.send(f"{message} {round(random.random() * 100, 2)}%", delete_after=10)

    @commands.command()
    async def sentence(self, ctx, length):
        """
        Returns a sentence of randomly generated words of <length> words long.
        """
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

    @commands.command(aliases=['red', 'r'])
    async def reddit(self, ctx, *, subreddit=None):
        """
        Gets a random post from a specified subreddit.
        """
        await ctx.message.delete()
        subreddit: str = ''.join(subreddit).lower().replace(' ', '')
        logger.info(f"{ctx.author.name} in guild {ctx.guild.name}, " +
                    f"id {ctx.guild.id} requested a random post from r/{subreddit}.")
        try:
            post = await get_reddit_post(subreddit)
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
                embed = embeds.Embed(title=post.title, url=post.shortlink)
                if '.jpg' in post.url:
                    embed.set_image(url=post.url)
                elif ('v.redd.it' in post.url) or ('youtu' in post.url):
                    video = True
                embed.set_author(name=post.author.name)
                embed.set_footer(text=f'r/{subreddit}')
                await ctx.send(embed=embed)
                if video:
                    await ctx.send(post.url)
