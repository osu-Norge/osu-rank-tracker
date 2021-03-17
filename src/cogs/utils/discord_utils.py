import discord


def get_user_color(user: discord.User) -> discord.Color:
    """
    Returns the user's top role color

    Parameters
    -----------
    user (discord.User): A discord user or member object

    Returns
    -----------
    (discord.Color): The user's displayed color

    """

    if str(user.color) != '#000000':
        return user.color

    return discord.Colour(0x99AAB5)
