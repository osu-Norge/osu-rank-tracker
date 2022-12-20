from enum import Enum

import discord
from discord import app_commands
from discord.ext import commands
from iso3166 import countries

from cogs.utils import embed_templates
import cogs.utils.database as database
from cogs.utils.osu_api import OsuApi


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

    whitelist_group = app_commands.Group(name='whitelist', description='Manage country whitelist', parent=settings_group)
    blacklist_group = app_commands.Group(name='blacklist', description='Manage user blacklist', parent=settings_group)

    async def __role_setter(self, interaction: discord.Interaction, role: discord.Role, role_variable: str, role_name: str):
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

        if not hasattr(guild, role_variable):
            raise commands.CommandError

        setattr(guild, role_variable, role.id)
        await guild_table.save(guild)

        embed = embed_templates.success(interaction, text=f'{role.mention} has been set as the {role_name}!')
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

        pass

    @settings_group.command()
    async def show(self, interaction: discord.Interaction):
        """
        Show all bot settings for the guild

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        pass

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

        embed = embed_templates.success(interaction, text='All settings have been reset!')
        await interaction.response.send_message(embed=embed)

    @settings_group.command()
    async def regchannel(self, interaction: discord.Interaction, channel: discord.TextChannel, *, remove_after_message: str = None):
        """
        Set the registration channel

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        channel (discord.TextChannel): The channel to set as the registration channel
        remove_after_message (str): The message to delete all messages after
        """

        # TODO: remove_after_message

        channel_table = database.ChannelTable()
        db_channel = await channel_table.get(channel.id)

        if remove_after_message:
            db_channel.clean_after_message_id = remove_after_message.id
        else:
            db_channel.clean_after_message_id = None

        await channel_table.save(db_channel)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)
        guild.registration_channel = channel.id
        await guild_table.save(guild)

        if remove_after_message:
            embed = embed_templates.success(
                interaction,
                text=f'Registration channel has been set to {channel.mention} & all messages in the channel after ' +
                     f'[this message]({remove_after_message.jump_url}) will be deleted on registration'
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = embed_templates.success(interaction, text=f'Registration channel has been set to {channel.mention}')
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
                interaction, text='Invalid country! Make you enter a valid country or country code\n\n' +
                          'Click [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for more info'
            )
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.whitelisted_countries:
            guild.whitelisted_countries = []

        if country.alpha2 in guild.whitelisted_countries:
            embed = embed_templates.error_warning(interaction, text='Country is already in the whitelist')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries.append(country.alpha2)
        await guild_table.save(guild)

        embed = embed_templates.success(interaction, text=f'`{country.name}` has been added to the whitelist')
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
                interaction, text='Invalid country! Make you enter a valid country or country code\n\n' +
                                  'Click [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for more info'
            )
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.whitelisted_countries or country.alpha2 not in guild.whitelisted_countries:
            embed = embed_templates.error_warning(interaction, text='Country is not in the whitelist')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries.remove(country.alpha2)
        await guild_table.save(guild)

        embed = embed_templates.success(interaction, text=f'`{country.name}` has been removed from the whitelist')
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
            embed = embed_templates.error_warning(interaction, text='No countries are whitelisted!')
            return await interaction.response.send_message(embed=embed)

        guild.whitelisted_countries = [f'`{country}`' for country in guild.whitelisted_countries]

        if len(guild.whitelisted_countries) > 2048:
            embed = embed_templates.error_warning(interaction, text='Whitelist is too long to be displayed!')
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

        user = await OsuApi.get_user(osu_user, 'standard')
        user_id = user.get('id')
        username = user.get('username')

        if not user:
            embed = embed_templates.error_warning(interaction, text='Invalid osu! user')
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.blacklisted_osu_users:
            guild.blacklisted_osu_users = []

        if user.get('id') in guild.blacklisted_osu_users:
            embed = embed_templates.error_warning(interaction, text='User is already blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users.append(user_id)
        await guild_table.save(guild)

        embed = embed_templates.success(
            interaction,
            text=f'[{username}](https://osu.ppy.sh/users/{user_id}) ({user_id}) is now blacklisted!'
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
        
        user = await OsuApi.get_user(osu_user, 'standard')
        user_id = user.get('id')
        username = user.get('username')

        if not user:
            embed = embed_templates.error_warning(interaction, text='Invalid osu! user')
            return await interaction.response.send_message(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)

        if not guild.blacklisted_osu_users or user_id not in guild.blacklisted_osu_users:
            embed = embed_templates.error_warning(interaction, text='User is not blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users.remove(user_id)
        await guild_table.save(guild)

        embed = embed_templates.success(
            interaction,
            text=f'[{username}](https://osu.ppy.sh/users/{user_id}) ({user_id}) is no longer blacklisted!'
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
            embed = embed_templates.error_warning(interaction, text='No users are blacklisted!')
            return await interaction.response.send_message(embed=embed)

        guild.blacklisted_osu_users = [f'[{user}](https://osu.ppy.sh/users/{user})' for user in guild.blacklisted_osu_users]

        if len(guild.blacklisted_osu_users) > 2048:
            embed = embed_templates.error_warning(interaction, text='Blacklist is too long to be displayed!')
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(title='Blacklisted users (IDs)')
        embed.description = ', '.join(guild.blacklisted_osu_users)
        await interaction.response.send_message(embed=embed)


    class Roles(Enum):
        """
        List of roles that can be set in the database. Serves as autocomplete for the role command
        """

        moderator = 'role_moderator', 'moderator'
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

    @settings_group.command()
    async def role(self, interaction: discord.Interaction, type: Roles, role: discord.Role):
        """
        Associate discord role with a role type in the database

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        type (Roles): The type of role to set
        role (discord.Role): The role to set
        """

        await self.__role_setter(interaction, role=role, role_variable=type.value[0], role_name=type.value[1])


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(Settings(bot))
