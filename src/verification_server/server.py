import sys
sys.path.append('..')  # Allow to share the same database abstractions and connection

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cogs.utils import database
from cogs.utils.osu_api import Gamemode, OsuApi

app = FastAPI()

# HTML templates to serve prettier feedback to the user
app.mount('/static', StaticFiles(directory='src/verification_server/static'), name='static')
templates = Jinja2Templates(directory='src/verification_server/templates')


@app.get('/')
async def index():
    return 'This is not where you\'re supposed be, dummy!'


@app.get('/callback')
async def callback(request: Request, code: str, state: str):

    try:
        discord_id, gamemode, uuid = state.split(':')
    except ValueError:
        return templates.TemplateResponse('error.html', {'request': request, 'message': 'Invalid request! Missing identifying data!'})

    gamemode = Gamemode.from_id(int(gamemode))

    # Check if user is pending verification
    verification_table = database.VerificationTable()
    verification = await verification_table.get(discord_id)

    # Verify user link
    if not verification and verification.uuid != uuid:
        return templates.TemplateResponse('error.html', {'request': request, 'message': 'Not a valid user or identifier'})

    # Get osu! user
    if not (osu_user := await OsuApi.get_me_user(code, gamemode)):
        return templates.TemplateResponse('error.html', {'request': request, 'message': 'Failed to fetch osu! user! Try again later.'})
    osu_id = osu_user['id']
    osu_name = osu_user['username']

    print(discord_id, osu_id, gamemode.id)

    # Enter user into database
    user = database.User(discord_id=discord_id, osu_id=osu_id, gamemode=gamemode.id)
    await database.UserTable().save(user)

    await OsuApi.update_newly_created_user_rank(discord_id, gamemode, osu_user)

    await verification_table.delete(discord_id)

    return RedirectResponse(f'/success/{osu_name}', status_code=303)


@app.get('/success/{name}')
async def success(request: Request, name: str):
    return templates.TemplateResponse('success.html', {'request': request, 'name': name})
