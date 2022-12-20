import asyncio
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.database as database
from cogs.utils.osu_api import OsuApi


class RankUpdate(commands.Cog):
    """Cog for handling rank updates"""

    def __init__(self, bot):
        self.bot = bot
        self.update_ranks.start()
        self.rank_cache = {}

    def cog_unload(self):
        self.update_ranks.cancel()

    async def __update_user_rank(self, guild: database.Guild, member: discord.Member, rank: int, gamemode_id: int, reason: str = None):
        """
        Update a user's rank

        Parameters
        ----------
        guild (database.GuildTable): A fetched guild from the database
        member (discord.Member): A Discord member object
        rank (int): The user's osu! rank
        gamemode (int): The user's osu! gamemode
        reason (str): The reason for the rank update
        """

        # Rank roles
        # This is terrible, I know :P
        if rank < 10:
            roles_to_add = set(['role_1_digit'])
            roles_to_remove = set(['role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 100:
            roles_to_add = set(['role_2_digit'])
            roles_to_remove = set(['role_1_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 1000:
            roles_to_add = set(['role_3_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 10000:
            roles_to_add = set(['role_4_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_5_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 100000:
            roles_to_add = set(['role_5_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_6_digit', 'role_7_digit'])
        elif rank < 1000000:
            roles_to_add = set(['role_6_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_7_digit'])
        else:
            roles_to_add = set(['role_7_digit'])
            roles_to_remove = set(['role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit', 'role_5_digit', 'role_6_digit'])

        # Gamemode roles
        match gamemode_id:
            case 0:
                roles_to_add.add('role_standard')
                roles_to_remove.add(['role_taiko', 'role_ctb', 'role_mania'])
            case 1:
                roles_to_add.add('role_taiko')
                roles_to_remove.add(['role_standard', 'role_ctb', 'role_mania'])
            case 2:
                roles_to_add.add('role_ctb')
                roles_to_remove.add(['role_standard', 'role_taiko', 'role_mania'])
            case 3:
                roles_to_add.add('role_mania')
                roles_to_remove.add(['role_standard', 'role_taiko', 'role_ctb'])

        # Add and remove any additional roles
        if guild.role_remove:
            roles_to_remove.append(guild.role_remove)
        if guild.role_add:
            roles_to_add.append(guild.role_add)

        # Convert role strings to Role objects
        roles_to_add = [member.guild.get_role(getattr(guild, attr)) for attr in roles_to_add if getattr(guild, attr)]
        roles_to_remove = [member.guild.get_role(getattr(guild, attr)) for attr in roles_to_remove if getattr(guild, attr)]

        await member.remove_roles(*roles_to_remove, reason=reason)
        await member.add_roles(*roles_to_add, reason=reason)

    @tasks.loop(hours=24)
    async def update_ranks(self):
        """
        Update the ranks of all users in the database
        """

        user_table = database.UserTable()
        guild_table = database.GuildTable()

        guilds = guild_table.get_all()

        user_count = user_table.count()
        sleep_time = user_count / 60  # TODO: calculate optimal sleep time based on user count and ratelimit

        for guild in guilds:
            for member in guild.members:
                if member.bot:
                    continue

                if not (user := user_table.get(member.id)):
                    continue

                if not (rank := self.rank_cache.get(user.id)):
                    osu_user = OsuApi.get_user(user.osu_id)
                    if not osu_user:
                        continue
                    rank = osu_user["statistics"]["global_rank"]
                    self.rank_cache[user.id] = rank

                # Update the user's rank
                await self.__update_user_rank(guild, member, rank, user.gamemode, reason='Automatic rank update based on osu! rank')

                await asyncio.sleep(sleep_time)

        self.rank_cache = {}  # Clear the rank cache

    @update_ranks.before_loop
    async def before_update_ranks(self):
        """
        Schedule the update ranks task to run at 00:00 UTC
        """

        await self.bot.wait_until_ready()

        now = datetime.utcnow()

        if now.hour > 0:
            sleep_until = now + datetime.timedelta(days=1)
            sleep_until = sleep_until.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            sleep_until = now.replace(hour=0, minute=0, second=0, microsecond=0)

        await discord.utils.sleep_until(sleep_until)

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self: commands.Bot, guild: discord.Guild):
        """
        Create a new guild in the database when the bot joins a guild

        Parameters
        ----------
        guild (discord.Guild): Guild instance
        """

        guild = database.Guild(discord_id=guild.id)
        await database.GuildTable().save(guild)

    @commands.Cog.listener('on_member_join')
    async def on_member_join(self, member: discord.Member):
        """
        Immidiately update a user's rank when they join a guild

        Parameters
        ----------
        member (discord.Member): Member instance
        """

        guild = await database.GuildTable().get(member.guild.id)
        user = await database.UserTable().get(member.id)
        if user:
            await self.__update_user_rank(guild, member, user.gamemode, reason='User joined guild')

    @app_commands.checks.cooldown(1, 60*60*12)  # 12 hours
    @app_commands.command(name='force_update')
    async def force_user_rank_update(self, interaction: discord.Interaction):
        """
        Force's a rank update for your user

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        guild = database.GuildTable().get(interaction.guild.id)
        user = database.UserTable().get(interaction.author.id)
        if user:
            self.__update_user_rank(guild, interaction.author, user.gamemmode, reason='User forced rank update through command')


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(RankUpdate(bot))
