import traceback

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import embed_templates


class Errors(commands.Cog):
    """Error handlers for commands"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot
        bot.tree.on_error = self.on_app_command_error  # Set error handler for slash commands

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        """
        Logs prefix command execution metadata

        Parameters
        ----------
        ctx (commands.Context): The command context
        """

        self.bot.logger.info(
            f'{"❌ " if ctx.command_failed else "✔ "} {ctx.command} | ' +
            f'{ctx.author.name} ({ctx.author.id}) | ' +
            f'{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}'
        )

    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: app_commands.Command | app_commands.ContextMenu
    ):
        """
        Logs slash command execution metadata

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        command (app_commands.Command | app_commands.ContextMenu): Command object
        """

        self.bot.logger.info(
            f'{"❌ " if interaction.command_failed else "✔ "} {command.name} | ' +
            f'{interaction.user.name} ({interaction.user.id}) | ' +
            f'{interaction.guild_id}-{interaction.channel_id}-{interaction.id}'
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        Handle prefix command errors

        Parameters
        ----------
        ctx (commands.Context): The command context
        error (commands.CommandError): The error the command raised
        """

        # Failed invocations shouldn't count towards the cooldown, but the cooldown error itself must not reset it
        if ctx.command and not isinstance(error, commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        # Ignore command's own error handling
        if hasattr(ctx.command, 'on_error'):
            return

        # Ignored errors
        ignored = commands.CommandNotFound
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        send_help = (
            commands.MissingRequiredArgument,
            commands.TooManyArguments,
            commands.BadArgument
        )
        if isinstance(error, send_help):
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = ', '.join(error.missing_permissions)
            embed = embed_templates.error_warning('I\'m missing the following permissions:\n\n' +
                                                  f'```\n{permissions}\n```')
            return await ctx.reply(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            permissions = ', '.join(error.missing_permissions)
            embed = embed_templates.error_warning('You\'re missing the following permissions:\n\n' +
                                                  f'```\n{permissions}\n```')
            return await ctx.reply(embed=embed)

        elif isinstance(error, commands.NotOwner):
            embed = embed_templates.error_fatal('Only the bot owner can do this')
            return await ctx.reply(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            embed = embed_templates.error_warning('The command has just been invoked\n' +
                                                  f'Try again in `{error.retry_after:.1f}` seconds.')
            return await ctx.reply(embed=embed)

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                embed = embed_templates.error_warning('This command is only invokable in guilds')
                await ctx.reply(embed=embed)
            except discord.errors.Forbidden:  # Thrown if bot is blocked by the user or if the user has closed their DMs
                self.bot.logger.info('DM Blocked!')
            return

        elif isinstance(error, commands.DisabledCommand):
            return

        elif isinstance(error, commands.CheckFailure):
            return

        embed = embed_templates.error_fatal('An unknown error occurred')
        await ctx.reply(embed=embed)

        # Log full exception to file
        self.bot.logger.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle slash command errors

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        error (app_commands.AppCommandError): The error the command raised
        """

        # Log command usage, just in case
        if interaction.command:
            await self.on_app_command_completion(interaction, interaction.command)

        if isinstance(error, app_commands.BotMissingPermissions):
            permissions = ', '.join(error.missing_permissions)
            embed = embed_templates.error_warning('I\'m missing the following permissions:\n\n' +
                                                  f'```\n{permissions}\n```')
            return await self._send_error(interaction, embed)

        elif isinstance(error, app_commands.MissingPermissions):
            permissions = ', '.join(error.missing_permissions)
            embed = embed_templates.error_warning('You\'re missing the following permissions:\n\n' +
                                                  f'```\n{permissions}\n```')
            return await self._send_error(interaction, embed)

        elif isinstance(error, app_commands.CommandOnCooldown):
            embed = embed_templates.error_warning('The command has just been invoked\n' +
                                                  f'Try again in `{error.retry_after:.1f}` seconds.')
            return await self._send_error(interaction, embed)

        # Log full exception to file
        self.bot.logger.error(''.join(traceback.format_exception(type(error), error, error.__traceback__)))

        embed = embed_templates.error_fatal('An unknown error occurred!')
        await self._send_error(interaction, embed)

    @staticmethod
    async def _send_error(interaction: discord.Interaction, embed: discord.Embed):
        """
        Send an error message, as a followup if the command has already responded or deferred

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        embed (discord.Embed): The error message
        """

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(Errors(bot))
