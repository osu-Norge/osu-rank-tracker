import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import embed_templates
import cogs.utils.database as database
from cogs.utils.osu_api import Gamemode, GamemodeOptions, OsuApi


class User(commands.Cog):
    """User commands cog"""

    def __init__(self, bot):
        self.bot = bot

    user_group = app_commands.Group(
        name='user',
        description='User management commands'
    )

    @user_group.command()
    async def register(self, interaction: discord.Interaction, gamemode: GamemodeOptions = GamemodeOptions.standard):
        """
        Connect your osu! account to the bot

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        # Check if user is already registered
        if await database.UserTable().get(interaction.user.id):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('You are already registered with the bot'),
                ephemeral=True
            )

        # Check if user is already pending verification
        verification_table = database.VerificationTable()
        if await verification_table.get(interaction.user.id):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('You are already pending verification'),
                ephemeral=True
            )

        # Generate auth link
        auth_link = await OsuApi.generate_auth_link(interaction.user.id, Gamemode.from_id(gamemode.value))
        await interaction.response.send_message(
            embed=embed_templates.success(f'Click the link to verify your osu! account:\n\n{auth_link}\n\nYou\'ve got 2 minutes to complete this verifcation'),
            ephemeral=True
        )

        # Cleanup after 2 minutes regardless of verification status
        await asyncio.sleep(120)
        await database.VerificationTable().delete(interaction.user.id)

    @user_group.command()
    async def remove(self, interaction: discord.Interaction):
        """
        Remove your osu! account from the bot

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        user_table = database.UserTable()

        # Check if user is registered
        if not (user := await user_table.get(interaction.user.id)):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('You are not registered with the bot'),
                ephemeral=True
            )

        await user_table.delete(user.discord_id)
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

        # Revert to author if no user provided
        if not user:
            user = interaction.user

        # Check if user is registered
        if not (db_user := await database.UserTable().get(user.id)):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('This user is not registered with the bot')
            )

        gamemode = Gamemode.from_id(db_user.gamemode)
        osu_user = await OsuApi.get_user(db_user.osu_id, gamemode)

        # TODO add data validation
        # TODO add spacing between numbers
        # TODO show data when None

        # unpack some of the data to shorten embed code
        country_emoji = f':flag_{osu_user["country_code"].lower()}:'
        global_rank = osu_user['statistics']['global_rank']
        country_rank = osu_user['statistics']['rank']['country']
        joined_timestamp = discord.utils.format_dt(datetime.fromisoformat(osu_user['join_date']), style="f")
        ss_ranks = osu_user['statistics']['grade_counts']['ss']
        ssh_ranks = osu_user['statistics']['grade_counts']['ssh']
        s_ranks = osu_user['statistics']['grade_counts']['s']
        sh_ranks = osu_user['statistics']['grade_counts']['sh']
        a_ranks = osu_user['statistics']['grade_counts']['a']

        # Construct embed
        embed = discord.Embed(
            title=f'{country_emoji} {osu_user["username"]}',
            color=osu_user['profile_colour'],
            url=f'https://osu.ppy.sh/users/{osu_user["id"]}'
        )
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar)
        embed.set_thumbnail(url=osu_user['avatar_url'])
        embed.description = f'**ID**: {osu_user["id"]}\n**Registered with gamemode**: {gamemode.name}\n' + \
                            f'{self.bot.emoji["osu_ss"]}{ss_ranks} ' + \
                            f'{self.bot.emoji["osu_ss_silver"]}{ssh_ranks} ' + \
                            f'{self.bot.emoji["osu_s"]}{s_ranks} ' + \
                            f'{self.bot.emoji["osu_s_silver"]}{sh_ranks} ' + \
                            f'{self.bot.emoji["osu_a"]}{a_ranks}'
        embed.add_field(name='Rank', value=f':earth_asia: {global_rank}\n{country_emoji} {country_rank}')
        embed.add_field(name='PP', value=int(osu_user['statistics']['pp']))
        embed.add_field(name='Accuracy', value=f'{round(osu_user["statistics"]["hit_accuracy"], 2)}%')
        embed.add_field(name='Level', value=osu_user['statistics']['level']['current'])
        embed.add_field(name='Playcount', value=osu_user['statistics']['play_count'])
        embed.add_field(name='Playtime (Hours)', value=f'{int(osu_user["statistics"]["play_time"] / 60 / 60)}')
        embed.add_field(name='Total Hits', value=osu_user['statistics']['total_hits'])
        embed.add_field(name='Total Score', value=osu_user['statistics']['total_score'])
        embed.add_field(name='Ranked Score', value=osu_user['statistics']['ranked_score'])
        embed.add_field(name='Joined', value=joined_timestamp)
        await interaction.response.send_message(embed=embed)

    @user_group.command(name='gamemode')
    async def set_gamemode(self, interaction: discord.Interaction, gamemode: GamemodeOptions):
        """
        Set your osu! gamemode

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        gamemode (GamemodeOptions): Gamemode to set
        """

        user_table = database.UserTable()

        # Check if user is registered
        if not (user := await user_table.get(interaction.user.id)):
            return await interaction.response.send_message(
                embed=embed_templates.error_warning('You are not registered with the bot')
            )

        gamemode = Gamemode.from_id(gamemode.value)
        user.gamemode = gamemode.id
        await user_table.save(user)

        await interaction.response.send_message(
            embed=embed_templates.success(f'Gamemode set to `{gamemode.name}`\n\n' + \
                                          'Role updates will take effect on next update cycle\n' + \
                                          'If you want to update your rank now, use `/user update`')
        )

    @app_commands.checks.cooldown(1, 60*60*12)  # 12 hours
    @user_group.command(name='update')
    async def force_user_rank_update(self, interaction: discord.Interaction):
        """
        Force's a rank update for your user

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild = database.GuildTable().get(interaction.guild.id)
        if (user := await database.UserTable().get(interaction.user.id)):
            osu_user = await OsuApi.get_user(user.osu_id, Gamemode.from_id(user.gamemode))
            if osu_user:
                await OsuApi.update_user_rank(guild, interaction.user, osu_user, Gamemode.from_id(user.gamemode),
                                              reason='User forced rank update through command')


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(User(bot))
