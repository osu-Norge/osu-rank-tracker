import discord


async def error_fatal_send(ctx, text, *, mention=False):
    """Message template for fatal errors"""

    embed = discord.Embed(color=0xFF0000, description=f'❌ {text}')
    embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

    if mention:
        return await ctx.send(content=ctx.author.mention, embed=embed)

    return await ctx.send(embed=embed)


async def error_warning_send(ctx, text, *, mention=False):
    """Message template for non-fatal errors"""

    embed = discord.Embed(color=0xF1C40F, description=f'⚠️ {text}')
    embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

    if mention:
        return await ctx.send(content=ctx.author.mention, embed=embed)

    return await ctx.send(embed=embed)


async def set_footer(ctx, embed):
    """Adds commands invoker's user info to embed footer"""

    return embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')


async def get_user_color(user):
    """Returns the top role color of a user"""

    if str(user.color) != '#000000':
        return user.color

    return discord.Colour(0x99AAB5)
