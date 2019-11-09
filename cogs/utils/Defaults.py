import discord


async def error_fatal_send(ctx, text, *, mention=False):
    embed = discord.Embed(color=0xFF0000, description=f'❌ {text}')
    embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

    if mention:
        return await ctx.send(content=ctx.author.mention, embed=embed)

    return await ctx.send(embed=embed)


async def error_warning_send(ctx, text, *, mention=False):
    embed = discord.Embed(color=0xF1C40F, description=f'⚠️ {text}')
    embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')

    if mention:
        return await ctx.send(content=ctx.author.mention, embed=embed)

    return await ctx.send(embed=embed)


async def set_footer(ctx, embed):
    return embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')
