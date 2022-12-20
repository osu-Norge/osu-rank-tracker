from __future__ import annotations
from codecs import open
import dataclasses
from enum import Enum

import aiohttp
from expiringdict import ExpiringDict
import yaml



class OsuApi:
    cache = ExpiringDict(max_len=1, max_age_seconds=86400)

    with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
        credntials = yaml.load(f, Loader=yaml.SafeLoader).get('api', {}).get('osu_v2', {})

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
        'redirect_uri': credntials.get('redirect_uri')
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
    async def get_user(cls, user: str, gamemode_name: str):
        """
        Fetch user info from the v2 API
        """

        gamemode = await Gamemode.from_name(gamemode_name)

        token = cls.cache.get('token')
        if not token:
            await cls.renew_token()
            token = cls.cache.get('token')

        async with aiohttp.ClientSession() as session:
            header = {'Authorization': f'Bearer {token}'}
            async with session.get(f'https://osu.ppy.sh/api/v2/users/{user}/{gamemode.url_name}', headers=header) as r:
                if r.status == 200:
                    data = await r.json()
                    return data


@dataclasses.dataclass
class Gamemode:
    id: int
    name: str
    url_name: str

    @classmethod
    async def from_id(cls, id: int) -> Gamemode:
        """
        Creates an instance of its class based on id

        Parameters
        -----------
        id (int): The gamemode id

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        name = await cls.id_to_name(id)
        url_name = await cls.id_to_url_name(id)
        return cls(id, name, url_name)

    @classmethod
    async def from_name(cls, name: str) -> Gamemode:
        """
        Creates an instance of its class based on name

        Parameters
        -----------
        name (str): The gamemode name

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        id = await cls.name_to_id(name)
        name = await cls.id_to_name(id)  # Ensure name is correct
        url_name = await cls.id_to_url_name(id)
        return cls(id, name, url_name)

    @classmethod
    async def from_url_name(cls, url_name: str) -> Gamemode:
        """
        Creates an instance of its class based on URL name

        Parameters
        -----------
        url_name (str): The gamemode URL name

        Returns
        -----------
        Gamemode: A Gamemode object
        """

        id = await Gamemode.url_name_to_id(url_name)
        name = await Gamemode.id_to_name(id)
        url_name = await Gamemode.id_to_url_name(id)  # Ensure name is correct
        return cls(id, name, url_name)

    @staticmethod
    async def id_to_name(id: int) -> str:
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
    async def id_to_url_name(id: int) -> str:
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
    async def url_name_to_id(url_name: str) -> int:
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
    async def name_to_id(name: str) -> int:
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
