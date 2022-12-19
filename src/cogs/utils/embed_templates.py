import discord


def default_footer(interaction: discord.Interaction, embed: discord.Embed) -> discord.Embed:
    """
    Sets a footer containing the command invoker's name, discriminator and avatar
    Parameters
    -----------
    interaction (discord.Interaction): Slash command context object
    embed (discord.Embed): An embed object to add the footer to
    Returns
    -----------
    (discord.Embed): The passed in embed + footer
    """

    return embed.set_footer(
        icon_url=interaction.user.avatar,
        text=f'{interaction.user.name}#{interaction.user.discriminator}'
    )


def error_warning(interaction: discord.Interaction, text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template
    Parameters
    -----------
    interaction (discord.Interaction): Slash command context object
    text (str): The error message
    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    embed = discord.Embed(color=discord.Color.gold(), description=f'⚠️ {text}')
    default_footer(interaction, embed)

    return embed


def error_fatal(interaction: discord.Interaction, text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template
    Parameters
    -----------
    interaction (discord.Interaction): Slash command context object
    text (str): The error message
    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    embed = discord.Embed(color=discord.Color.red(), description=f'❌ {text}')
    default_footer(interaction, embed)

    return embed


def success(interaction: discord.Interaction, text: str) -> discord.Embed:
    """
    Creates an embed with a specified message using a template signifying success.
    Parameters
    -----------
    interaction (discord.Interaction): Slash command context object
    text (str): The message
    Returns
    -----------
    discord.Embed: An embed object based on the template with the specified text
    """

    embed = discord.Embed(color=discord.Color.green(), description=f'✅ {text}')
    default_footer(interaction, embed)

    return embed

