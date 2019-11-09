from discord.ext import commands

import traceback
import sys
from datetime import datetime

from cogs.utils import Defaults


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        status = {False: '✔ ', True: '❌ '}
        print(f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} | ' +
              f'{ctx.command} {status[ctx.command_failed]} - ' +
              f'{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) | ' +
              f'{ctx.guild.id}-{ctx.channel.id}-{ctx.message.id}')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        try:
            self.bot.get_command(f'{ctx.command}').reset_cooldown(ctx)
        except AttributeError:
            pass

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = commands.CommandNotFound
        send_help = (commands.MissingRequiredArgument,
                     commands.TooManyArguments,
                     commands.BadArgument)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, send_help):
            self.bot.get_command(f'{ctx.command}').reset_cooldown(ctx)
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = ', '.join(error.missing_perms)
            return await Defaults.error_warning_send(ctx, text=f'Jeg mangler følgende tillatelser:\n\n' +
                                                               f'```\n{permissions}\n```')

        elif isinstance(error, commands.NotOwner):
            return await Defaults.error_fatal_send(ctx, text='Du er ikke båtteier')

        elif isinstance(error, commands.MissingPermissions):
            permissions = ', '.join(error.missing_perms)
            return await Defaults.error_warning_send(ctx, text=f'Du mangler følgende tillatelser:\n\n' +
                                                               f'```\n{permissions}\n```')

        elif isinstance(error, commands.CommandOnCooldown):
            return await Defaults.error_warning_send(ctx, text='Kommandoen har nettopp blitt brukt. Prøv igjen om ' +
                                                               f'`{error.retry_after:.1f}` sekunder.')

        elif isinstance(error, commands.NSFWChannelRequired):
            return await Defaults.error_fatal_send(ctx, text='Du må være i en NSFW-Kanal')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await Defaults.error_fatal_send(ctx, text=f'`{ctx.command}` kan ikke brukes i DMs')
            except:
                pass

        elif isinstance(error, commands.CheckFailure):
            return

        try:
            await Defaults.error_fatal_send(ctx, text='En ukjent feil oppstod. Be båtteier om å sjekke feilen')
        except:
            pass

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(Errors(bot))
