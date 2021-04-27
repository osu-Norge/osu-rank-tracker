from discord.ext import commands
import discord

from cogs.utils.database import Guild


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


def setup(bot):
    bot.add_cog(Settings(bot))
