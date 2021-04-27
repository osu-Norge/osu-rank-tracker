async def get_gamemode_id(gamemode: str) -> str:
    """
    Translates the osu! gamemode names to their respective values

    Parameters
    -----------
    gamemode (str): Name of the gamemode

    Returns
    -----------
    int: gamemode id
    """

    if gamemode is None:
        gamemode = 'standard'

    gamemode = gamemode.lower()

    gamemodes = {
        'standard': 0,
        'std': 0,
        'osu': 0,
        'osu!': 0,
        'osu!standard': 0,
        'taiko': 1,
        'osu!taiko': 1,
        'ctb': 2,
        'catch the beat': 2,
        'catch': 2,
        'fruits': 2,
        'osu!catch': 2,
        'mania': 3,
        'osu!mania': 3
    }
    if gamemode in gamemodes:
        return gamemodes[gamemode]


async def get_gamemode_name(gamemode: str) -> str:
    """
    Converts gamemode id to its name

    Parameters
    -----------
    gamemode (str): Name of the gamemode

    Returns
    -----------
    int: gamemode id
    """

    gamemodes = {
        0: 'Standard',
        1: 'Taiko',
        2: 'Catch The Beat',
        3: 'Mania'
    }
    return gamemodes[gamemode]


async def get_gamemode_url(gamemode_id: int) -> str:
    """
    Converts gamemode id to url name

    Parameters
    -----------
    gamemode_id (int): Name of the gamemode

    Returns
    -----------
    int: gamemode url name
    """

    gamemode_url = {
        0: 'osu',
        1: 'taiko',
        2: 'fruits',
        3: 'mania'
    }
    return gamemode_url[gamemode_id]


async def validate_rank(pp_rank: str) -> int:
    """
    Checks whether or not the given rank is a int and in the correct range

    Parameters
    -----------
    pp_rank (str): The rank returned by the osu!api

    Returns
    -----------
    int: The rank converted to integer
    """

    try:
        rank = int(pp_rank)
    except TypeError:
        rank = 0

    return rank
