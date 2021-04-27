import discord


async def get_user_color(user: discord.User) -> discord.Color:
    """
    Returns the user's top role color

    Parameters
    -----------
    user (discord.User): A discord user or member object

    Returns
    -----------
    (discord.Color): The user's displayed color
    """

    try:
        if str(user.color) != '#000000':
            return user.color
    except AttributeError:
        pass

    return discord.Colour(0x99AAB5)
