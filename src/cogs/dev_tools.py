from discord.ext import commands
import discord

import asyncio
from sys import exit
from os import listdir, system
import socket
from requests import get

from cogs.utils import misc_utils, embed_templates


class DevTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def shutdown(self, ctx):
        """
        Log out and shut down the bot
        """

        embed = discord.Embed(color=ctx.me.color, description='Shutting down...')
        await ctx.send(embed=embed)
        await self.bot.logout()
        exit('Bot stopped through command')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def custommsg(self, ctx, channel: int, *text):
        """
        Send a message to a specified channel
        """

        channel = self.bot.get_channel(channel)
        custommessage = ' '.join(text)
        await channel.send(custommessage)

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Sent', value=custommessage)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['listservers'])
    async def listguilds(self, ctx, page=0):
        """
        Lists all guilds the bot is a member of
        """

        guild_list = [f'{guild.name} - {guild.id}' for guild in self.bot.guilds]

        page_data = misc_utils.paginator(guild_list, int(page))
        page = page_data['page']
        pagecount = page_data['pagecount']
        guilds = '\n'.join(page_data['page_content'])

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Guilds', value=guilds)
        embed.set_footer(text=f'page: {page}/{pagecount}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def listusers(self, ctx, page=0):
        """
        Lists all users the bot has access to
        """

        user_list = [f'{user.name}#{user.discriminator} - {user.id}' for user in self.bot.users]
        page_data = misc_utils.paginator(user_list, int(page))

        pagecount = page_data['pagecount']
        page = page_data['page']
        users = '\n'.join(page_data['page_content'])

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Users', value=users)
        embed.set_footer(text=f'page: {page}/{pagecount}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(alises=['unloadcog', 'disablecog'])
    async def unload(self, ctx, cog: str):
        """
        Disables a specified cog
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    self.bot.unload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been disabled')
                    return await ctx.send(embed=embed)

        embed = await embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['loadcog', 'enablecog'])
    async def load(self, ctx, cog):
        """
        Enables a speicifed cog
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    self.bot.load_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} loaded')
                    return await ctx.send(embed=embed)

        embed = await embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['reloadcog'])
    async def reload(self, ctx, cog):
        """
        Reloads a specified cog
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    self.bot.reload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been reloaded')
                    return await ctx.send(embed=embed)

        embed = await embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def reloadcommand(self, ctx, cog):
        """
        Reloads a specified cog
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                if name == cog:
                    self.bot.reload_extension(f'cogs.{name}')
                    embed = discord.Embed(color=ctx.me.color, description=f'{cog} has been reloaded')
                    return await ctx.send(embed=embed)

        embed = await embed_templates.error_fatal(ctx, text=f'{cog} does not exist')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['reloadunloadedcogs'])
    async def reloadunloaded(self, ctx):
        """
        Reloads all cogs, including previously disabled ones
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.unload_extension(f'cogs.{name}')

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.load_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all cogs')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['reloadallcogs'])
    async def reloadall(self, ctx):
        """
        Reloads all previously enabled cogs
        """

        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.reload_extension(f'cogs.{name}')

        embed = discord.Embed(color=ctx.me.color, description='Reloaded all previously enabled cogs')
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def cmd(self, ctx, *, command: str):
        """
        Execute terminal commands
        """

        system(command)
        await ctx.send('Done!')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def localip(self, ctx):
        """
        Sends LAN IP-address
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='LAN IP-address', value=s.getsockname()[0])
        await ctx.send(embed=embed)
        s.close()

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def publicip(self, ctx):
        """
        Sends WAN IP-address
        inb4 I leak my IP-address
        """

        data = get('https://wtfismyip.com/json').json()
        ip = data['YourFuckingIPAddress']
        location = data['YourFuckingLocation']
        isp = data['YourFuckingISP']

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='WAN IP-address', value=f'{ip}\n{location}\n{isp}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command()
    async def changepresence(self, ctx, activity_type, message, status_type):
        """
        Changes presence status
        """

        activities = {
            'playing': 0,
            'listening': 2,
            'watching': 3
        }
        if activity_type in activities:
            activity_type = activities[activity_type]
        else:
            activity_type = 0

        status_types = {
            'online': discord.Status.online,
            'dnd': discord.Status.dnd,
            'idle': discord.Status.idle,
            'offline': discord.Status.offline
        }
        if status_type in status_types:
            status_types = status_types[status_type]
        else:
            status_type = status_types[status_type]

        await self.bot.change_presence(
            status=status_type,
            activity=discord.Activity(type=activity_type, name=message)
        )
        embed = discord.Embed(color=ctx.me.color, description='Endret Presence!')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.is_owner()
    @commands.command()
    async def leave(self, ctx, *guild_id: int):
        """
        Leaves a specified guild
        """

        if guild_id == ():
            guild_id = ctx.guild.id
        else:
            guild_id = guild_id

        try:
            guild = await self.bot.fetch_guild(guild_id)
        except discord.errors.Forbidden:
            embed = await embed_templates.error_fatal(ctx, text='Bot is not a member of this guild')
            return await ctx.send(embed=embed)

        confirmation_msg = await ctx.send(f'Do you want to leave {guild.name} (`{guild.id}`)?')
        await confirmation_msg.add_reaction('✅')

        def comfirm(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=comfirm)
        except asyncio.TimeoutError:
            await ctx.message.delete()
            await confirmation_msg.delete()
        else:
            await guild.leave()
            try:
                embed = discord.Embed(color=ctx.me.color, description='Guild left!')
                await ctx.send(embed=embed)
            except discord.errors.Forbidden:
                pass

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def resetcooldown(self, ctx, command: str):
        """
        Resets the cooldown period for a specified command
        """

        try:
            self.bot.get_command(command).reset_cooldown(ctx)
        except AttributeError:
            embed = await embed_templates.error_fatal(ctx, text=f'{command} is not a command')
            return await ctx.send(embed=embed)

        embed = discord.Embed(color=ctx.me.color, description='Cooldown reset!')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.is_owner()
    @commands.command()
    async def allemoji(self, ctx):
        """
        Sends all emoji the bot has access to
        """

        embed = discord.Embed(colour=ctx.me.color)

        emoji_string = ''
        for guild in self.bot.guilds:
            emoji_string += f'\n**{guild.name}**\n'
            for emoji in guild.emojis:
                if len(emoji_string) > 2000:
                    embed.description = emoji_string
                    await ctx.send(embed=embed)
                    emoji_string = f'\n**{guild.name}**\n'
                emoji_string += f'{emoji} '

        embed.description = emoji_string
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DevTools(bot))
