import platform
from collections import Counter
from os import getpid
from os.path import exists
from time import time

import discord
from discord import app_commands
from discord.ext import commands
from psutil import Process

from cogs.utils import embed_templates


class BotInfo(commands.Cog):
    """View information about the bot"""

    def __init__(self, bot: commands.Bot):
        """
        Parameters
        ----------
        bot (commands.Bot): The bot instance
        """

        self.bot = bot

    @app_commands.checks.bot_has_permissions(embed_links=True, external_emojis=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name='botinfo', description='Shows information about the bot')
    async def botinfo(self, interaction: discord.Interaction):
        """
        View information about the bot

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        # Dev user info
        dev = await self.bot.fetch_user(170506717140877312)

        # Memory usage
        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)

        # Presences are only available on members, and a user in several servers shows up once per server,
        # so key by ID to count every user once
        statuses = {member.id: member.status for member in self.bot.get_all_members()}
        status_counts = Counter(statuses.values())

        # Build embed
        embed = discord.Embed(color=interaction.client.user.color, url=self.bot.misc['website'])
        embed.set_author(name=dev.name, icon_url=dev.display_avatar)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name='Dev', value=f'{dev.mention}\n{dev.name}')
        embed.add_field(name='Uptime', value=self._get_uptime())
        embed.add_field(name='Ping', value=f'Websocket ping: {self._get_ping()} ms')
        embed.add_field(name='Servers', value=len(self.bot.guilds))
        embed.add_field(name='Discord.py', value=discord.__version__)
        embed.add_field(name='Python', value=platform.python_version())
        embed.add_field(name='Usage', value=f'RAM: {memory_usage} MB')
        embed.add_field(name='Kernel', value=f'{platform.system()} {platform.release()}')
        if exists('/.dockerenv'):
            embed.add_field(name='Docker', value='✅')
        shown_statuses = (discord.Status.online, discord.Status.idle, discord.Status.dnd, discord.Status.offline)
        embed.add_field(
            name=f'Users ({len(statuses)})',
            value=' '.join(f'{self.bot.emoji[status.value]}{status_counts[status]}' for status in shown_statuses)
        )
        embed.add_field(name='Links', value=f'[Website]({self.bot.misc["website"]}) | ' +
                                            f'[Source code]({self.bot.misc["source_code"]}) | ' +
                                            f'[Invite]({self._get_invite()})')
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name='uptime', description='Shows the bot\'s uptime')
    async def uptime(self, interaction: discord.Interaction):
        """
        View the bot's uptime

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(name='🔌 Uptime', value=self._get_uptime())
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name='ping', description='Shows the bot\'s ping')
    async def ping(self, interaction: discord.Interaction):
        """
        View the bot's ping

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(
            name='📶 Ping',
            value=f'**Websocket ping:** {self._get_ping()} ms'
        )
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed, content=None)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name='invite', description='Get the bot\'s invite link')
    async def invite(self, interaction: discord.Interaction):
        """
        Get the bot's invite link

        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction
        """

        embed = discord.Embed(color=interaction.client.user.color, title='Invite')
        embed.description = f'[Click here]({self._get_invite()}) to invite me to your server!'
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed, content=None)

    def _get_invite(self) -> str:
        """
        Returns the bot's invite link

        Returns
        ----------
        (str): The bot's invite link
        """

        return f'https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=414733126656'

    def _get_ping(self) -> int:
        """
        Get the bot's ping in milliseconds

        Returns
        ----------
        (int): The bot's ping in milliseconds
        """

        return int(self.bot.latency * 1000)

    def _get_uptime(self) -> str:
        """
        Returns the current uptime of the bot in string format

        Returns
        ----------
        (str): The bot's uptime in human readable format
        """

        now = time()
        diff = int(now - self.bot.uptime)
        days, remainder = divmod(diff, 24 * 60 * 60)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        return f'{days}d, {hours}h, {minutes}m, {seconds}s'


async def setup(bot: commands.Bot):
    """
    Add the cog to the bot on extension load

    Parameters
    ----------
    bot (commands.Bot): The bot instance
    """

    await bot.add_cog(BotInfo(bot))
