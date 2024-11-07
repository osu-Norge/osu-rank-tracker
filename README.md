<div align="center">
  <h1>osu! Rank Tracker</h1>

<p>A Discord bot that keeps track of members' osu! ranks and updates their roles accordingly.</p>
</div>

## Features (\* = new in rewrite)

- Updates roles every 12 hours
- Users can pick their desired gamemode to be tracked
- OAuth2 authentication with osu!\*
- Slash commands\*
- Automatic role removal/added on registration (you can essentially lock people out of the server until they've registered)
- Blacklist osu! users
- Whitelist osu! users from certain countries

## Setup

### Prerequisites

- Postgresql database
- Python 3.10+
- osu!API v2 API key

This README will assume you have managed to set all of these up correclty.

### Presteps - Configuration

Both hosting options below require you to create a config.

Make a copy of [config.yaml.example](src/config/config.yaml.example) and remove the `.example` part. Now edit the config to your liking!

### Option 1 - Docker

Run `docker-compose up` and you should be good!

### Option 2 - Manual

1. Install dependencies

```
python -m pip install -r requirements.txt
```

This assumes that `python` points to a python3.10+ installation.

2. Run the bot

```
python src/run.py
``

## Invite

If you don't feel like hosting the bot yourself you can [invite]() our instance to your server!

## Contributing

Even though the bot has recently been rewritten, it is quite the mess. All contributions are much appreciated!

Please read [CONTRIBUTING.md](CONTRIBUTING.md).
