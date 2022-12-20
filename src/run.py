from codecs import open
from os import listdir
from time import time

import discord
from discord.ext import commands
import yaml

import cogs.utils.database as database
from logger import BotLogger


with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

database.Database().init_db()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config['bot']['prefix']),
            case_insensitive=True,
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(everyone=False)
        )

        self.logger = BotLogger().logger  # Initialize logger

        self.presence = config['bot'].get('presence', {})
        self.osu_v1 = config['api'].get('osu_v1', {})
        self.osu_v2 = config['api'].get('osu_v2', {})
        self.emoji = config.get('emoji', {})
        self.misc = config.get('misc', {})
        self.server_port = config['server'].get('port', 80)

    async def setup_hook(self):
        # Load cogs
        for file in listdir('./src/cogs'):
            if file.endswith('.py'):
                name = file[:-3]
                await bot.load_extension(f'cogs.{name}')

        # Sync slash commands to Discord
        if config.get('config_mode') == 'prod':
            await self.tree.sync()
        else:
            self.tree.copy_global_to(guild=discord.Object(id=config['dev_guild_id']))
            await self.tree.sync(guild=discord.Object(id=config['dev_guild_id']))


bot = Bot()


@bot.event
async def on_ready():
    if not hasattr(bot, 'uptime'):
        bot.uptime = time()

    print(f'Username:        {bot.user.name}')
    print(f'ID:              {bot.user.id}')
    print(f'Version:         {discord.__version__}')
    print('.' * 50 + '\n')

    # Set initial presence
    # Presence status
    status_types = {
        'online': discord.Status.online,
        'dnd': discord.Status.dnd,
        'idle': discord.Status.idle,
        'offline': discord.Status.offline,
    }
    status_type = status_types.get(bot.presence['type'].lower(), discord.Status.online)

    # Presence actitivity
    activities = {'playing': 0, 'listening': 2, 'watching': 3}
    activity_type = activities.get(bot.presence['activity'].lower(), 0)

    await bot.change_presence(
        activity=discord.Activity(type=activity_type, name=bot.presence.get('message')),
        status=status_type
    )


bot.run(config['bot']['token'], reconnect=True)
