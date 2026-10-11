import sys

sys.path.append('..')  # Allow to share the same database abstractions and connection

from fastapi import FastAPI, Request  # noqa E402
from fastapi.responses import RedirectResponse  # noqa E402
from fastapi.staticfiles import StaticFiles  # noqa E402
from fastapi.templating import Jinja2Templates  # noqa E402

from cogs.utils import database  # noqa E402
from cogs.utils.osu_api import Gamemode, OsuApi  # noqa E402
from logger import verification_logger  # noqa E402

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
        return templates.TemplateResponse(
            request=request,
            name='error.html',
            context={'message': 'Invalid request! Missing identifying data!'}
        )

    gamemode = Gamemode.from_id(int(gamemode))

    # Check if user is pending verification
    verification_table = database.VerificationTable()
    verification = await verification_table.get(int(discord_id))

    # Verify user link
    if not verification or verification.uuid != uuid:
        return templates.TemplateResponse(
            request=request,
            name='error.html',
            context={'message': 'Not a valid user or identifier'}
        )

    # Get osu! user
    if not (osu_user := await OsuApi.get_me_user(code, gamemode)):
        return templates.TemplateResponse(
            request=request,
            name='error.html',
            context={'message': 'Failed to fetch osu! user! Try again later.'}
        )

    osu_id = osu_user['id']
    osu_name = osu_user['username']

    verification_logger.info(f'User verified: {discord_id=}, {osu_id=}, {gamemode.id=}')

    # Enter user into database
    user = database.User(discord_id=int(discord_id), osu_id=osu_id, gamemode=gamemode.id)
    await database.UserTable().save(user)

    await verification_table.delete(discord_id)

    bot = request.app.state.bot
    bot.loop.call_soon_threadsafe(bot.dispatch, 'user_registered', user.discord_id)

    return RedirectResponse(f'/success/{osu_name}', status_code=303)


@app.get('/success/{name}')
async def success(request: Request, name: str):
    return templates.TemplateResponse(request=request, name='success.html', context={'name': name})
