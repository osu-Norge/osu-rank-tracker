from os import environ, getpid
import platform
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
        interaction (discord.Interaction): Slash command context object
        """

        # Dev user info
        dev = await self.bot.fetch_user(170506717140877312)

        # Memory usage
        process = Process(getpid())
        memory_usage = round(process.memory_info().rss / 1000000, 1)

        # Member stats
        #
        # This is a pretty stupid way of doing things but it's the best I can come up with.
        # Using curly brackets for both dicts and sets is retarded becuase
        # I have to do this shit in order to create a fucking empty set.
        #
        # Apparently you can't access user presences, only member presences
        # Because of that I have to use sets instead of ints in order to not count duplicate users.
        # Fucking hell discord...
        total_members = set([])
        online_members = set([])
        idle_members = set([])
        dnd_members = set([])
        offline_members = set([])
        for guild in self.bot.guilds:
            for member in guild.members:
                total_members.add(member.id)
                if str(member.status) == 'online':
                    online_members.add(member.id)
                elif str(member.status) == 'idle':
                    idle_members.add(member.id)
                elif str(member.status) == 'dnd':
                    dnd_members.add(member.id)
                elif str(member.status) == 'offline':
                    offline_members.add(member.id)

        # Build embed
        embed = discord.Embed(color=interaction.client.user.color, url=self.bot.misc['website'])
        embed.set_author(name=dev.name, icon_url=dev.display_avatar)
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name='Dev', value=f'{dev.mention}\n{dev.name}#{dev.discriminator}')
        embed.add_field(name='Uptime', value=self.__get_uptime())
        embed.add_field(name='Ping', value=f'Websocket ping: {self.__get_ping()} ms')
        embed.add_field(name='Servers', value=len(self.bot.guilds))
        embed.add_field(name='Discord.py', value=discord.__version__)
        embed.add_field(name='Python', value=platform.python_version())
        embed.add_field(name='Usage', value=f'RAM: {memory_usage} MB')
        embed.add_field(name='Kernel', value=f'{platform.system()} {platform.release()}')
        if 'docker' in environ:
            embed.add_field(name='Docker', value='U+FE0F')
        embed.add_field(name=f'Users ({len(total_members)})',
                        value=f'{self.bot.emoji["online"]}{len(online_members)} ' +
                              f'{self.bot.emoji["idle"]}{len(idle_members)} ' +
                              f'{self.bot.emoji["dnd"]}{len(dnd_members)} ' +
                              f'{self.bot.emoji["offline"]}{len(offline_members)}')
        embed.add_field(name='Links', value=f'[Website]({self.bot.misc["website"]}) | ' +
                                            f'[Source code]({self.bot.misc["source_code"]}) |' +
                                            f'[Invite]({self.__get_invite()})')
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
        interaction (discord.Interaction): Slash command context object
        """

        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(name='🔌 Uptime', value=self.__get_uptime())
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
        interaction (discord.Interaction): Slash command context object
        """

        embed = discord.Embed(color=interaction.client.user.color)
        embed.add_field(
            name='📶 Ping',
            value=f'**Websocket ping:** {self.__get_ping()} ms'
        )
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed, content=None)

    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 2)
    @app_commands.command(name='ping', description='Get the bot\'s invite link')
    async def invite(self, interaction: discord.Interaction):
        """
        Get the bot's invite link

        Parameters
        ----------
        interaction (discord.Interaction): Slash command context object
        """

        embed = discord.Embed(color=interaction.client.user.color, title='Invite')
        embed.description = f'[Click here]({self.__get_invite()}) to invite me to your server!'
        embed_templates.default_footer(interaction, embed)
        await interaction.response.send_message(embed=embed, content=None)

    def __get_invite(self) -> str:
        """
        Returns the bot's invite link

        Returns
        ----------
        (str) The bot's invite link
        """'

        return f'https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=414733126656'

    def __get_ping(self) -> int:
        """
        Get the bot's ping in milliseconds

        Returns
        ----------
        (int) The bot's ping in milliseconds
        """

        return int(self.bot.latency * 1000)

    def __get_uptime(self) -> str:
        """
        Returns the current uptime of the bot in string format

        Returns
        ----------
        (str) The bot's uptime in human readable format
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
    bot (commands.Bot): Bot instance
    """

    await bot.add_cog(BotInfo(bot))

