from __future__ import annotations
from codecs import open
from dataclasses import dataclass
from enum import Enum
import uuid

import aiohttp
import discord
from expiringdict import ExpiringDict
import yaml

from . import database
from cogs.utils import embed_templates


class OsuApi:
    cache = ExpiringDict(max_len=1, max_age_seconds=86400)

    with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
        credntials = yaml.load(f, Loader=yaml.SafeLoader).get('api', {}).get('osu', {})

    base_payload = {
        'client_id': credntials.get('client_id'),
        'client_secret': credntials.get('client_secret')
    }

    token_payload = base_payload.copy()
    token_payload.update({
        'grant_type': 'client_credentials',
        'scope': 'public'
    })

    user_payload = base_payload.copy()
    user_payload.update({
        'grant_type': 'authorization_code',
        'redirect_uri': credntials.get('redirect_uri'),
        'scope': 'identify'
    })

    @classmethod
    async def renew_token(cls) -> None:
        """
        Requests a new Authorization Code from the osu!api v2
        """

        print('Fetching new token...')

        async with aiohttp.ClientSession() as session:
            async with session.post('https://osu.ppy.sh/oauth/token', json=cls.token_payload) as r:
                if r.status == 200:
                    data = await r.json()

                    cls.cache.update({
                        'token': data.get('access_token')
                    })
                else:
                    raise aiohttp.HTTPException(response=r.status, message=r.reason)

    @classmethod
    async def get_user(cls, user: str, gamemode: Gamemode) -> dict | None:
        """
        Fetch osu! user info from the v2 API

        Parameters
        ----------
        user (str): The osu username or user id
        gamemode (Gamemode): Specified gamemode for statistics

        Returns
        ----------
        dict: The user data. None if user not found
        """

        # Get cached API token. Renew token if expired
        token = cls.cache.get('token')
        if not token:
            await cls.renew_token()
            token = cls.cache.get('token')

        # Get user data
        async with aiohttp.ClientSession() as session:
            header = {'Authorization': f'Bearer {token}'}
            async with session.get(f'https://osu.ppy.sh/api/v2/users/{user}/{gamemode.url_name}', headers=header) as r:
                if r.status == 200:
                    data = await r.json()
                    return data

    @classmethod
    async def get_me_user(cls, code: str, gamemode: Gamemode) -> dict:
        """
        Fetch an authenticated osu! user's info from the v2 API

        Parameters
        ----------
        code (str): The authorization code return from oAuth callback
        gamemode (Gamemode): Specified gamemode for statistics

        Returns
        ----------
        dict: The user data
        """

        # Use code to get token
        async with aiohttp.ClientSession() as session:
            payload = cls.user_payload.copy()
            payload.update({
                'code': code
            })

            async with session.post('https://osu.ppy.sh/oauth/token', json=payload) as r:
                if r.status == 200:
                    data = await r.json()
                    token = data.get('access_token')
                else:
                    raise aiohttp.ClientResponseError(r.request_info, r.history)         

            # Get user data
            header = {'Authorization': f'Bearer {token}'}
            async with session.get(f'https://osu.ppy.sh/api/v2/me/{gamemode.url_name}', headers=header) as r:
                if r.status == 200:
                    data = await r.json()
                    return data
                raise aiohttp.ClientResponseError(r.request_info, r.history)

    @classmethod
    async def generate_auth_link(cls, discord_user_id: int, gamemode: Gamemode) -> str:
        """
        Generates an authorization link for users to authenticate with osu!api. Inserts pending verification into database

        Parameters
        -----------
        discord_user_id (int): The discord user id
        gamemode (Gamemode): The gamemode to set tracking for

        Returns
        -----------
        str: The authorization link
        """

        identifier = str(uuid.uuid1())
        state = f'{discord_user_id}:{gamemode.id}:{identifier}'

        verficiation = database.Verification(discord_id=discord_user_id, uuid=identifier)
        await database.VerificationTable().insert(verficiation)

        return f'https://osu.ppy.sh/oauth/authorize?client_id={cls.base_payload.get("client_id")}' + \
               f'&redirect_uri={cls.user_payload.get("redirect_uri")}' + \
               f'&state={state}&response_type=code&scope=identify'

    @staticmethod
    async def update_user_rank(guild: database.Guild, member: discord.Member, osu_user: dict, gamemode: Gamemode, reason: str = None):
        """
        Update a user's rank in a guild (if they're not blacklisted or from a non-whitelisted country)

        Parameters
        ----------
        guild (database.GuildTable): A fetched guild from the database
        member (discord.Member): A Discord member object
        osu_user (dict): userinfo from the osu! API
        gamemode (Gamemode): The gamemode the rank is for
        reason (str): The reason for the rank update
        """

        # Check if the user is blacklisted
        if guild.blacklisted_osu_users and osu_user['id'] in guild.blacklisted_osu_users:
            return

        # Check if the user is from a whitelisted country
        if guild.whitelisted_countries and osu_user['country']['code'] not in guild.whitelisted_countries:
            return

        rank = osu_user['statistics']['global_rank']

        # Rank roles
        # This is terrible, I know :P
        if rank < 10:
            roles_to_add = set(['role_1_digit'])
            roles_to_remove = set(['role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 100:
            roles_to_add = set(['role_2_digit'])
            roles_to_remove = set(['role_1_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 1000:
            roles_to_add = set(['role_3_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 10000:
            roles_to_add = set(['role_4_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 100000:
            roles_to_add = set(['role_5_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 1000000:
            roles_to_add = set(['role_6_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_7_digit'])
        else:
            roles_to_add = set(['role_7_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit'])

        # Gamemode roles
        match gamemode.id:
            case 0:
                roles_to_add.add('role_standard')
                roles_to_remove.update(['role_taiko', 'role_ctb', 'role_mania'])
            case 1:
                roles_to_add.add('role_taiko')
                roles_to_remove.update(['role_standard', 'role_ctb', 'role_mania'])
            case 2:
                roles_to_add.add('role_ctb')
                roles_to_remove.update(['role_standard', 'role_taiko', 'role_mania'])
            case 3:
                roles_to_add.add('role_mania')
                roles_to_remove.update(['role_standard', 'role_taiko', 'role_ctb'])


        # Add and remove any additional roles
        if guild.role_remove:
            roles_to_remove.add(str(guild.role_remove))
        if guild.role_add:
            roles_to_add.add(str(guild.role_add))

        # Convert role strings to Role objects
        roles_to_add = [member.guild.get_role(getattr(guild, attr)) for attr in roles_to_add if getattr(guild, attr)]
        roles_to_remove = [member.guild.get_role(getattr(guild, attr)) for attr in roles_to_remove if getattr(guild, attr)]

        await member.remove_roles(*roles_to_remove, reason=reason)
        await member.add_roles(*roles_to_add, reason=reason)

        await embed_templates.success('Your roles have been updated!')


@dataclass
class Gamemode:
    id: int
    name: str
    url_name: str

    @classmethod
    def from_id(cls, id: int) -> Gamemode:
        """
        Creates an instance of its class based on id

        Parameters
        -----------
        id (int): The gamemode id

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        name = cls.id_to_name(id)
        url_name = cls.id_to_url_name(id)
        return cls(id, name, url_name)

    @classmethod
    def from_name(cls, name: str) -> Gamemode:
        """
        Creates an instance of its class based on name

        Parameters
        -----------
        name (str): The gamemode name

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        id = cls.name_to_id(name)
        name = cls.id_to_name(id)  # Ensure name is correct
        url_name = cls.id_to_url_name(id)
        return cls(id, name, url_name)

    @classmethod
    def from_url_name(cls, url_name: str) -> Gamemode:
        """
        Creates an instance of its class based on URL name

        Parameters
        -----------
        url_name (str): The gamemode URL name

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        id = Gamemode.url_name_to_id(url_name)
        name = Gamemode.id_to_name(id)
        url_name = Gamemode.id_to_url_name(id)  # Ensure name is correct
        return cls(id, name, url_name)

    @staticmethod
    def id_to_name(id: int) -> str:
        """
        Converts a gamemode id to its display name

        Parameters
        -----------
        id (int): The gamemode id

        Returns
        -----------
        str: The gamemode display name
        """

        gamemode_names = {
            0: 'Standard',
            1: 'Taiko',
            2: 'Catch The Beat',
            3: 'Mania'
        }
        return gamemode_names.get(id)

    @staticmethod
    def id_to_url_name(id: int) -> str:
        """
        Converts a gamemode id to its name used in URLs

        Parameters
        -----------
        id (int): The gamemode id

        Returns
        -----------
        str: The gamemode URL name
        """

        gamemode_urls = {
            0: 'osu',
            1: 'taiko',
            2: 'fruits',
            3: 'mania'
        }
        return gamemode_urls.get(id)

    @staticmethod
    def url_name_to_id(url_name: str) -> int:
        """
        Converts a gamemode URL name to its id

        Parameters
        -----------
        url_name (str): The gamemode URL name

        Returns
        -----------
        int: The gamemode id
        """

        # This is a reversal of the method above.
        # The method above is sufficent and this is redundant
        # But improves ease of use of the class and prevents confusion.
        gamemode_ids = {
            'osu': 0,
            'taiko': 1,
            'fruits': 2,
            'mania': 3
        }
        return gamemode_ids.get(url_name.lower())

    @staticmethod
    def name_to_id(name: str) -> int:
        """
        Converts a gamemode display name to its id

        Parameters
        -----------
        name (str): The gamemode name

        Returns
        -----------
        int: The gamemode id
        """

        gamemode_ids = {
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
        return gamemode_ids.get(name.lower())


# class GamemodeOptions(Enum):
#     STANDARD = Gamemode.from_id(0)
#     TAIKO = Gamemode.from_id(1)
#     CATCH_THE_BEAT = Gamemode.from_id(2)
#     MANIA = Gamemode.from_id(3)
class GamemodeOptions(Enum):
    standard = 0
    taiko = 1
    ctb = 2
    mania = 3
