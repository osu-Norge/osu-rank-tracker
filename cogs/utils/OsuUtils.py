from math import floor, log10


async def get_gamemode(gamemode):
    """Translates the osu! gamemode names to their respective values"""

    if gamemode is None:
        gamemode = 'standard'

    gamemode = gamemode.lower()

    gamemodes = {
        'standard': '0',
        'std': '0',
        'osu': '0',
        'osu!': '0',
        'osu!standard': '0',
        'taiko': '1',
        'osu!taiko': '0',
        'ctb': '2',
        'catch the beat': '2',
        'catch': '2',
        'osu!catch': '2',
        'mania': '3',
        'osu!mania': '3'
    }

    if gamemode in gamemodes:
        gamemode = gamemodes[gamemode]
    else:
        return None

    return gamemode


async def rank_role(rank: int, role_list):
    """Calculates role based on your rank"""

    if rank < 1 or rank > 999999:
        return 'no rank role'

    x = floor(log10(rank))
    return role_list[x]


async def remove_old_roles(user, lst, do_not_remove):
    """Removes all roles in lst except do_not_remove"""

    for role in lst:
        if role in user.roles and role != do_not_remove:
            await user.remove_roles(role)


async def get_country_roles(self, guild):
    """Fetches the country roles and returns them in a list"""

    dansk = guild.get_role(self.bot.roles['dansk'])
    svensk = guild.get_role(self.bot.roles['svensk'])
    return dansk, svensk, [dansk, svensk]


async def get_rank_roles(self, guild):
    """Fetches the rank roles and returns them in a list"""

    digit_1 = guild.get_role(self.bot.roles['digit_1'])
    digit_2 = guild.get_role(self.bot.roles['digit_2'])
    digit_3 = guild.get_role(self.bot.roles['digit_3'])
    digit_4 = guild.get_role(self.bot.roles['digit_4'])
    digit_5 = guild.get_role(self.bot.roles['digit_5'])
    digit_6 = guild.get_role(self.bot.roles['digit_6'])
    return [digit_1, digit_2, digit_3, digit_4, digit_5, digit_6]


async def get_gamemode_roles(self, guild):
    """Fetches the gamemode roles and returns them in a list"""

    standard = guild.get_role(self.bot.roles['osu'])
    taiko = guild.get_role(self.bot.roles['taiko'])
    ctb = guild.get_role(self.bot.roles['ctb'])
    mania = guild.get_role(self.bot.roles['mania'])
    return standard, taiko, ctb, mania, [standard, taiko, ctb, mania]
