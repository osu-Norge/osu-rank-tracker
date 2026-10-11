from codecs import open
from os import listdir
from threading import Thread
from time import time

import discord
import uvicorn
import yaml
from discord.ext import commands

import cogs.utils.database as database
from logger import logger
from verification_server.server import app as verification_app

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

        self.logger = logger

        self.presence = config['bot'].get('presence', {})
        self.emoji = config.get('emoji', {})
        self.misc = config.get('misc', {})

        # Start verification server
        verification_app.state.bot = self
        server_port = config['server'].get('port', 80)
        server = Thread(
            target=uvicorn.run,
            args=(verification_app,),
            kwargs={'port': server_port, 'host': '0.0.0.0'},
            daemon=True,
        )
        server.start()

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

    bot.logger.info(f'Username:        {bot.user.name}')
    bot.logger.info(f'ID:              {bot.user.id}')
    bot.logger.info(f'Version:         {discord.__version__}')
    bot.logger.info('.' * 50)

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
