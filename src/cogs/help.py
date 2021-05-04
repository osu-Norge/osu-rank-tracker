from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command(hidden=True)
    async def help(self, ctx, *command):

        if not command:
            for cog in self.bot.cogs.values():
                embed = discord.Embed(color=ctx.me.color, title=cog.qualified_name)
                embed.set_author(name=ctx.me.name, icon_url=ctx.me.avatar_url)

                for command in cog.get_commands():
                    if not command.hidden or not command.enabled:
                        embed.add_field(name=command.name, value=command.help, inline=False)

                if embed.fields:
                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
