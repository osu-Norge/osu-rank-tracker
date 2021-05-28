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
