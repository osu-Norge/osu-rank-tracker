from __future__ import annotations

import uuid
from codecs import open
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

import aiohttp
import discord
import yaml
from expiringdict import ExpiringDict

from . import database


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
        Generates an authorization link for users to authenticate with osu!api.
        Inserts pending verification into database

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

        verficiation = database.Verification(
            discord_id=discord_user_id,
            uuid=identifier,
            expires=datetime.now(timezone.utc) + timedelta(minutes=2)
        )
        await database.VerificationTable().insert(verficiation)

        return f'https://osu.ppy.sh/oauth/authorize?client_id={cls.base_payload.get("client_id")}' + \
               f'&redirect_uri={cls.user_payload.get("redirect_uri")}' + \
               f'&state={state}&response_type=code&scope=identify'

    @staticmethod
    async def update_user_rank(
        guild: database.Guild,
        member: discord.Member,
        osu_user: dict,
        gamemode: Gamemode,
        reason: str = None
    ) -> dict:
        """
        Update a user's rank in a guild (if they're not blacklisted or from a non-whitelisted country)

        Parameters
        ----------
        guild (database.GuildTable): A fetched guild from the database
        member (discord.Member): A Discord member object
        osu_user (dict): userinfo from the osu! API
        gamemode (Gamemode): The gamemode the rank is for
        reason (str): The reason for the rank update

        Returns
        ----------
        dict: Information about the rank update. {success: bool, message: str}
        """

        # Check if the user is blacklisted
        if guild.blacklisted_osu_users and osu_user['id'] in guild.blacklisted_osu_users:
            return {'success': False, 'message': 'You are blacklisted from this guild'}

        # Check if the user is from a whitelisted country
        if guild.whitelisted_countries and osu_user['country']['code'] not in guild.whitelisted_countries:
            return {'success': False, 'message': 'You are not from a country that\'s whitelisted in this guild'}

        rank = osu_user['statistics']['global_rank']

        # Rank roles
        # This is terrible, I know :P
        if not rank:
            roles_to_add = []
        elif rank < 10:
            roles_to_add = ['role_1_digit']
        elif rank < 100:
            roles_to_add = ['role_2_digit']
        elif rank < 1000:
            roles_to_add = ['role_3_digit']
        elif rank < 10000:
            roles_to_add = ['role_4_digit']
        elif rank < 100000:
            roles_to_add = ['role_5_digit']
        elif rank < 1000000:
            roles_to_add = ['role_6_digit']
        else:
            roles_to_add = ['role_7_digit']

        # Gamemode roles
        match gamemode.id:
            case 0:
                roles_to_add.append('role_standard')
            case 1:
                roles_to_add.append('role_taiko')
            case 2:
                roles_to_add.append('role_ctb')
            case 3:
                roles_to_add.append('role_mania')

        roles_to_remove = OsuApi.__get_roles_to_remove(roles_to_add)

        # Add and remove any additional roles
        if guild.role_remove:
            roles_to_remove.append('role_remove')
        if guild.role_add:
            roles_to_add.append('role_add')

        # Convert role strings to Role objects
        roles_to_add = [member.guild.get_role(getattr(guild, r)) for r in roles_to_add if getattr(guild, r)]
        roles_to_remove = [member.guild.get_role(getattr(guild, r)) for r in roles_to_remove if getattr(guild, r)]

        await member.remove_roles(*roles_to_remove, reason=reason)
        await member.add_roles(*roles_to_add, reason=reason)
        return {'success': True, 'message': 'Your roles have been updated in accordance to your current osu! rank!'}

    @staticmethod
    def __get_roles_to_remove(roles_to_add: list[str]) -> list[str]:  # TODO: make an enum or something. idk
        """
        Returns a list of roles to remove based on the roles to add

        Parameters
        ----------
        roles_to_add (list[str]): A list of roles to add

        Returns
        ----------
        list[str]: A list of roles to remove
        """

        # This kinda fucking sucks because of its time complexity and it's hardcoded but whatever
        roles_to_remove = [
            'role_1_digit', 'role_2_digit', 'role_3_digit',
            'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit',
            'role_standard', 'role_taiko', 'role_ctb', 'role_mania'
        ]
        for add_role in roles_to_add:
            roles_to_remove.remove(add_role)

        return roles_to_remove


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
