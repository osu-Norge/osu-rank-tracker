from discord.ext import commands
import discord

from requests import get
import urllib.parse
from asyncio import sleep

from cogs.utils import Defaults, OsuUtils, Checks


class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Checks.is_set_channel()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def osuset(self, ctx, osu_brukernavn: str, *, gamemode: str=None):
        """Kobler osu!brukeren din opp mot båtten"""

        gamemode = await OsuUtils.get_gamemode(gamemode)
        if gamemode is None:
            return await Defaults.error_warning_send(ctx, text='Ugyldig gamemode!')

        try:
            url = 'https://osu.ppy.sh/api/get_user?' + urllib.parse.urlencode({
                'u': osu_brukernavn, 'm': gamemode, 'k': self.bot.osu_api_key
            })
            data = get(url).json()
            user_id = data[0]['user_id']
            country = data[0]['country'].lower()
        except:
            invalid_user_msg = await Defaults.error_warning_send(ctx, text='Kunne ikke finne brukeren!')
            await sleep(120)
            await ctx.message.delete()
            await invalid_user_msg.delete()
            return

        dansk, svensk, country_roles = await OsuUtils.get_country_roles(self, ctx.guild)
        accepted_countries = {
            "dk": dansk,
            "se": svensk
        }
        if country in accepted_countries:
            country = accepted_countries[country]
            await OsuUtils.remove_old_roles(ctx.author, country_roles, country)
            await ctx.author.add_roles(country)
        elif country == 'no':
            await OsuUtils.remove_old_roles(ctx.author, country_roles, country)
        else:
            invalid_user_msg = await Defaults.error_warning_send(ctx, text='Sorry, we only allow Norwegian, Swedish ' +
                                                                           'and Danish users on this server :(')

            await sleep(120)
            await ctx.message.delete()
            await invalid_user_msg.delete()
            return

        query = {'osu_user_id': user_id}
        try:
            db_user = self.bot.database.find_one(query)
        except:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        if db_user is not None:
            invalid_user_msg = await Defaults.error_warning_send(ctx, text='Det ser ut som at noen andre har ' +
                                                                           'registert seg med den brukeren\n\n' +
                                                                           'Om du er helt sikker på at dette er ' +
                                                                           'din bruker, kontakt mods')
            await sleep(120)
            await ctx.message.delete()
            await invalid_user_msg.delete()
            return

        status_msg = await ctx.send(f'Gyldig bruker funnet! Legger deg inn i databasen og sjekker rank...')

        if db_user is None:
            self.bot.database.insert_one({
                '_id': ctx.author.id,
                'osu_user_id': user_id,
                'gamemode': gamemode
            })
        else:
            self.bot.database.update_one(query, {'$set': {'osu_user_id': user_id, 'gamemode': gamemode}})

        try:
            rank = int(data[0]["pp_rank"])
        except:
            rank = 0

        rank_roles = await OsuUtils.get_rank_roles(self, ctx.guild)
        rank_role = await OsuUtils.rank_role(rank, rank_roles)
        await OsuUtils.remove_old_roles(ctx.author, rank_roles, rank_role)
        if rank_role != 'no rank role':
            await ctx.author.add_roles(rank_role)
            rank_msg = await ctx.send(f'{ctx.author.mention} Du har fått rollen **{rank_role.name}**')
        else:
            rank_msg = await ctx.send(f'{ctx.author.mention} Ranken din er for lav for å få en rolle. Du har ' +
                                      'likevel fått tilgang til serveren og heg vil følge med på ranken din og ' +
                                      'gi deg rolle om den blir høy nok :eyes:')

        standard, taiko, ctb, mania, gamemode_roles = await OsuUtils.get_gamemode_roles(self, ctx.guild)
        gamemode = str(gamemode)
        gamemodes = {
            "0": standard,
            "1": taiko,
            "2": ctb,
            "3": mania
        }
        gamemode = gamemodes[gamemode]
        await OsuUtils.remove_old_roles(ctx.author, gamemode_roles, gamemode)
        await ctx.author.add_roles(gamemode)

        anti_server_pass = ctx.guild.get_role(self.bot.roles['anti-server-pass'])
        await ctx.author.remove_roles(anti_server_pass)

        await sleep(60)
        await ctx.message.delete()
        await status_msg.delete()
        await rank_msg.delete()

    @Checks.is_guild()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['setgamemode'])
    async def gamemode(self, ctx, *, gamemode: str):
        """Endrer gamemode assosiert med brukeren din"""

        gamemode = await OsuUtils.get_gamemode(gamemode)
        if gamemode is None:
            return await Defaults.error_warning_send(ctx, text='Ugyldig gamemode!')

        query = {'_id': ctx.author.id}
        try:
            db_user = self.bot.database.find_one(query)
        except:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        if db_user is None:
            return Defaults.error_warning_send(ctx, text='Du har ikke registrert brukeren din enda!')

        self.bot.database.update_one(query, {'$set': {'gamemode': gamemode}})

        db_user = self.bot.database.find_one(query)
        osu_user = db_user['osu_user_id']

        try:
            url = 'https://osu.ppy.sh/api/get_user?' + urllib.parse.urlencode({
                'u': osu_user, 'm': gamemode, 'k': self.bot.osu_api_key
            })
            data = get(url).json()
        except:
            return await Defaults.error_warning_send(ctx, text='Kunne ikke finne brukeren!')

        try:
            rank = int(data[0]["pp_rank"])
        except:
            rank = 0

        rank_roles = await OsuUtils.get_rank_roles(self, ctx.guild)
        rank_role = await OsuUtils.rank_role(rank, rank_roles)
        await OsuUtils.remove_old_roles(ctx.author, rank_roles, rank_role)
        if rank_role != 'no rank role':
            await ctx.author.add_roles(rank_role)

        standard, taiko, ctb, mania, gamemode_roles = await OsuUtils.get_gamemode_roles(self, ctx.guild)
        gamemode = str(gamemode)
        gamemodes = {
            "0": standard,
            "1": taiko,
            "2": ctb,
            "3": mania
        }
        gamemode = gamemodes[gamemode]
        await OsuUtils.remove_old_roles(ctx.author, gamemode_roles, gamemode)
        await ctx.author.add_roles(gamemode)

        if rank_role != 'no rank role':
            await ctx.send(f'{ctx.author.mention} Du har fått rollen **{gamemode.name}** og ' +
                           f'rank har blitt satt til **{rank_role.name}**!')
        else:
            await ctx.send(f'{ctx.author.mention} Du har fått rollen **{gamemode.name}** og ' +
                           f'rank har blitt fjernet pga for lav rank')

    @Checks.is_guild()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command()
    async def forceset(self, ctx, discord_bruker: discord.Member, osu_bruker: str, *, gamemode: str=None):
        """Setter rollene til en bruker"""

        gamemode = await OsuUtils.get_gamemode(gamemode)
        if gamemode is None:
            return await Defaults.error_warning_send(ctx, text='Ugyldig gamemode!')

        try:
            url = 'https://osu.ppy.sh/api/get_user?' + urllib.parse.urlencode({
                'u': osu_bruker, 'm': gamemode, 'k': self.bot.osu_api_key
            })
            data = get(url).json()
            user_id = data[0]['user_id']
            country = data[0]['country'].lower()
            username = data[0]['username']
        except:
            return await Defaults.error_warning_send(ctx, text='Kunne ikke finne brukeren!')

        dansk, svensk, country_roles = await OsuUtils.get_country_roles(self, ctx.guild)
        accepted_countries = {
            "dk": dansk,
            "se": svensk
        }
        if country in accepted_countries:
            country = accepted_countries[country]
            await OsuUtils.remove_old_roles(discord_bruker, country_roles, country)
            await discord_bruker.add_roles(country)
        else:
            await OsuUtils.remove_old_roles(discord_bruker, country_roles, country)

        query = {'osu_user_id': user_id}
        try:
            db_user = self.bot.database.find_one(query)
        except:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')

        if db_user is not None:
            await ctx.send(f'{ctx.author.mention} ADVARSEL! Denne osu!brukeren er allerede ' +
                           'registrert på serveren. Fortsetter alikavel...')

        status_msg = await ctx.send(f'Gyldig bruker funnet! Legger inn i databasen og sjekker rank...')

        if db_user is None:
            self.bot.database.insert_one({
                '_id': discord_bruker.id,
                'osu_user_id': user_id,
                'gamemode': gamemode
            })
        else:
            self.bot.database.update_one(query, {'$set': {'osu_user_id': user_id, 'gamemode': gamemode}})

        try:
            rank = int(data[0]["pp_rank"])
        except:
            rank = 0

        rank_roles = await OsuUtils.get_rank_roles(self, ctx.guild)
        rank_role = await OsuUtils.rank_role(rank, rank_roles)
        await OsuUtils.remove_old_roles(discord_bruker, rank_roles, rank_role)
        if rank_role != 'no rank role':
            await discord_bruker.add_roles(rank_role)

        standard, taiko, ctb, mania, gamemode_roles = await OsuUtils.get_gamemode_roles(self, ctx.guild)
        gamemode = str(gamemode)
        gamemodes = {
            "0": standard,
            "1": taiko,
            "2": ctb,
            "3": mania
        }
        gamemode = gamemodes[gamemode]
        await OsuUtils.remove_old_roles(discord_bruker, gamemode_roles, gamemode)
        await discord_bruker.add_roles(gamemode)

        anti_server_pass = ctx.guild.get_role(self.bot.roles['anti-server-pass'])
        await discord_bruker.remove_roles(anti_server_pass)

        color = await Defaults.get_user_color(discord_bruker)
        embed = discord.Embed(color=color, title='Bruker satt!',
                              description=f'{discord_bruker.mention}\n' +
                              f'{discord_bruker.name}#{discord_bruker.discriminator}')
        embed.set_thumbnail(url=discord_bruker.avatar_url)
        embed.add_field(name='osu!brukernavn', value=username)
        embed.add_field(name='osu!id', value=user_id)
        embed.add_field(name='Gamemode', value=gamemode)
        embed.add_field(name='URL', value=f'https://osu.ppy.sh/users/{user_id}')
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)

    @Checks.is_guild()
    @commands.command(aliases=['user'])
    async def bruker(self, ctx, *, bruker: discord.Member=None):
        """Se hvilken osu!bruker som er koblet til båtten"""

        if not bruker:
            bruker = ctx.author

        query = {'_id': bruker.id}
        try:
            db_user = self.bot.database.find_one(query)
        except:
            return await Defaults.error_fatal_send(ctx, text='Jeg har ikke tilkobling til databasen\n\n' +
                                                             'Be båtteier om å fikse dette')
        if db_user is None:
            return await Defaults.error_fatal_send(ctx, text='Brukeren har ikke koblet til osu!kontoen sin!')

        color = await Defaults.get_user_color(bruker)

        user_id = db_user['osu_user_id']
        gamemode_url = await OsuUtils.get_gamemode_url(db_user['gamemode'])
        gamemode = await OsuUtils.convert_gamemode_name(db_user['gamemode'])
        url = f'https://osu.ppy.sh/users/{user_id}/{gamemode_url}'

        embed = discord.Embed(color=color, url=url, description=bruker.mention)
        embed.set_author(name=f'{bruker.name}#{bruker.discriminator}', icon_url=bruker.avatar_url)
        embed.set_thumbnail(url=bruker.avatar_url)
        embed.add_field(name='osu!id', value=user_id)
        embed.add_field(name='Gamemode', value=gamemode)
        embed.add_field(name='Lenke til osu!profil', value=url, inline=False)
        await Defaults.set_footer(ctx, embed)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(RoleManager(bot))
