from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.database as database
from cogs.utils.osu_api import OsuApi


class User(commands.Cog):
    """User commands cog"""

    def __init__(self, bot):
        self.bot = bot
        self.update_ranks.start()

    @tasks.loop(hours=24)
    async def update_ranks(self):
        """
        Update the ranks of all users in the database
        """

        pass

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

        pass

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: discord.Member):
        """
        Immidiately update a user's rank when they join a guild

        Parameters
        ----------
        guild (discord.Guild): Guild instance
        """

        pass

    @app_commands.checks.cooldown(1, 60*60*12)  # 12 hours
    @app_commands.command(name='force_update')
    async def force_user_rank_update(self, interaction: discord.Interaction):
        """
        Force's a rank update for your user

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        pass


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(User(bot))
