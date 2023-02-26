import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

import cogs.utils.database as database
from cogs.utils.osu_api import Gamemode, OsuApi


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

        sleep_time = 1 / 10  # Max 10 requests per second. Discord allows 50 and osu allows 20. We're playing it safe

        for guild in await guild_table.get_all():
            if not (discord_guild := self.bot.get_guild(guild.discord_id)):
                continue

            for member in discord_guild.members:
                if member.bot or not (user := await user_table.get(member.id)):
                    continue

                gamemode = Gamemode.from_id(user.gamemode)

                # If rank is not cached, fetch it and cache it
                if not (rank := self.rank_cache.get(user.discord_id)):
                    # Get osu user and verify it exists
                    if not (osu_user := await OsuApi.get_user(user.osu_id, gamemode)):
                        continue
                    # Get the user's rank and verify it exists
                    if not (rank := osu_user.get('statistics', {}).get('global_rank')):
                        continue
                    self.rank_cache[user.discord_id] = rank

                # Update the user's rank
                await OsuApi.update_user_rank(guild, member, osu_user, gamemode,
                                              reason='Automatic rank update based on osu! rank')

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
            sleep_until = now + timedelta(days=1)
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

    @commands.Cog.listener('on_guild_remove')
    async def on_guild_remove(self: commands.Bot, guild: discord.Guild):
        """
        Delete a guild from the database when the bot leaves a guild

        Parameters
        ----------
        guild (discord.Guild): Guild instance
        """

        await database.GuildTable().delete(guild.id)

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
        if user and not self.__is_blacklisted(member, guild):
            osu_user = await OsuApi.get_user(user.osu_id, Gamemode.from_id(user.gamemode))
            if osu_user and osu_user.get('statistics', {}).get('global_rank'):
                await OsuApi.update_user_rank(guild, member, osu_user, Gamemode.from_id(user.gamemode),
                                              reason='User joined guild')


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RankUpdate(bot))
