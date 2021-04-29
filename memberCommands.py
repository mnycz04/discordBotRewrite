"""
Collection of commands that any member may use
"""
import discord
from discord.ext import commands

from utilities import ConfigEdit, check_for_officer, logger, ping as _ping


class MemberCommands(commands.Cog, name="Member Commands"):
    """
    A set of commands that are accessible to any member.
    """

    @commands.command()
    async def ping(self, ctx, ip="173.70.56.251", port="25565"):
        """
        Pings an IP on a specified port.
        """
        await ctx.message.delete()

        try:
            port = int(port)
        except ValueError:
            logger.info("Invalid port argument")
            await ctx.send("Invalid port.", delete_after=5)
            return

        logger.info(f"{ctx.author.name} in guild {ctx.guild.name}, id {ctx.guild.id} pinged {ip}:{port}.")
        if await _ping(ip, port):
            await ctx.send("Connection successful!", delete_after=5)
        else:
            await ctx.send("Connection failed!", delete_after=5)

    @commands.command()
    async def officer(self, ctx):
        """
        Moves you to the Director's Channel,
        assuming you have the correct permissions and the channel is open
        """
        await ctx.message.delete()
        logger.info(f"{ctx.message.author} used the officer command in guild {ctx.guild.name}, id {ctx.guild.id}.")
        whitelisted_members = frozenset(ConfigEdit.read("OFFICER", "whitelistedpeople").split(', '))
        restrictionlevel = ConfigEdit.read("OFFICER", "restrictionlevel")

        officer_channel = discord.utils.get(ctx.guild.voice_channels, name=ConfigEdit.read("ADMIN", "adminchannel"))

        if restrictionlevel == 'closed':
            await ctx.send("**The Director's Channel is currently closed, ask a Director to move you.**",
                           delete_after=5)
            return

        elif restrictionlevel == 'restricted':
            if ctx.author.name in whitelisted_members and await check_for_officer(ctx):
                await ctx.send("**The Director's Channel is restricted, and a Director is in there," +
                               " ask them to move you.**",
                               delete_after=5)
            elif ctx.author.name in whitelisted_members:
                await ctx.send("Moved!", delete_after=2)
                await ctx.author.move_to(officer_channel)
            else:
                await ctx.send("**The Director's Channel is currently closed, ask a Director to move you.**",
                               delete_after=5)
            return

        elif restrictionlevel == 'whitelist':
            if ctx.author.name in whitelisted_members:
                await ctx.author.move_to(officer_channel)
                await ctx.send("Moved!", delete_after=2)
            else:
                await ctx.send("**The Director's Channel is currently closed, ask a Director to move you.**",
                               delete_after=5)
            return

        elif restrictionlevel == 'open':
            await ctx.send("Moved!", delete_after=3)
            await ctx.author.move_to(officer_channel)
