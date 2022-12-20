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

    @user_group.command()
    async def view(self, interaction: discord.Interaction, user: discord.Member = None):
        """
        View your osu! account

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        user (discord.Member): User to view. If not provided, defaults to the author of the command
        """

        if not user:
            user = interaction.user

        user_table = database.UserTable()
        user = await user_table.get_user(user.id)

        if not user:
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('This user is not registered with the bot')
            )

        osu_user = await OsuApi.get_user(user.osu_id)

        # TODO add data validation

        joined_timestamp = discord.utils.format_dt(datetime.fromisoformat(osu_user['join_date']), style="D")

        embed = discord.Embed(
            title=f':flag_{osu_user["country_code"]}: {osu_user["username"]}',
            description=f'ID: {osu_user.id}\nGamemode: {osu_user.gamemode}',
            color=osu_user['profile_colour']
        )
        embed.add_field(name='Rank', value=f'#{osu_user["statistics"]["global_rank"]}\n:flag_{osu_user["country_code"]}: #{osu_user["rank"]["country"]}')
        embed.add_field(name='PP', value=f'{osu_user["statistics"]["pp"]}')
        embed.add_field(name='Accuracy', value=f'{osu_user["statistics"]["hit_accuracy"]}%')
        embed.add_field(name='Level', value=f'{osu_user["statistics"]["level"]["current"]}')
        embed.add_field(name='Playcount', value=f'{osu_user["statistics"]["play_count"]}')
        embed.add_field(name='Playtime (Hours)', value=f'{osu_user["statistics"]["play_time"] / 60}')
        embed.add_field(name='Total Score', value=f'{osu_user["statistics"]["total_score"]}')
        embed.add_field(name='Total Hits', value=f'{osu_user["statistics"]["total_hits"]}')
        embed.add_field(name='Ranked Score', value=f'{osu_user["ranked_score"]}')
        embed.add_field(name='Joined', value=joined_timestamp)
        embed.set_thumbnail(url=osu_user.avatar_url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(User(bot))
