import psycopg2
import yaml

import dataclasses
from typing import List


class Database:
    def __init__(self):
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
        """

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS public.channel (
                discord_id bigint NOT NULL PRIMARY KEY,
                clean_after_message_id bigint
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS public.guild (
                discord_id bigint NOT NULL PRIMARY KEY,
                prefix varchar(255),
                registration_channel bigint REFERENCES channel(discord_id),
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
            CREATE TABLE IF NOT EXISTS public.user (
                discord_id integer NOT NULL PRIMARY KEY,
                osu_id integer,
                gamemode smallint
            )
            """
        )

        self.connection.commit()

    async def get_version(self) -> str:
        """
        Fetches the database server version number

        Returns
        ----------
        str: The database driver name and its version number
        """

        self.cursor.execute('SELECT VERSION()')
        version = self.cursor.fetchone()[0].split(' ')[:2]
        return ' '.join(version)

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

@dataclasses.dataclass
class Guild:
    discord_id: int
    prefix: str
    registration_channel: int
    whitelisted_countries: List[str]
    blacklisted_osu_users: List[int]
    role_moderator: int
    role_remove: int
    role_add: int
    role_1_digit: int
    role_2_digit: int
    role_3_digit: int
    role_4_digit: int
    role_5_digit: int
    role_6_digit: int
    role_7_digit: int
    role_standard: int
    role_taiko: int
    role_ctb: int
    role_mania: int


class GuildTable(Database):
    def __init__(self):
        super().__init__()

    async def get(self, discord_id: int) -> Guild:
        """
        Fetches a guild and its data from the database

        Parameters
        ----------
        discord_id (int): The Discord Guild ID

        Returns
        ----------
        Guild: A guild object
        """

        try:
            self.cursor.execute('INSERT INTO guild VALUES (%s)', (discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        self.cursor.execute('SELECT * FROM guild WHERE discord_id=%s', ([discord_id]))
        db_data = self.cursor.fetchone()

        if db_data:
            return Guild(*db_data)

    async def save(self, guild: Guild) -> None:
        """
        Save a guild object in the database

        Parameters
        ----------
        guild (Guild): A guild object
        """

        try:
            self.cursor.execute('INSERT INTO guild VALUES (%s)', (guild.discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        values =  dataclasses.astuple(guild) + (guild.discord_id,)

        self.cursor.execute(
            """
            UPDATE guild SET
            discord_id = %s,
            prefix = %s,
            registration_channel = %s,
            whitelisted_countries = %s,
            blacklisted_osu_users = %s,
            role_moderator = %s,
            role_remove = %s,
            role_add = %s,
            role_1_digit = %s,
            role_2_digit = %s,
            role_3_digit = %s,
            role_4_digit = %s,
            role_5_digit = %s,
            role_6_digit = %s,
            role_7_digit = %s,
            role_standard = %s,
            role_taiko = %s,
            role_ctb = %s,
            role_mania = %s
            WHERE discord_id = %s
            """,
            values
        )
        self.connection.commit()


@dataclasses.dataclass
class User:
    discord_id: int
    osu_id: int
    gamemode: int


class UserTable(Database):
    def __init__(self):
        super().__init__()

    async def get(self, discord_id: int) -> User:
        """
        Fetches a user and its data from the database

        Parameters
        ----------
        discord_id (int): The Discord User ID

        Returns
        ----------
        User: A user object
        """

        try:
            self.cursor.execute('INSERT INTO user VALUES (%s)', (discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        self.cursor.execute('SELECT * FROM user WHERE discord_id=%s', ([discord_id]))
        db_data = self.cursor.fetchone()

        return Guild(*db_data)

    async def save(self, user: User) -> None:
        """
        Save a user object in the database

        Parameters
        ----------
        user (User): A user object
        """

        try:
            self.cursor.execute('INSERT INTO user VALUES (%s)', (user.discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        try:
            self.cursor.execute('INSERT INTO user VALUES (%s)', (id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        values =  dataclasses.astuple(user) + (user.discord_id,)

        self.cursor.execute(
            """
            UPDATE user SET
            discord_id = %s,
            osu_id = %s,
            gamemode = %s,
            WHERE discord_id = %s
            """,
            values
        )
        self.connection.commit()


@dataclasses.dataclass
class Channel:
    discord_id: int
    clean_after_message_id: int


class ChannelTable(Database):
    def __init__(self):
        super().__init__()

    async def get(self, discord_id: int) -> Channel:
        """
        Fetches a channel and its data from the database

        Parameters
        ----------
        discord_id (int): The Discord Channel ID

        Returns
        ----------
        Channel: A channel object
        """

        try:
            self.cursor.execute('INSERT INTO guild VALUES (%s)', (discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

        try:
            self.cursor.execute('INSERT INTO channel VALUES (%s)', (discord_id,))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()

    async def save(self, channel: Channel) -> None:
        """
        Save a channel object in the database

        Parameters
        ----------
        channel (Channel): A user object
        """

        values =  dataclasses.astuple(channel) + (channel.discord_id,)

        self.cursor.execute(
            """
            UPDATE channel SET
            discord_id = %s,
            clean_after_message_id = %s,
            WHERE discord_id = %s
            """,
            values
        )
        self.connection.commit()
