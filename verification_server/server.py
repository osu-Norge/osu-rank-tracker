from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from ..src.cogs.utils import database
from ..src.cogs.utils.osu_api import Gamemode, OsuApi

app = FastAPI()


@app.get('/')
async def index():
    return 'This is not where you\'re supposed be, dummy!'


@app.get('/callback')
async def callback(code: str, state: str):

    try:
        discord_id, gamemode, uuid = state.split(':')
    except ValueError:
        return 'Invalid request!'

    verification_table = database.VerificationTable()
    verification = await verification_table.get(discord_id)

    if not verification:
        return 'Invalid request!'

    if verification.token != uuid:
        return 'Invalid request!'

    gamemode = Gamemode.from_id(gamemode)

    osu_user = await OsuApi.get_me_user(code, gamemode.url_name)
    if not osu_user:
        return 'Something went wrong! Please try again later'

    osu_id = osu_user['id']
    osu_name = osu_user['username']

    user = database.User(discord_id=discord_id, osu_id=osu_id, gamemode=gamemode)
    await database.UserTable().insert(user)

    await verification_table.delete(discord_id)

    return RedirectResponse(f'/success/{osu_name}', status_code=303)


@app.get('/success/{name}')
async def success(name: str):
    return f'Successfully verified {name}!'
