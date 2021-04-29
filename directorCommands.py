"""
A Collection of commands that may only be used by admins.
To add to the list of admins, you must edit the config.ini
"""

import discord.errors
from discord.ext import commands

from utilities import ADMINS, ConfigEdit, logger


class AdminCommands(commands.Cog, name="Director Commands"):
    """A set of commands that may only be used by Directors"""

    @commands.command()
    async def offres(self, ctx, restriction_level='closed'):
        """
        Command that changes Director's Channel's access
        Accepted levels are:
        open- anyone may join
        closed- no-one may join
        wl- only whitelisted members may join
        res- Only whitelisted members may join, so long as no Director is already in the channel
        """
        await ctx.message.delete()
        if ctx.author.name not in ADMINS:
            return

        restriction_level = restriction_level.lower()

        if restriction_level == 'closed':
            ConfigEdit.set('OFFICER', 'restrictionlevel', 'closed')
            await ctx.send(":x: The Director's Channel access is now **__Closed__**", delete_after=5)
        elif restriction_level == 'res':
            ConfigEdit.set('OFFICER', 'restrictionlevel', 'restricted')
            await ctx.send(":exclamation: The Director's Channel access is now **__Restricted__**", delete_after=5)
        elif restriction_level == 'wl':
            ConfigEdit.set('OFFICER', 'restrictionlevel', 'whitelist')
            await ctx.send(":warning: The Director's Channel access is now **__Whitelist Only__**", delete_after=5)
        elif restriction_level == 'open':
            ConfigEdit.set('OFFICER', 'restrictionlevel', 'open')
            await ctx.send(":white_check_mark: The Director's Channel access is now **__Open__**", delete_after=5)
        else:
            ConfigEdit.set('OFFICER', 'restrictionlevel', 'closed')
            await ctx.send(":x: The Director's Channel access is now **__Closed__**", delete_after=5)

    @commands.command()
    async def addwl(self, ctx, member_name):
        """
        Adds a member to the whitelist. Make sure to ping them when adding.
        """
        await ctx.message.delete()
        if ctx.author.name != 'mnycz04':
            await ctx.send("**You can't use that!**")

        current_wl: list = ConfigEdit.read("OFFICER", "whitelistedpeople").split(', ')
        for member in ctx.guild.members:
            if str(member_name) == f'<@!{member.id}>':
                current_wl.append(member.name)
                break
        else:
            await ctx.send('**Error in adding member, make sure you @ them.**', delete_after=5)
            return
        current_wl = list(set(current_wl))
        ConfigEdit.set('OFFICER', 'whitelistedpeople', ', '.join(current_wl))

    @commands.command()
    async def remwl(self, ctx, member_name):
        """
        Removes a member from the whitelist. Makes sure to ping who ever you're removing.
        """
        await ctx.message.delete()
        if ctx.author.name != 'mnycz04':
            await ctx.send("**You can't use that!**")

        current_wl: list = ConfigEdit.read("OFFICER", "whitelistedpeople").split(', ')

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

        current_wl: list = list(set(current_wl))
        ConfigEdit.set('OFFICER', 'whitelistedpeople', ', '.join(current_wl))

    @commands.command(aliases=['delete'])
    async def purge(self, ctx, limit="""10"""):
        """
        Purges a set number of messages from this channel, default value is 10, but this can be changed.
        """
        if ctx.message.author.name not in ADMINS:
            return
        logger.info(f"{ctx.author.name} has requested a purge of {ctx.channel.name} in guild {ctx.guild.name}, " +
                    f"id {ctx.guild.id}, for {limit} messages.")
        try:
            limit = int(limit)
            await ctx.message.delete()
            await ctx.channel.purge(limit=limit + 1, bulk=True)
            logger.info(f"{limit} messages purged.")
            await ctx.send(f"Purged {limit} messages!", delete_after=3)
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
