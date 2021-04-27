import discord


async def default_footer(ctx: discord.ext.commands.Context, embed: discord.Embed) -> discord.Embed:
    """
    Sets a footer containing the command invoker's name, discriminator and avatar

    Parameters
    -----------
    ctx (discord.ext.commands.Context): The current Discord context
    embed (discord.Embed): An embed object to add the footer to

    Returns
    -----------
    (discord.Embed): The sent in embed + footer
    """

    return embed.set_footer(icon_url=ctx.author.avatar_url, text=f'{ctx.author.name}#{ctx.author.discriminator}')


async def error_warning(ctx: discord.ext.commands.Context, text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template

    Parameters
    -----------
    ctx (discord.ext.commands.Context): The current Discord context
    text (str): The error message

    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    embed = discord.Embed(color=discord.Color.gold(), description=f'⚠️ {text}')
    await default_footer(ctx, embed)

    return embed


async def error_fatal(ctx: discord.ext.commands.Context, text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template

    Parameters
    -----------
    ctx (discord.ext.commands.Context): The current Discord context
    text (str): The error message

    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    embed = discord.Embed(color=discord.Color.red(), description=f'❌ {text}')
    await default_footer(ctx, embed)

    return embed
