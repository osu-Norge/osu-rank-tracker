from discord.ext import commands

import yaml

with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
    guild_id = config['guild']
    set_channel_id = config['set_channel']


def is_guild():
    """Checks whether or not a command is executed in the specified guild"""

    def predicate(ctx):
        guild = ctx.bot.get_guild(guild_id)
        return ctx.guild == guild
    return commands.check(predicate)


def is_set_channel():
    """Checks whether or not a command is executed in the specified channel"""

    def predicate(ctx):
        guild = ctx.bot.get_guild(guild_id)
        set_channel = guild.get_channel(set_channel_id)
        return ctx.message.channel == set_channel
    return commands.check(predicate)


def is_not_set_channel():
    """Checks whether or not a command is executed in the specified channel"""

    def predicate(ctx):
        guild = ctx.bot.get_guild(guild_id)
        set_channel = guild.get_channel(set_channel_id)
        return ctx.message.channel != set_channel
    return commands.check(predicate)
