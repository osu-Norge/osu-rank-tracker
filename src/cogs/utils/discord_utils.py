from contextlib import suppress

import discord

from cogs.utils import embed_templates


def get_color(discord_object: discord.User | discord.Member | discord.Role) -> discord.Color:
    """
    Returns the user's top role color

    Parameters
    ----------
    discord_object (discord.User | discord.Member | discord.Role): A discord object that has a color attribute

    Returns
    ----------
    (discord.Color): The user's displayed color
    """

    if hasattr(discord_object, 'color') and str(discord_object.color) != '#000000':
        return discord_object.color

    return discord.Colour(0x99AAB5)


class Scroller(discord.ui.View):
    """Buttons to flip through the pages of an embed. Only the user who ran the command can use them"""

    def __init__(self, pages: list[discord.Embed], interaction: discord.Interaction):
        """
        Parameters
        ----------
        pages (list[discord.Embed]): The pages
        interaction (discord.Interaction): The slash command interaction
        """

        super().__init__(timeout=180)
        self.pages = pages
        self.interaction = interaction
        self.page = 0
        self._update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Only let the user who ran the command use the buttons

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that triggered this

        Returns
        ----------
        (bool): Whether the button press is allowed
        """

        if interaction.user.id == self.interaction.user.id:
            return True

        embed = embed_templates.error_warning('Only the user who ran the command can use these buttons')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    async def on_timeout(self):
        """
        Remove the buttons once they stop working
        """

        with suppress(discord.HTTPException):
            await self.interaction.edit_original_response(view=None)

    @discord.ui.button(label='<', style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show the previous page

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that triggered this
        button (discord.ui.Button): The button that was pressed
        """

        self.page -= 1
        await self._show_page(interaction)

    @discord.ui.button(label='>', style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Show the next page

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that triggered this
        button (discord.ui.Button): The button that was pressed
        """

        self.page += 1
        await self._show_page(interaction)

    async def _show_page(self, interaction: discord.Interaction):
        """
        Show the current page and update which buttons can be pressed

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that triggered this
        """

        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.page], view=self)

    def _update_buttons(self):
        """
        Disable the buttons that would go past the first or last page
        """

        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = self.page == len(self.pages) - 1
