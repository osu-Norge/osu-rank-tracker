from __future__ import annotations
from abc import abstractmethod
from dataclasses import astuple, dataclass

import psycopg2
import yaml


class Database:
    def __init__(self):
        with open('./src/config/config.yaml', 'r', encoding='utf8') as f:
            self.db = yaml.load(f, Loader=yaml.SafeLoader).get('database', {})

    delete(self, discord_id: int) -> None:
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
    registration_channel: int | None
    whitelisted_countries: list[str] | None
    blacklisted_osu_users: list[int] | None
    role_moderator: int | None
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
class Channel:
    discord_id: int
    clean_after_message_id: int | None


class ChannelTable(Table):
    def __init__(self):
        super().__init__(table_name='channel', dataclass=Channel, create_row_on_none=True)

    async def save(self, channel: Channel) -> None:
        """
        Save a channel object in the database

        Parameters
        ----------
        channel (Channel): A user object
        """

        values = astuple(channel)

        try:
            self.cursor.execute(f'INSERT INTO {self.table_name} VALUES (%s %s)', values)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
        else:
            return

        values = values + (channel.discord_id,)

        self.cursor.execute(
            f"""
            UPDATE {self.table_name} SET
            discord_id = %s,
            clean_after_message_id = %s
            WHERE discord_id = %s
            """, values
        )
        self.connection.commit()


@dataclass
class Verification:
    discord_id: int
    uuid: str


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
            self.cursor.execute(f'INSERT INTO {self.table_name} VALUES (%s, %s)', values)
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            self.connection.rollback()
            return False

        return True
