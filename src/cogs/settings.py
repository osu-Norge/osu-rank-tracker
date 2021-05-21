from discord.ext import commands
import discord

import cogs.utils.database as database
from cogs.utils import embed_templates


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def role_setter(self, ctx: commands.context, role: str, role_variable: str, role_name: str):
        """
        Validates a role and puts it into the database. Sends confirmation message to Discord

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The current Discord context
        role (str): The user inputted role name, id or mention
        role_variable (str): The database column name
        role_name (str): The role name that will be displayed in the confirmation message on Discord
        """

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.RoleNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid role given!')
            await ctx.send(embed=embed)
            return

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)

        if not hasattr(guild, role_variable):
            raise commands.CommandError

        setattr(guild, role_variable, role.id)
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'{role.mention} has been set as the {role_name} role!')
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command()
    async def setup(self, ctx):
        """
        Automatic setup wizard for the bot
        """
        pass

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.group()
    async def settings(self, ctx):
        """
        Manage bot settings
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @settings.command()
    async def prefix(self, ctx, prefix: str):
        """
        Set the serverprefix
        """

        if len(prefix) > 255:
            embed = await embed_templates.error_warning(ctx, text='Maximum prefix length is 255 characters')
            return await ctx.send(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.prefix = prefix
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'Prefix is now set to `{prefix}`')
        await ctx.send(embed=embed)

    @settings.command()
    async def regchannel(self, ctx, channel: str, remove_after_message: str = None):
        """
        Set the registration channel
        """

        try:
            channel = await commands.TextChannelConverter().convert(ctx, channel)
        except commands.errors.ChannelNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid channel given!')
            return await ctx.send(embed=embed)

        channel_table = database.ChannelTable()
        db_channel = await channel_table.get(channel.id)

        if remove_after_message:
            db_channel.clean_after_message_id = remove_after_message

            try:
                remove_after_message = await commands.MessageConverter().convert(ctx, remove_after_message)
            except commands.errors.MessageNotFound:
                embed = await embed_templates.error_warning(ctx, text='Invalid message given!')
                return await ctx.send(embed=embed)

            embed = await embed_templates.success(
                ctx,
                text=f'Registration channel has been set to {channel.mention} & all messages in the channel after ' +
                     f'[this message]({remove_after_message.jump_url}) will be deleted on registration'
            )
        else:
            db_channel.clean_after_message_id = None
            embed = await embed_templates.success(ctx, text=f'Registration channel has been set to {channel.mention}')

        await channel_table.save(db_channel)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.registration_channel = channel.id
        await guild_table.save(guild)

        await ctx.send(embed=embed)

    @settings.group()
    async def whitelist(self, ctx):
        """
        Manage country whitelist
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @whitelist.command()
    async def add(self, ctx, country_code: str):
        """
        Add a country to the whitelist
        """

        if len(country_code) != 2:
            embed = await embed_templates.error_warning(
                ctx, text='Make sure the country code is in the correct format\n\n' +
                          'Click [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) for more info'
            )
            return await ctx.send(embed=embed)

        country_code = country_code.lower()

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)

        if not guild.whitelisted_countries:
            guild.whitelisted_countries = []

        if country_code in guild.whitelisted_countries:
            embed = await embed_templates.error_warning(ctx, text='Country is already in the whitelist')
            return await ctx.send(embed=embed)

        guild.whitelisted_countries.append(country_code)
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'`{country_code}` has been added to the whitelist')
        await ctx.send(embed=embed)

    @whitelist.command()
    async def remove(self, ctx, country_code: str):
        """
        Remove a country from the whitelist
        """

        country_code = country_code.lower()

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)

        if not guild.whitelisted_countries or country_code not in guild.whitelisted_countries:
            embed = await embed_templates.error_warning(ctx, text='Country is not in the whitelist')
            return await ctx.send(embed=embed)

        guild.whitelisted_countries.remove(country_code)
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'`{country_code}` has been removed from the whitelist')
        await ctx.send(embed=embed)

    @whitelist.command()
    async def show(self, ctx):
        """
        Show the country whitelist
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)

        if not guild.whitelisted_countries:
            embed = await embed_templates.error_warning(ctx, text='No countries are whitelisted!')
            return await ctx.send(embed=embed)

        guild.whitelisted_countries = [f'`{country}`' for country in guild.whitelisted_countries]

        if len(guild.whitelisted_countries) > 2048:
            embed = await embed_templates.error_warning(ctx, text='Whitelist is too long to be displayed!')
            return await ctx.send(embed=embed)

        embed = discord.Embed()
        embed.description = ', '.join(guild.whitelisted_countries)
        await ctx.send(embed=embed)

    @settings.group()
    async def role(self, ctx):
        """
        Manage roles
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @role.command()
    async def moderator(self, ctx, role: str):
        """
        Set the moderator role. Whoever has this role is able to change bot settings.
        """

        await self.role_setter(ctx, role=role, role_variable='role_moderator', role_name='moderator')

    @role.command()
    async def regadd(self, ctx, role: str):
        """
        Set a role that will be given when a user registers their account.
        """

        await self.role_setter(ctx, role=role, role_variable='role_add', role_name='registration add')

    @role.command()
    async def regremove(self, ctx, role: str):
        """
        Set a role that will be removed when a user registers their account.
        """

        await self.role_setter(ctx, role=role, role_variable='role_remove', role_name='registration remove')

    @role.command(name='1digit')
    async def digit1(self, ctx, role: str):
        """
        Set the 1 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_1_digit', role_name='1 digit')

    @role.command(name='2digit')
    async def digit2(self, ctx, role: str):
        """
        Set the 2 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_2_digit', role_name='2 digit')

    @role.command(name='3digit')
    async def digit3(self, ctx, role: str):
        """
        Set the 3 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_3_digit', role_name='3 digit')

    @role.command(name='4digit')
    async def digit4(self, ctx, role: str):
        """
        Set the 4 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_4_digit', role_name='4 digit')

    @role.command(name='5digit')
    async def digit5(self, ctx, role: str):
        """
        Set the 5 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_5_digit', role_name='5 digit')

    @role.command(name='6digit')
    async def digit6(self, ctx, role: str):
        """
        Set the 6 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_6_digit', role_name='6 digit')

    @role.command(name='7digit')
    async def digit7(self, ctx, role: str):
        """
        Set the 7 digit role
        """

        await self.role_setter(ctx, role=role, role_variable='role_7_digit', role_name='7 digit')

    @role.command(aliases=['osu!standard', 'std', 'osu', 'osu!'])
    async def standard(self, ctx, role: str):
        """
        Set the standard gamemode role
        """

        await self.role_setter(ctx, role=role, role_variable='role_standard', role_name='standard')

    @role.command(aliases=['osu!taiko'])
    async def taiko(self, ctx, role: str):
        """
        Set the taiko gamemode role
        """

        await self.role_setter(ctx, role=role, role_variable='role_taiko', role_name='taiko')

    @role.command(aliases=['osu!catch', 'catch', 'fruits'])
    async def ctb(self, ctx, role: str):
        """
        Set the catch the beat gamemode role
        """

        await self.role_setter(ctx, role=role, role_variable='role_ctb', role_name='catch the beat')

    @role.command(aliases=['osu!mania'])
    async def mania(self, ctx, role: str):
        """
        Set the mania gamemode role
        """

        await self.role_setter(ctx, role=role, role_variable='role_mania', role_name='mania')


def setup(bot):
    bot.add_cog(Settings(bot))
