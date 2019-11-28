from discord.ext import commands
import discord

from time import time, perf_counter
import platform
from os import getpid, environ
from psutil import Process
from git import Repo as repo

from cogs.utils import Defaults


class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['info', 'about', 'om', 'båttinfo'])
    async def botinfo(self, ctx):
        """Viser info om meg"""

        dev = await self.bot.fetch_user(170506717140877312)

        start = perf_counter()
        status_msg = await ctx.send('Beregner ping...')
        end = perf_counter()
        ping = int((end - start) * 1000)

        now = time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)
        cpu_percent = process.cpu_percent()

        total_members = []
        online_members = []
        idle_members = []
        dnd_members = []
        offline_members = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id in total_members:
                    continue
                total_members.append(member.id)
                if str(member.status) == 'online':
                    online_members.append(member.id)
                elif str(member.status) == 'idle':
                    idle_members.append(member.id)
                elif str(member.status) == 'dnd':
                    dnd_members.append(member.id)
                elif str(member.status) == 'offline':
                    offline_members.append(member.id)

        embed = discord.Embed(color=ctx.me.color, url=self.bot.misc['website'])
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='Dev', value=f'{dev.mention}\n{dev.name}#{dev.discriminator}')
        embed.add_field(name='Oppetid', value=f'{days}d {hours}t {minutes}m {seconds}s')
        embed.add_field(name='Ping', value=f'Ekte ping: {ping} ms\nWebsocket ping: {int(self.bot.latency * 1000)} ms')
        embed.add_field(name='Servere', value=len(self.bot.guilds))
        embed.add_field(name='Discord.py Versjon', value=discord.__version__)
        embed.add_field(name='Python Versjon', value=platform.python_version())
        embed.add_field(name='Ressursbruk', value=f'RAM: {memory_usage} MB\nCPU: {cpu_percent}%')
        embed.add_field(name='Maskin', value=f'{platform.system()} {platform.release()}')
        if "docker" in environ:
            embed.add_field(name='Docker', value=f'U+FE0F')
        embed.add_field(name=f'Brukere ({len(total_members)})',
                        value=f'{self.bot.emoji["online"]}{len(online_members)} ' +
                              f'{self.bot.emoji["idle"]}{len(idle_members)} ' +
                              f'{self.bot.emoji["dnd"]}{len(dnd_members)} ' +
                              f'{self.bot.emoji["offline"]}{len(offline_members)}')
        embed.add_field(name='Lenker', value=f'[Nettside]({self.bot.misc["website"]}) ' +
                                             f'| [Kildekode]({self.bot.misc["source_code"]})')
        await Defaults.set_footer(ctx, embed)
        await status_msg.edit(embed=embed, content=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['uptime'])
    async def oppetid(self, ctx):
        """Sjekk hvor lenge båtten har kjørt"""

        now = time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='🔌 Oppetid', value=f'{days}d, {hours}t, {minutes}m, {seconds}s')
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ping(self, ctx):
        """Sjekk pingen til båtten"""

        start = perf_counter()
        status_msg = await ctx.send('Beregner ping...')
        end = perf_counter()
        ping = int((end - start) * 1000)

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='📶 Ping', value=f'**Ekte ping:** {ping} ms\n**Websocket ping:** {int(self.bot.latency * 1000)} ms')
        await Defaults.set_footer(ctx, embed)
        await status_msg.edit(embed=embed, content=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['githubrepo', 'repo', 'git'])
    async def github(self, ctx):
        """Sender link til Github-repoet mitt"""

        embed = discord.Embed(color=ctx.me.color)
        embed.set_thumbnail(url='https://cdn2.iconfinder.com/data/icons/black-' +
                                'white-social-media/64/social_media_logo_github-512.png')
        embed.add_field(name='🔗 Github Repo',
                        value=f'[Klikk her]({self.bot.misc["source_code"]}) for å se den dritt skrevne kildekoden min')
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['gitcommit', 'githash', 'gitstatus', 'gitversion'])
    async def version(self, ctx):
        """Viser versjonen som båtten kjører på"""

        githash = repo('.').head.commit
        embed = discord.Embed(color=ctx.me.color, title='Git Commit Hash',
                              description=f'[{githash}]({self.bot.misc["source_code"]}/commit/{githash})')
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotInfo(bot))
