

from contextlib import contextmanager
import discord


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


def get_color(discord_object: discord.User | discord.Member | discord.Role) -> discord.Color:
    """
    Returns the user's top role color

    Parameters
    -----------
    discord_object (discord.User|discord.Member|discord.Role): A discord object that has a color attribute

    Returns
    -----------
    (discord.Color): The user's displayed color
    """

    if hasattr(discord_object, 'color') and str(discord_object.color) != '#000000':
        return discord_object.color

    return discord.Colour(0x99AAB5)

