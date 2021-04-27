import psycopg2
import yaml

from cogs.utils.osu_utils import get_gamemode_id


class Database:
    def __init__(self) -> None:
        with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
            self.db = yaml.load(f, Loader=yaml.SafeLoader).get('database', {})

        connection = psycopg2.connect(
            host=self.db['host'],
            dbname=self.db['dbname'],
            user=self.db['username'],
            password=self.db['password']
        )
        self.cursor = connection.cursor()


class Guild(Database):
    def __init__(self, id: int) -> None:
        super().__init__()
        self.id = id

    async def get_all(self) -> tuple:
        """
        Fetches all the info about a guild in the database

        Returns
        -----------
        tuple: Database row
        """

        self.cursor.execute('SELECT * FROM guild WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    @property
    async def prefix(self) -> str:
        """
        Fetches the guild's prefix

        Returns
        -----------
        str: The guild's prefix
        """

        self.cursor.execute('SELECT prefix FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    @property
    async def locale(self) -> str:
        """
        Fetches the guild's locale

        Returns
        -----------
        str: The guild's locale
        """

        self.cursor.execute('SELECT locale FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def is_oauth(self) -> bool:
        """
        Checks whether or not oAuth is enabled

        Returns
        -----------
        bool
        """

        self.cursor.execute('SELECT oauth FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def is_country_whitelisted(self, country_code: str) -> bool:
        """
        Checks whether or not a specified country code is in the list of whitelisted countries

        Parameters
        ----------
        country_code (str): ISO 3166-1 Alpha-2 country code

        Returns
        -----------
        bool
        """

        self.cursor.execute('SELECT whitelisted_countries FROM guild WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response and country_code in response:
            return True


class User(Database):
    def __init__(self) -> None:
        super().__init__()
        self.id = id

    async def get_all(self) -> tuple:
        """
        Fetches all the info about a user in the database

        Returns
        -----------
        tuple: Database row
        """

        self.cursor.execute('SELECT * FROM user WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    @property
    async def osu_id(self) -> int:
        """
        Fetches the user's osu user id

        Returns
        -----------
        int: The user's registered osu id
        """

        self.cursor.execute('SELECT osu_id FROM channel WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    @property
    async def gamemode(self) -> int:
        """
        Fetches the user's set osu gamemode id

        Returns
        -----------
        int: The user's set gamemode
        """

        self.cursor.execute('SELECT gamemode FROM channel WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    @property
    async def gamemode_name(self) -> str:
        """
        Fetches the user's set osu gamemode and converts the id to a readable name

        Returns
        -----------
        str: The user's set gamemode name
        """

        gamemode_id = await self.gamemode
        return get_gamemode_id(gamemode_id)


class Channel(Database):
    def __init__(self) -> None:
        super().__init__()
        self.id = id

    async def get_all(self) -> tuple:
        """
        Fetches all the info about a channel in the database

        Returns
        -----------
        tuple: Database row
        """

        self.cursor.execute('SELECT * FROM channel WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    @property
    async def clean_after_message_id(self) -> int:
        """
        Fetches the message id that the bot will remove all messages after in the specified channel

        Returns
        -----------
        int: The Discord message id that the bot will delete all messages after in the channel
        """

        self.cursor.execute('SELECT clean_after_message_id FROM channel WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]
