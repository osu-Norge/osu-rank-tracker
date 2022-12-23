import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.database as database
from cogs.utils.osu_api import OsuApi


class RankUpdate(commands.Cog):
    """Cog for handling rank updates"""

    def __init__(self, bot):
        self.bot = bot
        self.update_ranks.start()
        self.rank_cache = {}

    def cog_unload(self):
        self.update_ranks.cancel()

    @tasks.loop(hours=24)
    async def update_ranks(self):
        """
        Update the ranks of all users in the database
        """

        user_table = database.UserTable()
        guild_table = database.GuildTable()

        guilds = guild_table.get_all()

        user_count = user_table.count()
        sleep_time = user_count / 60  # TODO: calculate optimal sleep time based on user count and ratelimit

        for guild in guilds:
            for member in guild.members:
                if member.bot:
                    continue

                if not (user := user_table.get(member.id)):
                    continue

                if not (rank := self.rank_cache.get(user.id)):
                    osu_user = OsuApi.get_user(user.osu_id)
                    if not osu_user:
                        continue
                    rank = osu_user["statistics"]["global_rank"]
                    self.rank_cache[user.id] = rank

                # Update the user's rank
                await self.__update_user_rank(guild, member, rank, user.gamemode, reason='Automatic rank update based on osu! rank')

                await asyncio.sleep(sleep_time)

        self.rank_cache = {}  # Clear the rank cache

    @update_ranks.before_loop
    async def before_update_ranks(self):
        """
        Schedule the update ranks task to run at 00:00 UTC
        """

        await self.bot.wait_until_ready()

        now = datetime.utcnow()

        if now.hour > 0:
            sleep_until = now + datetime.timedelta(days=1)
            sleep_until = sleep_until.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            sleep_until = now.replace(hour=0, minute=0, second=0, microsecond=0)

        await discord.utils.sleep_until(sleep_until)

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self: commands.Bot, guild: discord.Guild):
        """
        Create a new guild in the database when the bot joins a guild

        Parameters
        ----------
        guild (discord.Guild): Guild instance
        """

        guild = database.Guild(discord_id=guild.id)
        await database.GuildTable().save(guild)

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: discord.Member):
        """
        Immidiately update a user's rank when they join a guild

        Parameters
        ----------
        member (discord.Member): Member instance
        """

        guild = await database.GuildTable().get(member.guild.id)
        user = await database.UserTable().get(member.id)
        if user:
            await self.__update_user_rank(guild, member, user.gamemode, reason='User joined guild')

    @app_commands.checks.cooldown(1, 60*60*12)  # 12 hours
    @app_commands.command(name='force_update')
    async def force_user_rank_update(self, interaction: discord.Interaction):
        """
        Force's a rank update for your user

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild = database.GuildTable().get(interaction.guild.id)
        user = database.UserTable().get(interaction.author.id)
        if user:
            self.__update_user_rank(guild, interaction.author, user.gamemmode, reason='User forced rank update through command')


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RankUpdate(bot))
