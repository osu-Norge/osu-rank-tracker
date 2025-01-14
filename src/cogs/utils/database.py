from abc import abstractmethod
from dataclasses import astuple, dataclass
from datetime import datetime

import psycopg2
import yaml


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
            CREATE TABLE IF NOT EXISTS public.guild (
                discord_id bigint NOT NULL PRIMARY KEY,
                whitelisted_countries char(2)[],
                blacklisted_osu_users integer[],
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
                discord_id bigint NOT NULL PRIMARY KEY,
                osu_id integer NOT NULL,
                gamemode smallint NOT NULL
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS public.verification (
                discord_id bigint NOT NULL PRIMARY KEY,
                uuid TEXT NOT NULL,
                expires TIMESTAMP
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


class Table(Database):
    def __init__(self, table_name: str, dataclass: dataclass, create_row_on_none: bool = False):
        super().__init__()
        self.table_name = table_name
        self.dataclass = dataclass
        self.create_row_on_none = create_row_on_none

    async def get(self, discord_id: int) -> dataclass:
        """
        Fetches a row from the database

        Parameters
        ----------
        discord_id (int): The Discord ID

        Returns
        ----------
        dataclass: A dataclass object
        """

        self.cursor.execute(f'SELECT * FROM public.{self.table_name} WHERE discord_id = %s', (discord_id,))
        db_data = self.cursor.fetchone()

        if not db_data:
            if not self.create_row_on_none:
                return None

            self.cursor.execute(f'INSERT INTO public.{self.table_name} VALUES (%s)', (discord_id,))
            self.connection.commit()

            self.cursor.execute(f'SELECT * FROM public.{self.table_name} WHERE discord_id = %s', (discord_id,))
            db_data = self.cursor.fetchone()

        return self.dataclass(*db_data)

    async def get_all(self) -> tuple[dataclass]:
        """
        Fetches all the rows from the database

        Returns
        ----------
        tuple[dataclass]: A tuple of dataclass objects
        """

        self.cursor.execute(f'SELECT * FROM public.{self.table_name}')
        db_data = self.cursor.fetchall()

        return tuple(self.dataclass(*data) for data in db_data)

    async def count(self) -> int:
        """
        Counts the number of rows in the database
        Returns
        ----------
        int: The number of rows in the database
        """

        self.cursor.execute(f'SELECT COUNT(*) FROM public.{self.table_name}')
        return self.cursor.fetchone()[0]

    @abstractmethod
    async def save(self, data: dataclass) -> None:
        """
        Saves a row to the database

        Parameters
        ----------
        data (dataclass): A dataclass object
        Raises
        ----------
        NotImplementedError: If the child class does not implement this method
        """

        # Leave implementation to the child class
        raise NotImplementedError()

    async def delete(self, discord_id: int) -> None:
        """
        Deletes a row from the database

        Parameters
        ----------
        discord_id (int): The Discord ID
        """

        self.cursor.execute(f'DELETE FROM public.{self.table_name} WHERE discord_id = %s', (discord_id,))
        self.connection.commit()


@dataclass
class Guild:
    discord_id: int
    whitelisted_countries: list[str] | None
    blacklisted_osu_users: list[int] | None
    role_remove: int | None
    role_add: int | None
    role_1_digit: int | None
    role_2_digit: int | None
    role_3_digit: int | None
    role_4_digit: int | None
    role_5_digit: int | None
    role_6_digit: int | None
    role_7_digit: int | None
    role_standard: int | None
    role_taiko: int | None
    role_ctb: int | None
    role_mania: int | None


class GuildTable(Table):
    def __init__(self):
        super().__init__(table_name='guild', dataclass=Guild, create_row_on_none=True)

    async def save(self, guild: Guild) -> None:
        """
        Save a guild object in the database

        Parameters
        ----------
        guild (Guild): A guild object
        """

        values = astuple(guild)

        try:
            self.cursor.execute(
                f"""
                INSERT INTO {self.table_name}
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, values)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
        else:
            return

        values = values + (guild.discord_id,)

        self.cursor.execute(
            f"""
            UPDATE {self.table_name} SET
            discord_id = %s,
            whitelisted_countries = %s,
            blacklisted_osu_users = %s,
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
            """, values
        )
        self.connection.commit()


@dataclass
class User:
    discord_id: int
    osu_id: int
    gamemode: int


class UserTable(Table):
    def __init__(self):
        super().__init__(table_name='user', dataclass=User, create_row_on_none=False)

    async def save(self, user: User) -> None:
        """
        Save a user object in the database

        Parameters
        ----------
        user (User): A user object
        """

        values = astuple(user)

        try:
            self.cursor.execute(f'INSERT INTO public.{self.table_name} VALUES (%s, %s, %s)', values)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
        else:
            return

        values = astuple(user) + (user.discord_id,)

        self.cursor.execute(
            f"""
            UPDATE public.{self.table_name} SET
            discord_id = %s,
            osu_id = %s,
            gamemode = %s
            WHERE discord_id = %s
            """, values
        )
        self.connection.commit()


@dataclass
class Verification:
    discord_id: int
    uuid: str
    expires: datetime


class VerificationTable(Table):
    def __init__(self):
        super().__init__(table_name='verification', dataclass=Verification, create_row_on_none=False)

    async def insert(self, verification: Verification) -> bool:
        """
        Insert a new pending verification into the database

        Parameters
        ----------
        verification (Verification): A verification object

        Returns
        ----------
        bool: True if the verification was inserted, False if it already exists
        """

        values = astuple(verification)

        try:
            self.cursor.execute(f'INSERT INTO {self.table_name} VALUES (%s, %s, %s)', values)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

        return True
