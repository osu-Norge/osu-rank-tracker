from discord.ext import commands
import discord

from cogs.utils.database import Guild
from cogs.utils import embed_templates


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx):
        """
        Automatic setup wizard for the bot
        """
        pass

    @commands.has_permissions(manage_guild=True)
    @commands.group('settings')
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

        guild = Guild(ctx.guild.id)
        await guild.set_prefix(prefix)

        embed = discord.Embed(color=discord.Color.green())
        embed.description = f'Prefix is now set to `{prefix}`'
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

        guild = Guild(ctx.guild.id)
        await guild.whitelist_add(country_code)

        embed = discord.Embed(color=discord.Color.green())
        embed.description = f'`{country_code}` has been added to the whitelist'
        await ctx.send(embed=embed)

    @whitelist.command()
    async def remove(self, ctx, country_code: str):
        """
        Remove a country from the whitelist
        """

        guild = Guild(ctx.guild.id)
        await guild.whitelist_remove(country_code)

        embed = discord.Embed(color=discord.Color.green())
        embed.description = f'`{country_code}` has been removed from the whitelist'
        await ctx.send(embed=embed)

    @whitelist.command()
    async def show(self, ctx):
        """
        Show the country whitelist
        """

        guild = Guild(ctx.guild.id)
        whitelist = await guild.get_whitelist()

        if not whitelist:
            embed = await embed_templates.error_warning(ctx, text='No countries are whitelisted!')
            return await ctx.send(embed=embed)

        whitelist_string = ''
        for country in whitelist:
            whitelist_string += f'`{country}`\n'

        if len(whitelist) > 2048:
            embed = await embed_templates.error_warning(ctx, text='Whitelist is too long to be displayed!')
            return await ctx.send(embed=embed)

        embed = discord.Embed()
        embed.description = whitelist
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Settings(bot))
