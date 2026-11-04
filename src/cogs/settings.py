import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from iso3166 import countries

from cogs.utils import database, discord_utils, embed_templates
from cogs.utils.osu_api import Gamemode, OsuApi


class Settings(commands.Cog):
    """Manage guild settings"""

    def __init__(self, bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

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

    async def _role_setter(
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
        interaction (discord.Interaction): The slash command interaction
        role (discord.Role | None): The role to set, or None to reset it
        role_variable (str): The database column name
        role_name (str): The name of the role setting, as shown in Discord
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if role:
            setattr(guild, role_variable, role.id)
        else:
            setattr(guild, role_variable, None)

        await guild_table.save(guild)

        if not role:
            embed = embed_templates.success(f'**{role_name}** no longer has a role')
            return await interaction.response.send_message(embed=embed)

        embed = embed_templates.success(f'{role.mention} is now set for **{role_name}**')
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.command()
    async def setup(self, interaction: discord.Interaction):
        """
        Automatic setup wizard for the bot

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        await interaction.response.send_message('This feature is not yet implemented')

    @settings_group.command()
    async def show(self, interaction: discord.Interaction):
        """
        Show all bot settings for the guild

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        await interaction.response.send_message('This feature is not yet implemented')

    @settings_group.command()
    async def reset(self, interaction: discord.Interaction):
        """
        Reset all settings to default

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
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
    @app_commands.describe(country_code='Country code or English name, e.g. NO, NOR or Norway')
    async def whitelist_add(self, interaction: discord.Interaction, country_code: str):
        """
        Add a country to the whitelist

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
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
    @app_commands.describe(country_code='Country code or English name, e.g. NO, NOR or Norway')
    async def whitelist_remove(self, interaction: discord.Interaction, country_code: str):
        """
        Remove a country from the whitelist

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
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
        interaction (discord.Interaction): The slash command interaction
        """

        guild = await database.GuildTable().get(interaction.guild.id)

        if not guild.whitelisted_countries:
            embed = embed_templates.error_warning('No countries are whitelisted!')
            return await interaction.response.send_message(embed=embed)

        names = {code: country.name for code in guild.whitelisted_countries if (country := countries.get(code, None))}
        lines = [f'{self._flag(code)} {names[code]} ({code})' for code in sorted(names, key=names.get)]
        lines += [f'{code} (unknown country code)' for code in guild.whitelisted_countries if code not in names]
        await discord_utils.send_paginated(interaction, f'Whitelisted countries ({len(lines)})', lines)

    @staticmethod
    def _flag(country_code: str) -> str:
        """
        Returns the flag emoji of a country

        Parameters
        ----------
        country_code (str): The ISO 3166 alpha-2 country code

        Returns
        ----------
        (str): The flag emoji, made of the two regional indicator symbols for the code
        """

        return ''.join(chr(0x1F1E6 + ord(letter) - ord('A')) for letter in country_code.upper())

    @blacklist_group.command(name='add')
    @app_commands.describe(osu_user='osu! username or user ID')
    async def blacklist_add(self, interaction: discord.Interaction, osu_user: str):
        """
        Add an osu user to the blacklist

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        osu_user (str): The osu! user to add to the blacklist
        """

        user = await OsuApi.get_user(osu_user, Gamemode.from_name('standard'))
        if not user:
            embed = embed_templates.error_warning('Invalid osu! user')
            return await interaction.response.send_message(embed=embed)

        user_id = user.get('id')
        username = user.get('username')

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
    @app_commands.describe(osu_user='osu! username or user ID')
    async def blacklist_remove(self, interaction: discord.Interaction, osu_user: str):
        """
        Remove an osu user from the blacklist

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        osu_user (str): The osu! user to remove from the blacklist
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)
        blacklist = guild.blacklisted_osu_users or []

        # Remove blacklisted IDs without looking them up, as restricted or deleted accounts can't be looked up
        if osu_user.isdigit() and int(osu_user) in blacklist:
            user_id, username = int(osu_user), None
        else:
            user = await OsuApi.get_user(osu_user, Gamemode.from_name('standard'))
            if not user:
                embed = embed_templates.error_warning('Invalid osu! user')
                return await interaction.response.send_message(embed=embed)

            user_id = user.get('id')
            username = user.get('username')

        if user_id not in blacklist:
            embed = embed_templates.error_warning('User is not blacklisted!')
            return await interaction.response.send_message(embed=embed)

        blacklist.remove(user_id)
        guild.blacklisted_osu_users = blacklist
        await guild_table.save(guild)

        name = f'[{username}](https://osu.ppy.sh/users/{user_id}) ({user_id})' if username else \
            f'[{user_id}](https://osu.ppy.sh/users/{user_id})'
        embed = embed_templates.success(f'{name} is no longer blacklisted!')
        await interaction.response.send_message(embed=embed)

    @blacklist_group.command(name='show')
    async def blacklist_show(self, interaction: discord.Interaction):
        """
        Show the osu user blacklist

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        guild = await database.GuildTable().get(interaction.guild.id)
        blacklist = guild.blacklisted_osu_users

        if not blacklist:
            embed = embed_templates.error_warning('No users are blacklisted!')
            return await interaction.response.send_message(embed=embed)

        # Looking up a long blacklist can take longer than Discord waits for a response
        await interaction.response.defer()

        try:
            usernames = await OsuApi.get_usernames(blacklist)
        except aiohttp.ClientError:
            usernames = None  # Fall back to showing the IDs

        if usernames is None:
            lines = [f'[{user_id}](https://osu.ppy.sh/users/{user_id})' for user_id in blacklist]
        else:
            # No markdown escaping: Discord shows the backslashes in link text, and osu! usernames can't contain * or `
            found = sorted((i for i in blacklist if i in usernames), key=lambda i: usernames[i].lower())
            lines = [f'[{usernames[i]}](https://osu.ppy.sh/users/{i})' for i in found]
            # Keep the ID of accounts without a name, as it's needed to remove them
            lines += [f'{user_id} (restricted or deleted)' for user_id in blacklist if user_id not in usernames]

        title = f'Blacklisted osu! users ({len(lines)})'
        if usernames is None:
            title += ' - couldn\'t look up usernames'
        await discord_utils.send_paginated(interaction, title, lines)

    # The role settings by database column, with the names shown in Discord
    ROLE_TYPES = {
        'role_add': 'Given on registration',
        'role_remove': 'Removed on registration',
        'role_1_digit': '1-digit rank (#1–9)',
        'role_2_digit': '2-digit rank (#10–99)',
        'role_3_digit': '3-digit rank (#100–999)',
        'role_4_digit': '4-digit rank (#1,000–9,999)',
        'role_5_digit': '5-digit rank (#10,000–99,999)',
        'role_6_digit': '6-digit rank (#100,000–999,999)',
        'role_7_digit': '7-digit rank (#1,000,000+)',
        'role_standard': 'osu!standard players',
        'role_taiko': 'osu!taiko players',
        'role_ctb': 'osu!catch players',
        'role_mania': 'osu!mania players',
    }
    ROLE_TYPE_CHOICES = [app_commands.Choice(name=name, value=column) for column, name in ROLE_TYPES.items()]

    @role_group.command(name='set')
    @app_commands.rename(role_type='type')
    @app_commands.choices(role_type=ROLE_TYPE_CHOICES)
    @app_commands.describe(
        role_type='What the role is for: a rank range, a gamemode, or given/removed on registration',
        role='The Discord role to use'
    )
    async def role_set(self, interaction: discord.Interaction, role_type: app_commands.Choice[str], role: discord.Role):
        """
        Associate discord role with a role type in the database

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        role_type (app_commands.Choice[str]): The role setting to change
        role (discord.Role): The role to set
        """

        await self._role_setter(interaction, role=role, role_variable=role_type.value, role_name=role_type.name)

    @role_group.command(name='remove')
    @app_commands.rename(role_type='type')
    @app_commands.choices(role_type=ROLE_TYPE_CHOICES)
    @app_commands.describe(role_type='Which role to unset')
    async def role_remove(self, interaction: discord.Interaction, role_type: app_commands.Choice[str]):
        """
        Remove a role from the database

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        role_type (app_commands.Choice[str]): The role setting to reset
        """

        await self._role_setter(interaction, role=None, role_variable=role_type.value, role_name=role_type.name)

    @role_group.command(name='show')
    async def role_show(self, interaction: discord.Interaction):
        """
        Show all role associations to database

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        embed = discord.Embed(title='Role associations')
        for column, name in self.ROLE_TYPES.items():
            role_id = getattr(guild, column)
            if role_id:
                discord_role = interaction.guild.get_role(role_id)
                embed.add_field(name=name, value=discord_role.mention)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(Settings(bot))
