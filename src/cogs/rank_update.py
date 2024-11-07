import asyncio
import dataclasses
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

    @tasks.loop(hours=12)
    async def update_ranks(self):
        """
        Update the ranks of all users in the database
        """

        self.bot.logger.info('Initiating automatic rank update...')

        user_table = database.UserTable()
        guild_table = database.GuildTable()

        sleep_time = 1 / 10  # Max 10 requests per second. Discord allows 50 and osu allows 20. We're playing it safe

        for guild in await guild_table.get_all():
            self.bot.logger.info(f'Updating ranks for guild - {guild.discord_id}...')

            if not (discord_guild := self.bot.get_guild(guild.discord_id)):
                continue

            for member in discord_guild.members:
                if member.bot or not (user := await user_table.get(member.id)):
                    continue

                self.bot.logger.info(f'Checking/Updating rank of user - {user.discord_id}...')

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

        self.bot.logger.info("Rank update complete!")

    @update_ranks.before_loop
    async def before_update_ranks(self):
        """
        Schedule the update ranks task to every 12 hours at 00:00/12:00 UTC
        Chooses the closest next time to run based on the current time
        """

        await self.bot.wait_until_ready()

        now = datetime.utcnow()

        if now.hour < 12:
            sleep_until = now.replace(hour=12, minute=0, second=0, microsecond=0)
        else:
            sleep_until = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        self.bot.logger.info(f'Scheduling automatic rank update for {sleep_until} UTC')

        await discord.utils.sleep_until(sleep_until)

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self: commands.Bot, guild: discord.Guild):
        """
        Create a new guild in the database when the bot joins a guild

        Parameters
        ----------
        guild (discord.Guild): Guild instance
        """

        self.bot.logger.info(f'Bot added to guild - {guild.id}')
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

        self.bot.logger.info(f'Bot removed from guild - {guild.id}')
        await database.GuildTable().delete(guild.id)

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: discord.Member):
        """
        Immidiately update a user's rank when they join a guild

        Parameters
        ----------
        member (discord.Member): Member instance
        """

        self.bot.logger.info(f'User ({member.id}) joined guild ({member.guild.id})')

        guild = await database.GuildTable().get(member.guild.id)
        user = await database.UserTable().get(member.id)
        if user:
            osu_user = await OsuApi.get_user(user.osu_id, Gamemode.from_id(user.gamemode))
            update = await OsuApi.update_user_rank(guild, member, osu_user, Gamemode.from_id(user.gamemode),
                                                   reason='User joined guild')

            if update.get('success'):
                self.bot.logger.info(f'Updated rank of user ({member.id})')
            else:
                self.bot.logger.info(f'Rank not updated for user ({member.id}) - {update["reason"]}')

    @commands.Cog.listener('on_guild_role_delete')
    async def on_guild_role_delete(self, role: discord.Role):
        """
        Clear database mapping if role is deleted

        Parameters
        ----------
        role (discord.Role): Role instance
        """

        guild = await database.GuildTable().get(role.guild.id)
        if not guild:
            return

        attributes = dataclasses.asdict(guild)
        for key, value in attributes.items():
            if value == role.id:
                setattr(guild, key, None)

        await database.GuildTable().save(guild)

        self.bot.logger.info(f'Registered role {role.id} deleted! Removed the mapping!')


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RankUpdate(bot))
