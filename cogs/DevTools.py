from discord.ext import commands
import discord

import asyncio
from sys import exit
from os import listdir, system
import socket
from requests import get
from math import ceil

from cogs.utils import Defaults


class DevTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def stopbot(self, ctx):
        """Stopper båtten gjennom Discord-klienten"""

        embed = discord.Embed(color=ctx.me.color, description='Stopper bot...')
        await ctx.send(embed=embed)
        await self.bot.logout()
        exit('Bot stoppet')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def custommsg(self, ctx, channel: int, *args):
        """Sender melding til spesifisert kanal"""

        channel = self.bot.get_channel(channel)
        custommessage = ' '.join(args)
        await channel.send(custommessage)

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Sendte', value=custommessage)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['listservers'])
    async def listguilds(self, ctx, *side: int):
        """Sender en liste over guilds som båtten er medlem av"""

        guild_list = []
        for guild in self.bot.guilds:
            guild_list.append(f'{guild.name} - {guild.id}')

        pagecount = ceil(len(guild_list) / 10)

        if side is ():
            side = 1
        else:
            side = side[0]

        if side <= 0 or side > pagecount:
            side = 1

        start_index = (side - 1) * 10
        end_index = side * 10

        guilds = '\n'.join(guild_list[start_index:end_index])

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Guilds', value=guilds)
        embed.set_footer(text=f'Side: {side}/{pagecount}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def listusers(self, ctx, *side: int):
        """Sender en liste over alle medlemmene båtten har tilgang til"""

        user_list = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue
                member_string = f'{member.name}#{member.discriminator} ' +\
                    f'- {member.id}'
                if member_string in user_list:
                    continue
                else:
                    user_list.append(member_string)

        pagecount = ceil(len(user_list) / 10)

        if side is ():
            side = 1
        else:
            side = side[0]

        if side <= 0 or side > pagecount:
            side = 1

        start_index = (side - 1) * 10
        end_index = side * 10

        users = '\n'.join(user_list[start_index:end_index])

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Brukere', value=users)
        embed.set_footer(text=f'Side: {side}/{pagecount}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx, cog):
        """Slår av spesifisert cog"""

        try:
            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    if name == cog:
                        try:
                            self.bot.unload_extension(f'cogs.{name}')
                        except:
                            return await Defaults.error_fatal_send(ctx, text='Error!')

                        embed = discord.Embed(color=ctx.me.color, description=f'{cog} har blitt skrudd av')
                        return await ctx.send(embed=embed)

            await Defaults.error_fatal_send(ctx, text=f'{cog} er ikke en cog')
        except:
            return await Defaults.error_fatal_send(ctx, text='Error!')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['disablecommand'])
    async def unloadcommand(self, ctx, command: str):
        """Slår av spesifisert command"""

        command = self.bot.get_command(command)
        command.enabled = False
        await ctx.send(f'{command} har blitt skrudd på')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command(aliases=['enablecommand'])
    async def loadcommand(self, ctx, command: str):
        """Slår på spesifisert command"""

        command = self.bot.get_command(command)
        command.enabled = True
        await ctx.send(f'{command} har blitt skrudd på')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def load(self, ctx, cog):
        """Slår på spesifisert cog"""

        try:
            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    if name == cog:
                        try:
                            self.bot.load_extension(f'cogs.{name}')
                        except:
                            return await Defaults.error_fatal_send(ctx, text='Error!')

                        embed = discord.Embed(color=ctx.me.color, description=f'{cog} har blitt lastet inn!')
                        return await ctx.send(embed=embed)

            await Defaults.error_fatal_send(ctx, text=f'{cog} er ikke en cog')
        except:
            return await Defaults.error_fatal_send(ctx, text='Error!')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, cog):
        """Laster inn spesifisert cog på nytt"""

        try:
            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    if name == cog:
                        try:
                            self.bot.reload_extension(f'cogs.{name}')
                        except:
                            return await Defaults.error_fatal_send(ctx, text='Error!')

                        embed = discord.Embed(color=ctx.me.color, description=f'{cog} har blitt lastet inn på nytt!')
                        await ctx.send(embed=embed)
        except:
            await Defaults.error_fatal_send(ctx, text=f'{cog} er ikke en cog')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def reloadunloaded(self, ctx):
        """laster inn alle cogs på nytt"""

        try:
            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    try:
                        self.bot.unload_extension(f'cogs.{name}')
                    except:
                        pass

            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    try:
                        self.bot.load_extension(f'cogs.{name}')
                    except:
                        await Defaults.error_fatal_send(ctx, text=f'{name} feilet')

            embed = discord.Embed(color=ctx.me.color, description='Lastet inn alle cogs!')
            await ctx.send(embed=embed)
        except:
            await Defaults.error_fatal_send(ctx, text='Error!')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def reloadall(self, ctx):
        """laster inn alle cogs på nytt"""

        try:
            for file in listdir('cogs'):
                if file.endswith('.py'):
                    name = file[:-3]
                    try:
                        self.bot.reload_extension(f'cogs.{name}')
                    except:
                        pass

            embed = discord.Embed(color=ctx.me.color, description='Lastet inn alle cogs på nytt!')
            await ctx.send(embed=embed)
        except:
            await Defaults.error_fatal_send(ctx, text='Error!')

    @commands.is_owner()
    @commands.command()
    async def cmd(self, ctx, *, command: str):
        """Execute terminal commands"""

        system(command)
        await ctx.send('Fullført!')

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def localip(self, ctx):
        """Sender den lokale ip-en til maskinen"""

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Lokal ip', value=s.getsockname()[0])
        await ctx.send(embed=embed)
        s.close()

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def publicip(self, ctx):
        """inb4 lekker ip-en min"""

        data = get('https://wtfismyip.com/json').json()
        ip = data['YourFuckingIPAddress']
        location = data['YourFuckingLocation']
        isp = data['YourFuckingISP']

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Public ip', value=f'{ip}\n{location}\n{isp}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.command()
    async def changepresence(self, ctx, activity_type, message, *status_type):
        """Endrer status"""

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

        if not status_type:
            status_type = status_types['online']
        try:
            await self.bot.change_presence(status=status_type,
                                           activity=discord.Activity(type=activity_type, name=message))
            embed = discord.Embed(color=ctx.me.color, description='Endret Presence!')
            await ctx.send(embed=embed)
        except:
            await Defaults.error_warning_send(ctx, text='Error!')

    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    @commands.is_owner()
    @commands.command()
    async def leave(self, ctx, *guild_id: int):
        """Forlater spesifisert guild"""

        if guild_id is ():
            guild_id = ctx.message.guild.id
        else:
            guild_id = guild_id[0]

        try:
            guild = await self.bot.fetch_guild(guild_id)
        except:
            return await Defaults.error_fatal_send(ctx, text='Båtten er ikke i denne guilden')

        confirmation_msg = await ctx.send(f'Vil du virkelig forlate {guild.name} (`{guild.id}`)?')
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
                embed = discord.Embed(color=ctx.me.color, description='Forlatt guild!')
                await ctx.send(embed=embed)
            except:
                pass

    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    @commands.command()
    async def resetcooldown(self, ctx, command: str):
        """Resetter nedkjøling for spesifisert kommando"""

        try:
            self.bot.get_command(command).reset_cooldown(ctx)
        except AttributeError:
            return await Defaults.error_fatal_send(ctx, text=f'{command} er ikke en command', mention=False)

        embed = discord.Embed(color=ctx.me.color, description='Fjernet cooldown!')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.is_owner()
    @commands.command()
    async def allemoji(self, ctx):
        """Se alle emoji båtten har tilgang til"""

        embed = discord.Embed(colour=ctx.me.color)
        await Defaults.set_footer(ctx, embed)

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

    @commands.bot_has_permissions()
    @commands.is_owner()
    @commands.command()
    async def deletemsg(self, channel_id: int, message_id: int):
        """Slett melding"""

        channel = self.bot.get_channel(channel_id)
        msg = await channel.fetch_message(message_id)
        await msg.delete()


def setup(bot):
    bot.add_cog(DevTools(bot))
