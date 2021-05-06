from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    async def filter_command(self, ctx: commands.Context, command: commands.Command) -> bool:
        """
        Filters commands that fails check decorators. Also filters disabled commands

        Parameters
        ----------
        ctx (discord.ext.commands.Context): The Discord context
        command (discord.ext.commands.Command): The Discord command object

        Returns
        ----------
        bool: Whether or not the command is executable and viewable based on Discord context.
        """

        try:
            return await command.can_run(ctx)
        except commands.CommandError:
            return False

    @commands.command(hidden=True)
    async def help(self, ctx, *commands):
        """
        Displays the bot help. Commands and how to use them.
        """

        if not commands:
            for cog in self.bot.cogs.values():
                embed = discord.Embed(color=ctx.me.color, title=cog.qualified_name)
                embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)

                for command in cog.get_commands():
                    if not command.hidden and await self.filter_command(ctx, command):
                        embed.add_field(name=command.name, value=command.help, inline=False)

                if embed.fields:
                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
