import discord


def default_footer(interaction: discord.Interaction, embed: discord.Embed) -> discord.Embed:
    """
    Sets a footer containing the command invoker's name, discriminator and avatar

    Parameters
    -----------
    interaction (discord.Interaction): The slash command context object
    embed (discord.Embed): An embed object to add the footer to

    Returns
    -----------
    (discord.Embed): The passed in embed + footer
    """

    return embed.set_footer(
        icon_url=interaction.user.avatar,
        text=interaction.user.name
    )


def error_warning(text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template

    Parameters
    -----------
    text (str): The error message

    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    return discord.Embed(color=discord.Color.gold(), description=f'⚠️ {text}')


def error_fatal(text: str) -> discord.Embed:
    """
    Creates an embed with a specified error message based on a warning template

    Parameters
    -----------
    text (str): The error message

    Returns
    -----------
    (discord.Embed): An embed object based on the template with the specified text
    """

    return discord.Embed(color=discord.Color.red(), description=f'❌ {text}')


def success(text: str) -> discord.Embed:
    """
    Creates an embed with a specified message using a template signifying success.

    Parameters
    -----------
    text (str): The message

    Returns
    -----------
    discord.Embed: An embed object based on the template with the specified text
    """

    return discord.Embed(color=discord.Color.green(), description=f'✅ {text}')
