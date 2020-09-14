from discord.ext import commands
import discord

import pymongo.errors

from requests import get
import urllib.parse

from cogs.utils import Defaults


class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.group(aliases=['blacklist'])
    async def svarteliste(self, ctx):
        """Hindre noen osu!brukere fra å bli med"""

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @svarteliste.command(aliases=['show', 'list'])
    async def vis(self, ctx):
        """Se svartelista"""

        try:
            db_users = self.bot.blacklist.find()
        except pymongo.errors.ServerSelectionTimeoutError:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        blacklisted = []
        for user in db_users:
            user_id = user['osu_user_id']
            blacklisted.append(f'[{user_id}](https://osu.ppy.sh/users/{user_id})')

        if not blacklisted:
            return await ctx.send('Svartelista er tom!')

        embed = discord.Embed(color=ctx.me.color)
        embed.description = '\n'.join(blacklisted)
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)

    @svarteliste.command(aliases=['leggtil', 'add'])
    async def ny(self, ctx, osu_bruker: str):
        """Legg en bruker inn i svartelista"""

        try:
            url = 'https://osu.ppy.sh/api/get_user?' + urllib.parse.urlencode({
                'u': osu_bruker, 'k': self.bot.osu_api_key
            })
            data = get(url).json()
            user_id = data[0]['user_id']
            username = data[0]['username']
        except (KeyError, IndexError):
            return await Defaults.error_warning_send(ctx, text='Kunne ikke finne brukeren!')

        query = {'osu_user_id': user_id}
        try:
            db_user = self.bot.blacklist.find_one(query)
        except pymongo.errors.ServerSelectionTimeoutError:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        if db_user is not None:
            return await ctx.send('Brukeren er allerede registrert i svartelista')

        self.bot.blacklist.insert_one({'osu_user_id': user_id})

        embed = discord.Embed(color=ctx.me.color)
        embed.set_thumbnail(url=f'https://a.ppy.sh/{user_id}?.png')
        embed.description = '✅ Bruker lagt til i svartelista!'
        embed.add_field(name='Brukernavn', value=username)
        embed.add_field(name='ID', value=user_id)
        embed.add_field(name='URL', value=f'https://osu.ppy.sh/users/{user_id}', inline=False)
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)

    @svarteliste.command(aliases=['slett', 'remove', 'delete'])
    async def fjern(self, ctx, osu_id: str):
        """Fjern en bruker inn i svartelista"""

        try:
            self.bot.blacklist.delete_one({'osu_user_id': osu_id})
        except pymongo.errors.ServerSelectionTimeoutError:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        embed = discord.Embed(color=ctx.me.color)
        embed.description = '✅ Bruker er fjernet fra svartelista!'
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Blacklist(bot))
