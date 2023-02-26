from enum import Enum

import discord
from discord import app_commands
from discord.ext import commands
from iso3166 import countries

from cogs.utils import embed_templates
import cogs.utils.database as database
from cogs.utils.osu_api import Gamemode, OsuApi


class Settings(commands.Cog):
    """Manage guild settings"""

    def __init__(self, bot):
        self.bot = bot

    settings_group = app_commands.Group(
        name='settings',
        description='Manage bot settings',
        guild_only=True,
        default_permissions=discord.Permissions(manage_guild=True)
    )

    whitelist_group = app_commands.Group(name='whitelist', description='Manage country whitelist',
                                         parent=settings_group)
    blacklist_group = app_commands.Group(name='blacklist', description='Manage user blacklist',
                                         parent=settings_group)
    role_group = app_commands.Group(name='role', description='Manage role settings',
                                    parent=settings_group)

    async def __role_setter(
        self,
        interaction: discord.Interaction,
        role: discord.Role | None,
        role_variable: str,
        role_name: str
    ):
        """
        Validates a role and puts it into the database. Sends confirmation message to Discord

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        role (str): The user inputted role name, id or mention
        role_variable (str): The database column name
        role_name (str): The role name that will be displayed in the confirmation message on Discord
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if role:
            setattr(guild, role_variable, role.id)
        else:
            setattr(guild, role_variable, None)

        await guild_table.save(guild)

        if not role:
            embed = embed_templates.success(f'The {role_name} role has been reset!')
            return await interaction.response.send_message(embed=embed)

        embed = embed_templates.success(f'{role.mention} has been set as the {role_name} role!')
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command()
    async def setup(self, interaction: discord.Interaction):
        """
        Automatic setup wizard for the bot

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        await interaction.response.send_message('This feature is not yet implemented')

    @settings_group.command()
    async def show(self, interaction: discord.Interaction):
        """
        Show all bot settings for the guild

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        await interaction.response.send_message('This feature is not yet implemented')

    @settings_group.command()
    async def reset(self, interaction: discord.Interaction):
        """
        Reset all settings to default

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)
        for attribute in dir(guild):
            if not attribute.startswith('__') and not callable(getattr(guild, attribute)) and attribute != 'discord_id':
                setattr(guild, attribute, None)
        await guild_table.save(guild)

        embed = embed_templates.success('All settings have been reset!')
        await interaction.response.send_message(embed=embed)

    @whitelist_group.command(name='add')
    async def whitelist_add(self, interaction: discord.Interaction, country_code: str):
        """
        Add a country to the whitelist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        country_code (str): The iso3166 country code to add to the whitelist
        """

        try:
            country = countries.get(country_code)
        except KeyError:
            embed = embed_templates.error_warning(
                'Invalid country! Make you enter a valid country or country code\n\n' +
                'Click [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for more info'
            )
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.whitelisted_countries:
            guild.whitelisted_countries = []

        if country.alpha2 in guild.whitelisted_countries:
            embed = embed_templates.error_warning('Country is already in the whitelist')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries.append(country.alpha2)
        await guild_table.save(guild)

        embed = embed_templates.success(f'`{country.name}` has been added to the whitelist')
        await interaction.response.send_message(embed=embed)

    @whitelist_group.command(name='remove')
    async def whitelist_remove(self, interaction: discord.Interaction, country_code: str):
        """
        Remove a country from the whitelist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        country_code (str): The iso3166 country code to remove from the whitelist
        """

        try:
            country = countries.get(country_code)
        except KeyError:
            embed = embed_templates.error_warning(
                'Invalid country! Make you enter a valid country or country code\n\n' +
                'Click [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for more info'
            )
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.whitelisted_countries or country.alpha2 not in guild.whitelisted_countries:
            embed = embed_templates.error_warning('Country is not in the whitelist')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries.remove(country.alpha2)
        await guild_table.save(guild)

        embed = embed_templates.success(f'`{country.name}` has been removed from the whitelist')
        await interaction.response.send_message(embed=embed)

    @whitelist_group.command(name='show')
    async def whitelist_show(self, interaction: discord.Interaction):
        """
        Show the country whitelist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.whitelisted_countries:
            embed = embed_templates.error_warning('No countries are whitelisted!')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries = [f'`{country}`' for country in guild.whitelisted_countries]

        if len(guild.whitelisted_countries) > 2048:
            embed = embed_templates.error_warning('Whitelist is too long to be displayed!')
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(title='Whitelisted countries')
        embed.description = ', '.join(guild.whitelisted_countries)
        await interaction.response.send_message(embed=embed)

    @blacklist_group.command(name='add')
    async def blacklist_add(self, interaction: discord.Interaction, osu_user: str):
        """
        Add an osu user to the blacklist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        osu_user (str): The osu! user to add to the blacklist
        """

        user = await OsuApi.get_user(osu_user, Gamemode.from_name('standard'))
        user_id = user.get('id')
        username = user.get('username')

        if not user:
            embed = embed_templates.error_warning('Invalid osu! user')
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.blacklisted_osu_users:
            guild.blacklisted_osu_users = []

        if user.get('id') in guild.blacklisted_osu_users:
            embed = embed_templates.error_warning('User is already blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users.append(user_id)
        await guild_table.save(guild)

        embed = embed_templates.success(
            f'[{username}](https://osu.ppy.sh/users/{user_id}) ({user_id}) is now blacklisted!'
        )
        await interaction.response.send_message(embed=embed)

    @blacklist_group.command(name='remove')
    async def blacklist_remove(self, interaction: discord.Interaction, osu_user: str):
        """
        Remove an osu user from the blacklist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        osu_user (str): The osu! user to remove from the blacklist
        """

        user = await OsuApi.get_user(osu_user, Gamemode.from_name('standard'))
        user_id = user.get('id')
        username = user.get('username')

        if not user:
            embed = embed_templates.error_warning('Invalid osu! user')
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.blacklisted_osu_users or user_id not in guild.blacklisted_osu_users:
            embed = embed_templates.error_warning('User is not blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users.remove(user_id)
        await guild_table.save(guild)

        embed = embed_templates.success(
            f'[{username}](https://osu.ppy.sh/users/{user_id}) ({user_id}) is no longer blacklisted!'
        )
        await interaction.response.send_message(embed=embed)

    @blacklist_group.command(name='show')
    async def blacklist_show(self, interaction: discord.Interaction):
        """
        Show the osu user blacklist

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.blacklisted_osu_users:
            embed = embed_templates.error_warning('No users are blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users = [f'[{u}](https://osu.ppy.sh/users/{u})' for u in guild.blacklisted_osu_users]

        if len(guild.blacklisted_osu_users) > 2048:
            embed = embed_templates.error_warning('Blacklist is too long to be displayed!')
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(title='Blacklisted users (IDs)')
        embed.description = ', '.join(guild.blacklisted_osu_users)
        await interaction.response.send_message(embed=embed)

    class Roles(Enum):
        """
        List of roles that can be set in the database. Serves as autocomplete for the role command
        """

        on_registration_add = 'role_add', 'addrole'
        on_registration_remove = 'role_remove', 'removerole'
        digit_1 = 'role_1_digit', '1 digit'
        digit_2 = 'role_2_digit', '2 digit'
        digit_3 = 'role_3_digit', '3 digit'
        digit_4 = 'role_4_digit', '4 digit'
        digit_5 = 'role_5_digit', '5 digit'
        digit_6 = 'role_6_digit', '6 digit'
        digit_7 = 'role_7_digit', '7 digit'
        gamemode_standard = 'role_standard', 'osu!standard'
        gamemode_taiko = 'role_taiko', 'osu!taiko'
        gamemode_ctb = 'role_ctb', 'osu!catch'
        gamemode_mania = 'role_mania', 'osu!mania'

    @role_group.command(name='set')
    async def role_set(self, interaction: discord.Interaction, type: Roles, role: discord.Role):
        """
        Associate discord role with a role type in the database

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        type (Roles): The type of role to set
        role (discord.Role): The role to set
        """

        await self.__role_setter(interaction, role=role, role_variable=type.value[0], role_name=type.value[1])

    @role_group.command(name='remove')
    async def role_remove(self, interaction: discord.Interaction, type: Roles):
        """
        Remove a role from the database

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        type (Roles): The type of role to remove
        """

        await self.__role_setter(interaction, role=None, role_variable=type.value[0], role_name=type.value[1])

    @role_group.command(name='show')
    async def role_show(self, interaction: discord.Interaction):
        """
        Show all role associations to database

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        embed = discord.Embed(title='Role associations')
        for role in self.Roles:
            role_id = getattr(guild, role.value[0])
            if role_id:
                discord_role = interaction.guild.get_role(role_id)
                embed.add_field(name=role.value[1], value=discord_role.mention)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Settings(bot))
