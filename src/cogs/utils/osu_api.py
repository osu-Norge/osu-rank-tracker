import aiohttp
from expiringdict import ExpiringDict

from codecs import open
import yaml

from cogs.utils import osu_utils


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
    async def get_user(cls, user: str, gamemode: str):
        """
        Fetch user info from the v2 API
        """

        gamemode_id = await osu_utils.get_gamemode_id(gamemode)
        gamemode = await osu_utils.get_gamemode_url(gamemode_id)

        token = cls.cache.get('token')
        if not token:
            await cls.renew_token()
            token = cls.cache.get('token')

        async with aiohttp.ClientSession() as session:
            header = {'Authorization': f'Bearer {token}'}
            async with session.get(f'https://osu.ppy.sh/api/v2/users/{user}/{gamemode}', headers=header) as r:
                if r.status == 200:
                    data = await r.json()
                    return data
