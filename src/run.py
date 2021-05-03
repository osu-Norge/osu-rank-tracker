from discord.ext import commands
import discord

from codecs import open
import yaml
from os import listdir
from time import time

from cogs.utils.database import Guild, Database

from typing import List


with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

intents = discord.Intents.all()
mentions = discord.AllowedMentions(everyone=False)

Database().init_db()


async def get_prefix(bot: commands.Bot, message: discord.Message) -> List[str]:
    """
    Fetches the on_message guild prefix from the database. If not found, it uses the default prefix.

    Parameters
    ----------
    bot (commands.Bot): A bot instance
    message (discord.Message): A Discord message object

    Returns
    ----------
    list[str]: The list of prefixes. In this case the list contains a single prefix
    """

    guild_prefix = await Guild(message.guild.id).get_prefix()
    if guild_prefix:
        return commands.when_mentioned_or(guild_prefix)(bot, message)
    else:
        return commands.when_mentioned_or(config['bot']['prefix'])(bot, message)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            case_insensitive=True,
            intents=intents,
            allowed_mentions=mentions
        )

        self.prefix = config['bot']['prefix']
        self.presence = config['bot'].get('presence', {})

        self.osu_v1 = config['api'].get('osu_v1', {})
        self.osu_v2 = config['api'].get('osu_v2', {})

        self.emoji = config.get('emoji', {})
        self.misc = config.get('misc', {})


bot = Bot()


activities = {
    'playing': 0,
    'listening': 2,
    'watching': 3
}
if bot.presence['activity'].lower() in activities:
    activity_type = activities[bot.presence['activity'].lower()]
else:
    print('Presence activity type is not valid. Check your config file! ' +
          'Falling back to default activity type (playing).')
    activity_type = 0


@bot.event
async def on_ready():
    if not hasattr(bot, 'uptime'):
        bot.uptime = time()

    for file in listdir('./src/cogs'):
        if file.endswith('.py'):
            name = file[:-3]
            bot.load_extension(f'cogs.{name}')

    print(f'Username:        {bot.user.name}')
    print(f'ID:              {bot.user.id}')
    print(f'Version:         {discord.__version__}')
    print('.' * 50 + '\n')
    await bot.change_presence(
        activity=discord.Activity(type=activity_type, name=bot.presence['message']),
        status=discord.Status.online
    )


bot.run(config['bot']['token'], bot=True, reconnect=True)
