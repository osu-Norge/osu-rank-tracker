import asyncio
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


async def run_on_bot_loop(request: Request, coro):
    """
    Runs a coroutine on the bot's event loop and waits for the result.
    The database pool and HTTP session belong to that loop, while this server runs on its own in a separate thread

    Parameters
    ----------
    request (Request): The request being handled
    coro (Coroutine): The coroutine to run

    Returns
    ----------
    (Any): What the coroutine returns
    """

    return await asyncio.wrap_future(asyncio.run_coroutine_threadsafe(coro, request.app.state.bot.loop))


@app.get('/')
async def index():
    """
    Show a message at the server root, which users aren't meant to visit

    Returns
    ----------
    (str): The message
    """

    return 'This is not where you\'re supposed be, dummy!'


@app.get('/callback')
async def callback(request: Request, code: str, state: str):
    """
    Handle the redirect from osu! after a user authorizes the bot, and register the user

    Parameters
    ----------
    request (Request): The incoming request
    code (str): The authorization code from osu!
    state (str): The Discord ID, gamemode ID and verification UUID, separated by colons

    Returns
    ----------
    (TemplateResponse | RedirectResponse): An error page, or a redirect to the success page
    """

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
    verification = await run_on_bot_loop(request, verification_table.get(int(discord_id)))

    # Verify user link
    if not verification or verification.uuid != uuid:
        return templates.TemplateResponse(
            request=request,
            name='error.html',
            context={'message': 'Not a valid user or identifier'}
        )

    # Get osu! user
    if not (osu_user := await run_on_bot_loop(request, OsuApi.get_me_user(code, gamemode))):
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
    await run_on_bot_loop(request, database.UserTable().save(user))

    await run_on_bot_loop(request, verification_table.delete(int(discord_id)))

    bot = request.app.state.bot
    bot.loop.call_soon_threadsafe(bot.dispatch, 'user_registered', user.discord_id)

    return RedirectResponse(f'/success/{osu_name}', status_code=303)


@app.get('/success/{name}')
async def success(request: Request, name: str):
    """
    Show the page confirming that a user's osu! account is connected

    Parameters
    ----------
    request (Request): The incoming request
    name (str): The osu! username to show

    Returns
    ----------
    (TemplateResponse): The success page
    """

    return templates.TemplateResponse(request=request, name='success.html', context={'name': name})
