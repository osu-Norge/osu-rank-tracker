from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import embed_templates
import cogs.utils.database as database
from cogs.utils.osu_api import OsuApi


class User(commands.Cog):
    """User commands cog"""

    def __init__(self, bot):
        self.bot = bot

    user_group = app_commands.Group(
        name='user',
        description='User management commands'
    )

    @user_group.command()
    async def register(self, interaction: discord.Interaction):
        """
        Connect your osu! account to the bot

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        pass

    @user_group.command()
    async def remove(self, interaction: discord.Interaction):
        """
        Remove your osu! account from the bot

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        user_table = database.UserTable()
        user = await user_table.get_user(interaction.user.id)

        if not user:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('You are not registered with the bot'),
                ephemeral=True
            )
        
        user_table.delete(user.id)
        await interaction.response.send_message(
            embed=embed_templates.success('Your osu! account has been removed from the bot'),
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(User(bot))
