from discord.ext import commands


class HelpCommand(commands.MinimalHelpCommand):
    async def filter_command(self, command: commands.Command) -> bool:
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
            return await command.can_run(self.context)
        except commands.CommandError:
            return False


class Help(commands.Cog):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
