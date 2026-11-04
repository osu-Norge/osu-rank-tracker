<div align="center">
  <h1>osu! Rank Tracker</h1>

<p>A Discord bot that keeps track of members' osu! ranks and updates their roles accordingly.</p>
</div>

## Features (\* = new in rewrite)

- Updates roles every 12 hours, at 00:00 and 12:00 UTC
- Users can pick their desired gamemode to be tracked
- OAuth2 authentication with osu!\*
- Slash commands\*
- Automatic role removal/added on registration (you can essentially lock people out of the server until they've registered)
- Blacklist osu! users
- Whitelist osu! users from certain countries

## Setup

### Prerequisites

- Postgresql database
- A Discord bot application with the privileged intents enabled (see below)
- [uv](https://docs.astral.sh/uv/getting-started/installation/), which installs the right Python version
- osu!API v2 API credentials

This README will assume you have managed to set all of these up correctly.

### Presteps - Discord application

The bot uses every gateway intent, including the privileged ones. In the [Discord Developer Portal](https://discord.com/developers/applications), open your application, go to **Bot** and enable **Presence Intent**, **Server Members Intent** and **Message Content Intent**. Otherwise the bot stops at startup with `PrivilegedIntentsRequired`.

### Presteps - Configuration

Both hosting options below require you to create a config.

Make a copy of [config.yaml.example](src/config/config.yaml.example) and remove the `.example` part. Now edit the config to your liking!

### Option 1 - Docker

Run `docker compose up` and you should be good!

The config is mounted into the container from `src/config/config.yaml`, not copied into the image, so changing it only needs a restart.

The bot logs to the console, which `docker compose logs` shows, and to `logs/discord.log`, which is kept outside the container.

If you have changed the specified port in the config remember to reflect that in the docker-compose file.

### Option 2 - Manual

1. Install dependencies

```
uv sync
```

2. Run the bot

```
uv run src/run.py
```

## Development

Set `config_mode` to anything other than `prod`, e.g. `dev`, and `dev_guild_id` to the ID of your test server. Slash commands are then only synced to that server instead of globally.

Use a separate bot application, with its own token, for development. If you run dev mode with the production bot's token, every command shows up twice in the test server: once as a global command and once as a server command. The bot logs a warning when this happens, and prod mode removes the test server's commands again if `dev_guild_id` is set. To check which application you're running, compare the bot ID logged at startup. If Discord still shows old commands, press Ctrl+R to reload it.

## Invite

If you don't feel like hosting the bot yourself you can [invite]() our instance to your server!

## Contributing

Even though the bot has recently been rewritten, it is quite the mess. All contributions are much appreciated!

Please read [CONTRIBUTING.md](CONTRIBUTING.md).
