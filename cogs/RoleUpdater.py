from discord.ext import commands, tasks

from requests import get
import urllib.parse
from datetime import time, datetime
from asyncio import sleep

from cogs.utils import OsuUtils


class RoleUpdater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_roles.start()

    def cog_unload(self):
        self.update_roles.cancel()

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @commands.group()
    async def loop(self, ctx):
        """Manipulér loop"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @loop.command()
    async def start(self, ctx):
        """Starter loop"""

        self.update_roles.start()
        await ctx.send(':thumbsup:')

    @loop.command(aliases=['restart'])
    async def omstart(self, ctx):
        """Starter loop på nytt"""

        self.update_roles.restart()
        await ctx.send(':thumbsup:')

    @loop.command(aliases=['stop'])
    async def stopp(self, ctx):
        """Stopper loop (foregående loop)"""

        self.update_roles.stop()
        await ctx.send(':thumbsup:')

    @loop.command(aliases=['cancel'])
    async def avbryt(self, ctx):
        """Stopper loop (og fremtidige)"""

        self.update_roles.cancel()
        await ctx.send(':thumbsup:')

    @tasks.loop(time=[time(hour=0, minute=0), time(hour=12, minute=0)], reconnect=True)
    async def update_roles(self):
        """Checks all db users' ranks and updates their roles accordingly"""

        print(f'Checking all users\' ranks | {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')

        guild = self.bot.get_guild(self.bot.guild)

        try:
            db_users = self.bot.database.find()
        except:
            return 'DATABASE CONNECTION FAILED!'

        for user in db_users:
            discord_user_id = user['_id']
            osu_user = user['osu_user_id']
            gamemode = user['gamemode']

            discord_user = guild.get_member(discord_user_id)
            if discord_user is None:
                continue

            try:
                url = 'https://osu.ppy.sh/api/get_user?' + urllib.parse.urlencode({
                    'u': osu_user, 'm': gamemode, 'k': self.bot.osu_api_key
                })
                data = get(url).json()
                rank = data[0]["pp_rank"]
            except:
                print(f'{discord_user.id} - COULD NOT FETCH DATA osu! USER DATA - ({osu_user})')
                continue

            try:
                rank = int(rank)
            except:
                rank = 0

            rank_roles = await OsuUtils.get_rank_roles(self, guild)
            rank_role = await OsuUtils.rank_role(rank, rank_roles)
            await OsuUtils.remove_old_roles(discord_user, rank_roles, rank_role)
            if rank_role != 'no rank role':
                await discord_user.add_roles(rank_role)

            print(f'Checking rank - {discord_user.id}')

            await sleep(2)

        print(f'All users have been checked! | {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')

    @update_roles.before_loop
    async def before_upate_roles(self):
        """Delays loop initialization until the bot is ready for use"""

        await self.bot.wait_until_ready()

    @update_roles.after_loop
    async def on_update_roles_cancel(self):
        """Prints cancel message when loop is cancelled"""

        if self.update_roles.is_being_cancelled():
            print('Stopping loop...')


def setup(bot):
    bot.add_cog(RoleUpdater(bot))
