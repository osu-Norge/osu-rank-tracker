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


def paginate(lines: list[str], max_lines: int = 20, max_chars: int = 4096) -> list[str]:
    """
    Splits lines into pages that fit in an embed description

    Parameters
    ----------
    lines (list[str]): The lines to split
    max_lines (int): The most lines on one page. Defaults to 20
    max_chars (int): The most characters on one page. Defaults to 4096, Discord's limit for embed descriptions

    Returns
    ----------
    (list[str]): The pages, with the lines joined by newlines
    """

    pages = []
    page = []
    length = 0
    for line in lines:
        line = line[:max_chars]
        if page and (len(page) == max_lines or length + 1 + len(line) > max_chars):
            pages.append('\n'.join(page))
            page, length = [], 0
        length += len(line) + (1 if page else 0)
        page.append(line)

    if page:
        pages.append('\n'.join(page))

    return pages
