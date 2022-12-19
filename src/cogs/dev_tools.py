import asyncio
from os import listdir
import requests

import discord
from discord.ext import commands

from cogs.utils import embed_templates


class DevTools(commands.Cog):
    """Commands for developers to mangage cogs and other functionality of the bot"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='custommsg', description='Send a message to any channel in any server the bot is in')
    async def custommsg(self, ctx: commands.Context, channel: int, *text: tuple[str]):
        """
        Send a message to any channel on any server the bot is in

        Parameters
        ----------
        ctx (commands.Context): Context object
        channel (int): The channel ID to send the message to
        text (tuple[str]): The text to send
        """

        # Send message to the requested channel
        channel = self.bot.get_channel(channel)
        custommessage = ' '.join(text)
        await channel.send(custommessage)

        # Send confirmation message to the invoker
        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Sent', value=custommessage)
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command(name='changepresence', description='Change the bot\'s Discord presence status')
    async def changepresence(self, ctx: commands.Context, activity_type: str, message: str, status_type: str):
        """
        Change the bot's presence status

        Parameters
        ----------
        ctx (commands.Context): Context object
        activity_type (str): The type of activity to set the bot's status to
        message (str): The message to set the bot's status to
        status_type (str): The type of status to set the bot's status to
        """

        activities = {
            'playing': 0,
            'listening': 2,
            'watching': 3
        }
        activity_type = activities.get(activity_type, 0)

        status_types = {
            'online': discord.Status.online,
            'dnd': discord.Status.dnd,
            'idle': discord.Status.idle,
            'offline': discord.Status.offline
        }
        status_type = status_types.get(status_type, discord.Status.online)

        await self.bot.change_presence(
            status=status_type,
            activity=discord.Activity(type=activity_type, name=message)
        )

        embed = discord.Embed(color=ctx.me.color, description='Presence changed')
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.command(name='leave', description='Leave a guild. If none is specified, leave the current guild')
    async def leave(self, ctx: commands.Context, *guild_id: int):
        """
        Make bot leave a specified guild. If no guild is specified, leave the guild the command was sent from

        Parameters
        ----------
        ctx (commands.Context): Context object
        guild_id (int): The ID of the guild to leave
        """

        # If no guild id is specified, leave the current guild
        guild_id = guild_id if guild_id else ctx.guild.id

        # Get guild
        try:
            guild = await self.bot.fetch_guild(guild_id)
        except discord.errors.Forbidden:
            embed = embed_templates.error_fatal(ctx, text='Bot is not a member of this guild')
            return await ctx.reply(embed=embed)

        # Send confirmation message for leaving
        confirmation_msg = await ctx.reply(f'Do you want to leave {guild.name} (`{guild.id}`)?')
        await confirmation_msg.add_reaction('✅')

        # Check confirmation
        def comfirm(reaction: discord.Reaction, user: discord.Member):
            return user == ctx.author and str(reaction.emoji) == '✅'

        try:
            await self.bot.wait_for('reaction_add', timeout=15.0, check=comfirm)
        except asyncio.TimeoutError:
            await ctx.message.delete()
            await confirmation_msg.delete()
        else:
            await guild.leave()
            try:
                embed = discord.Embed(color=ctx.me.color, description='Guild left!')
                await ctx.reply(embed=embed)
            except discord.errors.Forbidden:
                pass

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='publicip', description='Get the public IP address of the bot\'s host')
    async def publicip(self, ctx: commands.Context):
        """
        Sends WAN IP-address. Inb4 I leak my IP-address

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        data = requests.get('https://wtfismyip.com/json', timeout=10).json()
        ip = data['YourFuckingIPAddress']
        location = data['YourFuckingLocation']
        isp = data['YourFuckingISP']

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='WAN IP-address', value=f'{ip}\n{location}\n{isp}')
        await ctx.reply(embed=embed)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.group(name='cogs', description='Manage cogs')
    async def cogs(self, ctx: commands.Context):
        """
        Cog management commands

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        if not ctx.invoked_subcommand:
            await ctx.reply_help(ctx.command)

    @cogs.command(name='unload')
    async def cogs_unload(self, ctx: commands.Context, cog: str):
        """
        Disables a specified cog

        Parameters
        ----------
        ctx (commands.Context): Context object
        cog (str): The name of the cog to disable
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.unload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been disabled')
                    return await ctx.reply(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.reply(embed=embed)

    @cogs.command(name='load')
    async def cogs_load(self, ctx: commands.Context, cog: str):
        """
        Enables a speicifed cog

        Parameters
        ----------
        ctx (commands.Context): Context object
        cog (str): The name of the cog to enable
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.load_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} loaded')
                    return await ctx.reply(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.reply(embed=embed)

    @cogs.command(name='reload')
    async def cogs_reload(self, ctx: commands.Context, cog: str):
        """
        Reloads a specified cog

        Parameters
        ----------
        ctx (commands.Context): Context object
        cog (str): The name of the cog to reload
        """
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    await self.bot.reload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been reloaded')
                    return await ctx.reply(embed=embed)

        embed = embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.reply(embed=embed)

    @cogs.command(name='reloadunloaded')
    async def cogs_reloadunloaded(self, ctx: commands.Context):
        """
        Reloads all cogs, including previously disabled ones

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        # Unload all cogs
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.unload_extension(f'cogs.{name}')

        # Load all cogs
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.load_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all cogs')
        await ctx.reply(embed=embed)

    @cogs.command(name='reloadall')
    async def cogs_reloadall(self, ctx: commands.Context):
        """
        Reloads all previously enabled cogs

        Parameters
        ----------
        ctx (commands.Context): Context object
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await self.bot.reload_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all previously enabled cogs')
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(DevTools(bot))

