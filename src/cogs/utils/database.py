import psycopg2
import yaml

from cogs.utils.osu_utils import get_gamemode_id

from typing import List


class Database:
    def __init__(self) -> None:
        with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
            self.db = yaml.load(f, Loader=yaml.SafeLoader).get('database', {})

        self.connection = psycopg2.connect(
            host=self.db['host'],
            dbname=self.db['dbname'],
            user=self.db['username'],
            password=self.db['password']
        )
        self.cursor = self.connection.cursor()


    def init_db(self) -> None:
        """
        Creates all the necessary tables in order for the bot to function

        Returns
        ----------
        None
        """

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS channels (
                discord_id bigint NOT NULL PRIMARY KEY,
                clean_after_message_id bigint
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS guilds (
                discord_id bigint NOT NULL PRIMARY KEY,
                prefix varchar(255),
                locale char(5),
                registration_channel bigint REFERENCES channels(discord_id),
                oauth boolean,
                whitelisted_countries char(2)[],
                blacklisted_osu_users integer[],
                role_moderator bigint,
                role_remove bigint,
                role_add bigint,
                role_1_digit bigint,
                role_2_digit bigint,
                role_3_digit bigint,
                role_4_digit bigint,
                role_5_digit bigint,
                role_6_digit bigint,
                role_7_digit bigint,
                role_standard bigint,
                role_taiko bigint,
                role_ctb bigint,
                role_mania bigint
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                discord_id integer NOT NULL PRIMARY KEY,
                osu_id integer,
                gamemode smallint
            )
            """
        )

        self.connection.commit()

    async def get_guilds(self) -> List[tuple]:
        """
        Fetches all the entries in the guild table

        Returns
        -----------
        List[tuple]: Table rows
        """

        self.cursor.execute('SELECT * FROM guilds')
        return self.cursor.fetchall()

    async def get_users(self) -> List[tuple]:
        """
        Fetches all the entries in the users table

        Returns
        -----------
        List[tuple]: Table rows
        """

        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    async def get_channels(self) -> List[tuple]:
        """
        Fetches all the entries in the channels table

        Returns
        -----------
        List[tuple]: Table rows
        """

        self.cursor.execute('SELECT * FROM channels')
        return self.cursor.fetchall()


class Guild(Database):
    def __init__(self, id: int) -> None:
        super().__init__()
        self.id = id

        try:
            self.cursor.execute('INSERT INTO guilds VALUES (%s)', (id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()


    async def get_all(self) -> tuple:
        """
        Fetches all the info about a guild in the database

        Returns
        -----------
        tuple: Database row
        """

        self.cursor.execute('SELECT * FROM guilds WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    async def get_prefix(self) -> str:
        """
        Fetches the guild's prefix

        Returns
        -----------
        str: The guild's prefix
        """

        self.cursor.execute('SELECT prefix FROM guilds WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def set_prefix(self, prefix: str) -> None:
        """
        Sets the guild prefix

        Parameters
        ----------
        prefix (str): The desired prefix

        Returns
        -----------
        None
        """

        self.cursor.execute('UPDATE guilds SET prefix=(%s) WHERE discord_id=%s', (prefix, self.id))
        self.connection.commit()

    async def get_locale(self) -> str:
        """
        Fetches the guild's locale

        Returns
        -----------
        str: The guild's locale
        """

        self.cursor.execute('SELECT locale FROM guilds WHERE discord_id=%s', ([self.id]))
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

        self.cursor.execute('SELECT oauth FROM guilds WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def get_whitelist(self) -> tuple:
        """
        Fetches the list of whitelisted countries

        Returns
        -----------
        tuple: The whitelisted countries
        """

        self.cursor.execute('SELECT whitelisted_countries FROM guilds WHERE discord_id=%s', ([self.id]))
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

        self.cursor.execute('SELECT whitelisted_countries FROM guilds WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response and country_code in response:
            return True

    async def whitelist_add(self, country_code: str) -> None:
        """
        Adds a country to the whitelist

        Parameters
        ----------
        country_code (str): ISO 3166-1 Alpha-2 country code

        Returns
        -----------
        None
        """

        self.cursor.execute(
            """
            UPDATE guilds
            SET whitelisted_countries=array_append(whitelisted_countries, %s) 
            WHERE discord_id=%s
            """,
            (country_code, self.id)
        )
        self.connection.commit()

    async def whitelist_remove(self, country_code: str) -> None:
        """
        Removes a country from the whitelist

        Parameters
        ----------
        country_code (str): ISO 3166-1 Alpha-2 country code

        Returns
        -----------
        None
        """

        self.cursor.execute(
            """
            UPDATE guild
            SET whitelisted_countries=array_remove(whitelisted_countries, %s) 
            WHERE discord_id=%s
            """, 
            (country_code, self.id)
        )
        self.connection.commit()


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

        self.cursor.execute('SELECT * FROM users WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    async def get_osu_id(self) -> int:
        """
        Fetches the user's osu user id

        Returns
        -----------
        int: The user's registered osu id
        """

        self.cursor.execute('SELECT osu_id FROM users WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def get_gamemode(self) -> int:
        """
        Fetches the user's set osu gamemode id

        Returns
        -----------
        int: The user's set gamemode
        """

        self.cursor.execute('SELECT gamemode FROM users WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]

    async def get_gamemode_name(self) -> str:
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

        self.cursor.execute('SELECT * FROM channels WHERE discord_id=%s', ([self.id]))
        return self.cursor.fetchone()

    async def get_clean_after_message_id(self) -> int:
        """
        Fetches the message id that the bot will remove all messages after in the specified channel

        Returns
        -----------
        int: The Discord message id that the bot will delete all messages after in the channel
        """

        self.cursor.execute('SELECT clean_after_message_id FROM channels WHERE discord_id=%s', ([self.id]))
        response = self.cursor.fetchone()
        if response:
            return response[0]
