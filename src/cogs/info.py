from discord.ext import commands
import discord

from time import time, perf_counter
import platform
from os import getpid, environ
from psutil import Process

from cogs.utils import embed_templates


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['info', 'about'])
    async def botinfo(self, ctx):
        """
        Displays key information about the bot
        """

        dev = await self.bot.fetch_user(170506717140877312)

        # Ping
        start = perf_counter()
        status_msg = await ctx.send('Pinging...')
        end = perf_counter()
        ping = int((end - start) * 1000)

        # Memory usage
        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)

        # Member stats
        """
        This is a pretty stupid way of doing things but it's the best I can come up with.
        Using curly brackets for both dicts and sets is retarded becuase
        I have to do this shit in order to create a fucking empty set.

        Apparently you can't access user presences, only member presences
        Because of that I have to use sets instead of ints in order to not count duplicate users.
        Fucking hell discord...
        """
        total_members = set([])
        online_members = set([])
        idle_members = set([])
        dnd_members = set([])
        offline_members = set([])
        for guild in self.bot.guilds:
            for member in guild.members:
                total_members.add(member.id)
                if str(member.status) == 'online':
                    online_members.add(member.id)
                elif str(member.status) == 'idle':
                    idle_members.add(member.id)
                elif str(member.status) == 'dnd':
                    dnd_members.add(member.id)
                elif str(member.status) == 'offline':
                    offline_members.add(member.id)

        # Build embed
        embed = discord.Embed(color=ctx.me.color, url=self.bot.misc['website'])
        embed.set_author(name=dev.name, icon_url=dev.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='Dev', value=f'{dev.mention}\n{dev.name}#{dev.discriminator}')
        embed.add_field(name='Uptime', value=await self.get_uptime())
        embed.add_field(name='Ping', value=f'Ekte ping: {ping} ms\nWebsocket ping: {int(self.bot.latency * 1000)} ms')
        embed.add_field(name='Guilds', value=len(self.bot.guilds))
        embed.add_field(name='Discord.py', value=discord.__version__)
        embed.add_field(name='Python', value=platform.python_version())
        embed.add_field(name='Usage', value=f'RAM: {memory_usage} MB')
        embed.add_field(name='Kernel', value=f'{platform.system()} {platform.release()}')
        if 'docker' in environ:
            embed.add_field(name='Docker', value='U+FE0F')
        embed.add_field(name=f'Users ({len(total_members)})',
                        value=f'{self.bot.emoji["online"]}{len(online_members)} ' +
                              f'{self.bot.emoji["idle"]}{len(idle_members)} ' +
                              f'{self.bot.emoji["dnd"]}{len(dnd_members)} ' +
                              f'{self.bot.emoji["offline"]}{len(offline_members)}')
        embed.add_field(name='Links', value=f'[Website]({self.bot.misc["website"]}) | ' +
                                            f'[Source code]({self.bot.misc["source_code"]})')
        await embed_templates.default_footer(ctx, embed)
        await status_msg.edit(embed=embed, content=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def uptime(self, ctx):
        """
        Fetches the amount of time the bot has been running for
        """

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='🔌 Uptime', value=await self.get_uptime())
        await embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command()
    async def ping(self, ctx):
        """
        Checks the latency between the bot and Discord
        """

        start = perf_counter()
        status_msg = await ctx.send('Pinging...')
        end = perf_counter()
        ping = int((end - start) * 1000)

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(
            name='📶 Ping',
            value=f'**Ekte ping:** {ping} ms\n**Websocket ping:** {int(self.bot.latency * 1000)} ms'
        )
        await embed_templates.default_footer(ctx, embed)
        await status_msg.edit(embed=embed, content=None)

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliases=['databaseinfo', 'db', 'database'])
    async def dbinfo(self, ctx):
        """Sjekk antall registrerte brukere og status til databasen"""
        pass

    async def get_uptime(self):
        """
        Returns the current uptime of the bot in string format
        """
        now = time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        return f'{days}d, {hours}h, {minutes}m, {seconds}s'


def setup(bot):
    bot.add_cog(Info(bot))
