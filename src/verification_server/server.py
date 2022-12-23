import sys
sys.path.append('..')  # Allow to share the same database abstractions and connection

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from cogs.utils import database
from cogs.utils.osu_api import Gamemode, OsuApi

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

    gamemode = Gamemode.from_id(int(gamemode))

    # Check if user is pending verification
    verification_table = database.VerificationTable()
    verification = await verification_table.get(discord_id)

    # Verify user link
    if not verification and verification.uuid != uuid:
        return 'Invalid verification! Not a valid user or identifier!'

    # Get osu! user
    if not (osu_user := await OsuApi.get_me_user(code, gamemode)):
        return 'Something went wrong! Please try again later!'
    osu_id = osu_user['id']
    osu_name = osu_user['username']

    print(discord_id, osu_id, gamemode.id)

    # Enter user into database
    user = database.User(discord_id=discord_id, osu_id=osu_id, gamemode=gamemode.id)
    await database.UserTable().save(user)

    await verification_table.delete(discord_id)

    return RedirectResponse(f'/success/{osu_name}', status_code=303)


@app.get('/success/{name}')
async def success(name: str):
    return f'Hey {name}\nYou\'ve successfully connected your account to the bot!' + \
            'You can close this window and return to Discord!'
