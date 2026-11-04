import asyncio
import functools
from contextlib import contextmanager

import aiohttp
import discord

from logger import logger

# The exceptions discord.ext.tasks.Loop already retries with backoff
LOOP_RETRIED_EXCEPTIONS = (
    OSError,
    discord.GatewayNotFound,
    discord.ConnectionClosed,
    aiohttp.ClientError,
    asyncio.TimeoutError,
)


@contextmanager
def ignore_exception(*exceptions: Exception):
    """
    Ignores the given exceptions

    Parameters
    ----------
    *exceptions tuple[Exception]: The exceptions you want to ignore
    """

    try:
        yield
    except exceptions:
        pass


def log_errors(coro):
    """
    Keeps a background loop running after an unexpected exception by logging it instead.
    Place it under @tasks.loop. Exceptions the loop retries by itself are re-raised, so it still backs off and retries

    Parameters
    ----------
    coro (Callable): The loop's coroutine function
    """

    @functools.wraps(coro)
    async def wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except LOOP_RETRIED_EXCEPTIONS:
            raise
        except Exception:
            logger.exception(f'Unhandled exception in background loop {coro.__qualname__}, continuing')

    return wrapper
