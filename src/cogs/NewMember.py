from discord.ext import commands


class NewMember(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Gives the user the anti-server-pass role whenever they join the guild"""

        if member.bot or member.guild.id != self.bot.guild:
            return
        await member.add_roles(member.guild.get_role(self.bot.roles['anti-server-pass']))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Removes the user from database whenever they leave the guild"""

        if member.bot or member.guild.id != self.bot.guild:
            return
        self.bot.database.delete_one({'_id': member.id})


def setup(bot):
    bot.add_cog(NewMember(bot))
