from discord.ext import commands
import discord

import cogs.utils.database as database
from cogs.utils import embed_templates


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.RoleNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid role given!')
            return await ctx.send(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.role_moderator = role.id
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'{role.mention} has been set as the moderator role!')
        await ctx.send(embed=embed)

    @role.command()
    async def standard(self, ctx, role: str):
        """
        Set the standard gamemode role
        """

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.RoleNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid role given!')
            return await ctx.send(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.role_standard = role.id
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'{role.mention} has been set as the standard gamemode role!')
        await ctx.send(embed=embed)

    @role.command()
    async def taiko(self, ctx, role: str):
        """
        Set the taiko gamemode role
        """

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.RoleNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid role given!')
            return await ctx.send(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.role_taiko = role.id
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'{role.mention} has been set as the taiko gamemode role!')
        await ctx.send(embed=embed)

    @role.command(aliases=['catch'])
    async def ctb(self, ctx, role: str):
        """
        Set the catch the beat gamemode role
        """

        try:
            role = await commands.RoleConverter().convert(ctx, role)
        except commands.errors.RoleNotFound:
            embed = await embed_templates.error_warning(ctx, text='Invalid role given!')
            return await ctx.send(embed=embed)

        guild_table = database.GuildTable()
        guild = await guild_table.get(ctx.guild.id)
        guild.role_ctb = role.id
        await guild_table.save(guild)

        embed = await embed_templates.success(ctx, text=f'{role.mention} has been set as the catch the beat gamemode role!')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Settings(bot))
