from dataclasses import astuple, dataclass, fields
from datetime import datetime

from psycopg_pool import AsyncConnectionPool


class Database:
    pool: AsyncConnectionPool | None = None  # Shared by every table, opened by the bot at startup

    @classmethod
    async def open(cls, config: dict) -> None:
        """
        Opens the connection pool. Must be called before any queries are run

        Parameters
        ----------
        config (dict): The database section of the config
        """

        cls.pool = AsyncConnectionPool(
            kwargs={
                'host': config['host'],
                'dbname': config['dbname'],
                'user': config['username'],
                'password': config['password'],
                'autocommit': True,
            },
            check=AsyncConnectionPool.check_connection,
            open=False,
        )
        await cls.pool.open(wait=True, timeout=30)

    @classmethod
    async def close(cls) -> None:
        """
        Closes the connection pool
        """

        if cls.pool:
            await cls.pool.close()

    async def execute(self, query: str, params: tuple = ()) -> int:
        """
        Runs a query

        Parameters
        ----------
        query (str): The SQL query
        params (tuple): The query parameters

        Returns
        ----------
        (int) The number of rows affected
        """

        async with self.pool.connection() as connection:
            cursor = await connection.execute(query, params)
            return cursor.rowcount

    async def fetchone(self, query: str, params: tuple = ()) -> tuple | None:
        """
        Runs a query and returns the first row

        Parameters
        ----------
        query (str): The SQL query
        params (tuple): The query parameters

        Returns
        ----------
        (tuple | None) The first row, or None if there are no rows
        """

        async with self.pool.connection() as connection:
            cursor = await connection.execute(query, params)
            return await cursor.fetchone()

    async def fetchall(self, query: str, params: tuple = ()) -> list[tuple]:
        """
        Runs a query and returns all rows

        Parameters
        ----------
        query (str): The SQL query
        params (tuple): The query parameters

        Returns
        ----------
        (list[tuple]) The rows
        """

        async with self.pool.connection() as connection:
            cursor = await connection.execute(query, params)
            return await cursor.fetchall()

    async def init_db(self) -> None:
        """
        Creates all the necessary tables in order for the bot to function
        """

        await self.execute(
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
        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS public.user (
                discord_id bigint NOT NULL PRIMARY KEY,
                osu_id integer NOT NULL,
                gamemode smallint NOT NULL
            )
            """
        )
        await self.execute(
            """
            CREATE TABLE IF NOT EXISTS public.verification (
                discord_id bigint NOT NULL PRIMARY KEY,
                uuid TEXT NOT NULL,
                expires TIMESTAMP
            )
            """
        )

    async def get_version(self) -> str:
        """
        Fetches the database server version number

        Returns
        ----------
        str: The database driver name and its version number
        """

        version = (await self.fetchone('SELECT VERSION()'))[0].split(' ')[:2]
        return ' '.join(version)


class Table(Database):
    def __init__(self, table_name: str, dataclass: dataclass, create_row_on_none: bool = False):
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

        db_data = await self.fetchone(f'SELECT * FROM public.{self.table_name} WHERE discord_id = %s', (discord_id,))

        if not db_data:
            if not self.create_row_on_none:
                return None

            # The no-op update makes RETURNING give the row even if it was created in the meantime
            db_data = await self.fetchone(
                f"""
                INSERT INTO public.{self.table_name} (discord_id) VALUES (%s)
                ON CONFLICT (discord_id) DO UPDATE SET discord_id = EXCLUDED.discord_id
                RETURNING *
                """, (discord_id,)
            )

        return self.dataclass(*db_data)

    async def get_all(self) -> tuple[dataclass]:
        """
        Fetches all the rows from the database

        Returns
        ----------
        tuple[dataclass]: A tuple of dataclass objects
        """

        db_data = await self.fetchall(f'SELECT * FROM public.{self.table_name}')
        return tuple(self.dataclass(*data) for data in db_data)

    async def count(self) -> int:
        """
        Counts the number of rows in the database
        Returns
        ----------
        int: The number of rows in the database
        """

        return (await self.fetchone(f'SELECT COUNT(*) FROM public.{self.table_name}'))[0]

    async def save(self, data: dataclass) -> None:
        """
        Saves a row to the database, replacing the existing row with the same Discord ID

        Parameters
        ----------
        data (dataclass): A dataclass object
        """

        columns = [field.name for field in fields(data)]
        await self.execute(
            f"""
            INSERT INTO public.{self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            ON CONFLICT (discord_id) DO UPDATE SET
            {', '.join(f'{column} = EXCLUDED.{column}' for column in columns if column != 'discord_id')}
            """, astuple(data)
        )

    async def delete(self, discord_id: int) -> None:
        """
        Deletes a row from the database

        Parameters
        ----------
        discord_id (int): The Discord ID
        """

        await self.execute(f'DELETE FROM public.{self.table_name} WHERE discord_id = %s', (discord_id,))


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


@dataclass
class User:
    discord_id: int
    osu_id: int
    gamemode: int


class UserTable(Table):
    def __init__(self):
        super().__init__(table_name='user', dataclass=User, create_row_on_none=False)


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

        inserted = await self.execute(
            f'INSERT INTO public.{self.table_name} VALUES (%s, %s, %s) ON CONFLICT (discord_id) DO NOTHING',
            astuple(verification)
        )
        return inserted == 1
