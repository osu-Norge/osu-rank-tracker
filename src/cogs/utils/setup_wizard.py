import re
from contextlib import suppress

import aiohttp
import discord
from iso3166 import countries

from cogs.utils import database, discord_utils, embed_templates
from cogs.utils.osu_api import Gamemode, OsuApi

RANK_ROLES_DESCRIPTION = 'Given by global rank in the gamemode the member registered with. Updated every 12 hours'

# The role steps of the wizard: title, description and role settings. A step can have at most 4 roles to fit the layout
ROLE_STEPS = (
    (
        'Registration roles',
        'Changed when a member links their osu! account with `/user register`',
        ('role_add', 'role_remove')
    ),
    ('Rank roles', RANK_ROLES_DESCRIPTION, ('role_1_digit', 'role_2_digit', 'role_3_digit', 'role_4_digit')),
    ('Rank roles (continued)', RANK_ROLES_DESCRIPTION, ('role_5_digit', 'role_6_digit', 'role_7_digit')),
    (
        'Gamemode roles',
        'Given by the gamemode the member registered with',
        ('role_standard', 'role_taiko', 'role_ctb', 'role_mania')
    ),
)
ROLE_HELP = {
    'role_add': 'For example a Verified role',
    'role_remove': 'For example an Unverified role',
}
STEP_WHITELIST = len(ROLE_STEPS)
STEP_BLACKLIST = STEP_WHITELIST + 1
STEP_SUMMARY = STEP_BLACKLIST + 1
STEP_COUNT = STEP_SUMMARY + 1

# Text inputs can't hold more than this
MAX_INPUT_LENGTH = 4000


def _split_entries(text: str) -> list[str]:
    """
    Split comma or newline separated text into its non-empty entries

    Parameters
    ----------
    text (str): The text to split

    Returns
    ----------
    (list[str]): The entries, without surrounding whitespace
    """

    return [entry.strip() for entry in re.split(r'[,\n]', text) if entry.strip()]


def _shorten(items: list[str], limit: int = 20) -> str:
    """
    Join items with commas, cutting the list short if it's long

    Parameters
    ----------
    items (list[str]): The items to join
    limit (int): The most items to show

    Returns
    ----------
    (str): The joined items
    """

    text = ', '.join(items[:limit])
    if len(items) > limit:
        text += f' and {len(items) - limit} more'
    return text


class SetupWizard(discord.ui.LayoutView):
    """
    Walks through the guild settings one step at a time, and saves them all at the end.
    Only the user who started it can use it
    """

    def __init__(
        self,
        interaction: discord.Interaction,
        guild: database.Guild,
        role_types: dict[str, str],
        usernames: dict[int, str]
    ):
        """
        Parameters
        ----------
        interaction (discord.Interaction): The slash command interaction that started the wizard
        guild (database.Guild): The guild's current settings
        role_types (dict[str, str]): The names of the role settings shown in Discord, by database column
        usernames (dict[int, str]): The usernames of the blacklisted osu! users, by user ID
        """

        super().__init__(timeout=600)
        self.interaction = interaction  # The latest interaction, used to edit the message on timeout
        self.role_types = role_types
        # Leave out roles that no longer exist, so they don't show up as selected
        self.roles = {
            column: role_id if (role_id := getattr(guild, column)) and interaction.guild.get_role(role_id) else None
            for column in role_types
        }
        self.whitelist = list(guild.whitelisted_countries or [])
        self.blacklist = list(guild.blacklisted_osu_users or [])
        self.usernames = dict(usernames)
        self.step = 0
        self.notice = None  # A message shown on the next render only, e.g. about invalid input
        self.render()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Only let the user who started the wizard use it

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that triggered this

        Returns
        ----------
        (bool): Whether the interaction is allowed
        """

        if interaction.user.id == self.interaction.user.id:
            self.interaction = interaction
            return True

        embed = embed_templates.error_warning('Only the user who ran the command can use this')
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False

    async def on_timeout(self):
        """
        Tell the user the wizard has stopped, as its components no longer work
        """

        self._finish('⌛ Setup timed out, so nothing was saved. Run `/setup` to start again')
        with suppress(discord.HTTPException):
            await self.interaction.edit_original_response(view=self)

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        """
        Log the error and tell the user something went wrong

        Parameters
        ----------
        interaction (discord.Interaction): The interaction that failed
        error (Exception): The error
        item (discord.ui.Item): The component that was used
        """

        interaction.client.logger.exception('Setup wizard failed', exc_info=error)
        embed = embed_templates.error_fatal('Something went wrong! Please try again')
        with suppress(discord.HTTPException):
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)

    def render(self):
        """
        Rebuild the components for the current step
        """

        guild = self.interaction.guild
        container = discord.ui.Container(accent_colour=discord_utils.get_color(guild.me))

        if self.step < STEP_WHITELIST:
            title, description, columns = ROLE_STEPS[self.step]
        else:
            title, description, columns = {
                STEP_WHITELIST: ('Country whitelist', 'Only members from these countries get roles', ()),
                STEP_BLACKLIST: ('Blacklist', 'These osu! users never get roles', ()),
                STEP_SUMMARY: ('Summary', 'Nothing is saved until you press **Save**', ()),
            }[self.step]
        container.add_item(discord.ui.TextDisplay(
            f'-# Setup · step {self.step + 1} of {STEP_COUNT}\n## {title}\n{description}'
        ))

        if columns and not guild.me.guild_permissions.manage_roles:
            container.add_item(discord.ui.TextDisplay(
                '⚠️ I need the **Manage Roles** permission to give members these roles'
            ))

        for column in columns:
            self._add_role_picker(container, column)

        if self.step == STEP_WHITELIST:
            self._add_whitelist(container)
        elif self.step == STEP_BLACKLIST:
            self._add_blacklist(container)
        elif self.step == STEP_SUMMARY:
            self._add_summary(container)

        if self.notice:
            container.add_item(discord.ui.TextDisplay(self.notice))
            self.notice = None

        container.add_item(discord.ui.Separator())
        container.add_item(self._navigation())

        self.clear_items()
        self.add_item(container)

    def _add_role_picker(self, container: discord.ui.Container, column: str):
        """
        Add a labelled role select menu for a role setting

        Parameters
        ----------
        container (discord.ui.Container): The container to add it to
        column (str): The role setting's database column
        """

        label = f'**{self.role_types[column]}**'
        if help_text := ROLE_HELP.get(column):
            label += f'\n-# {help_text}'
        role = self.interaction.guild.get_role(self.roles[column]) if self.roles[column] else None
        if role and not role.is_assignable():
            label += '\n-# ⚠️ I can\'t give out this role, as it\'s above my highest role'
        container.add_item(discord.ui.TextDisplay(label))

        select = discord.ui.RoleSelect(
            placeholder='No role',
            min_values=0,
            max_values=1,
            default_values=[role] if role else []
        )

        async def callback(interaction: discord.Interaction):
            selected = select.values[0] if select.values else None
            if selected and (selected.is_default() or selected.managed):
                self.notice = f'⚠️ {selected.mention} is managed by Discord or a bot, so it can\'t be given out'
            else:
                self.roles[column] = selected.id if selected else None
            await self._show(interaction)

        select.callback = callback
        container.add_item(discord.ui.ActionRow(select))

    def _add_whitelist(self, container: discord.ui.Container):
        """
        Add the current whitelist and the buttons to change it

        Parameters
        ----------
        container (discord.ui.Container): The container to add them to
        """

        if self.whitelist:
            text = _shorten([self._country_name(code) for code in self.whitelist])
        else:
            text = 'No countries are whitelisted, so members from every country get roles'
        container.add_item(discord.ui.TextDisplay(text))

        edit = discord.ui.Button(label='Edit whitelist', style=discord.ButtonStyle.primary)
        clear = discord.ui.Button(label='Clear', style=discord.ButtonStyle.secondary, disabled=not self.whitelist)

        async def edit_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(WhitelistModal(self))

        async def clear_callback(interaction: discord.Interaction):
            self.whitelist = []
            await self._show(interaction)

        edit.callback = edit_callback
        clear.callback = clear_callback
        container.add_item(discord.ui.ActionRow(edit, clear))

    def _add_blacklist(self, container: discord.ui.Container):
        """
        Add the current blacklist and the buttons to change it

        Parameters
        ----------
        container (discord.ui.Container): The container to add them to
        """

        if self.blacklist:
            text = _shorten([self._osu_user(user_id) for user_id in self.blacklist])
        else:
            text = 'No osu! users are blacklisted'
        container.add_item(discord.ui.TextDisplay(text))

        too_long = len(self.blacklist_text()) > MAX_INPUT_LENGTH
        if too_long:
            container.add_item(discord.ui.TextDisplay(
                '-# The blacklist is too long to edit here. Use `/settings blacklist add` and `remove` instead'
            ))

        edit = discord.ui.Button(label='Edit blacklist', style=discord.ButtonStyle.primary, disabled=too_long)
        clear = discord.ui.Button(label='Clear', style=discord.ButtonStyle.secondary, disabled=not self.blacklist)

        async def edit_callback(interaction: discord.Interaction):
            await interaction.response.send_modal(BlacklistModal(self))

        async def clear_callback(interaction: discord.Interaction):
            self.blacklist = []
            await self._show(interaction)

        edit.callback = edit_callback
        clear.callback = clear_callback
        container.add_item(discord.ui.ActionRow(edit, clear))

    def _add_summary(self, container: discord.ui.Container):
        """
        Add an overview of all the settings

        Parameters
        ----------
        container (discord.ui.Container): The container to add it to
        """

        guild = self.interaction.guild
        lines = []
        for title, _, columns in ROLE_STEPS:
            if title.endswith('(continued)'):
                lines.pop()  # Show the rank roles under one heading
            else:
                lines.append(f'**{title}**')
            for column in columns:
                role = guild.get_role(self.roles[column]) if self.roles[column] else None
                lines.append(f'{self.role_types[column]}: {role.mention if role else "not set"}')
            lines.append('')

        whitelist = _shorten(self.whitelist) if self.whitelist else 'all countries'
        lines.append(f'**Country whitelist:** {whitelist}')
        lines.append(f'**Blacklisted osu! users:** {len(self.blacklist)}')

        container.add_item(discord.ui.TextDisplay('\n'.join(lines)))

        unassignable = [
            role.mention for role_id in set(self.roles.values())
            if role_id and (role := guild.get_role(role_id)) and not role.is_assignable()
        ]
        if unassignable:
            container.add_item(discord.ui.TextDisplay(
                f'⚠️ These roles are above my highest role, so I can\'t give them out: {", ".join(unassignable)}\n' +
                '-# Move my role above them in Server Settings → Roles'
            ))

    def _navigation(self) -> discord.ui.ActionRow:
        """
        Create the buttons to move between steps, save and cancel

        Returns
        ----------
        (discord.ui.ActionRow): The buttons
        """

        back = discord.ui.Button(label='Back', style=discord.ButtonStyle.secondary, disabled=self.step == 0)
        if self.step == STEP_SUMMARY:
            forward = discord.ui.Button(label='Save', style=discord.ButtonStyle.success)
        else:
            forward = discord.ui.Button(label='Next', style=discord.ButtonStyle.primary)
        cancel = discord.ui.Button(label='Cancel', style=discord.ButtonStyle.danger)

        async def back_callback(interaction: discord.Interaction):
            self.step -= 1
            await self._show(interaction)

        async def forward_callback(interaction: discord.Interaction):
            if self.step == STEP_SUMMARY:
                return await self._save(interaction)
            self.step += 1
            await self._show(interaction)

        async def cancel_callback(interaction: discord.Interaction):
            self._finish('Setup cancelled, so nothing was saved')
            await interaction.response.edit_message(view=self)

        back.callback = back_callback
        forward.callback = forward_callback
        cancel.callback = cancel_callback
        return discord.ui.ActionRow(back, forward, cancel)

    async def _show(self, interaction: discord.Interaction):
        """
        Re-render the current step in place of the wizard's message

        Parameters
        ----------
        interaction (discord.Interaction): The component or modal interaction to respond to
        """

        self.render()
        if interaction.response.is_done():
            await interaction.edit_original_response(view=self)
        else:
            await interaction.response.edit_message(view=self)

    async def _save(self, interaction: discord.Interaction):
        """
        Save all settings to the database

        Parameters
        ----------
        interaction (discord.Interaction): The interaction from the save button
        """

        guild_table = database.GuildTable()
        guild = await guild_table.get(interaction.guild.id)
        for column, role_id in self.roles.items():
            setattr(guild, column, role_id)
        guild.whitelisted_countries = self.whitelist or None
        guild.blacklisted_osu_users = self.blacklist or None
        await guild_table.save(guild)

        self._finish('✅ Settings saved! Change them any time with `/setup` or the `/settings` commands')
        await interaction.response.edit_message(view=self)

    def _finish(self, text: str):
        """
        Stop the wizard and replace it with a message

        Parameters
        ----------
        text (str): The message
        """

        self.stop()
        self.clear_items()
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(text),
            accent_colour=discord_utils.get_color(self.interaction.guild.me)
        ))

    def blacklist_text(self) -> str:
        """
        Returns
        ----------
        (str): The blacklist as editable text, with usernames where they're known and IDs otherwise
        """

        return ', '.join(self.usernames.get(user_id, str(user_id)) for user_id in self.blacklist)

    @staticmethod
    def _country_name(country_code: str) -> str:
        """
        Parameters
        ----------
        country_code (str): The ISO 3166 alpha-2 country code

        Returns
        ----------
        (str): The country's name and code
        """

        country = countries.get(country_code, None)
        return f'{country.name} ({country_code})' if country else country_code

    def _osu_user(self, user_id: int) -> str:
        """
        Parameters
        ----------
        user_id (int): The osu! user ID

        Returns
        ----------
        (str): A link to the user's profile, named after them if their username is known
        """

        return f'[{self.usernames.get(user_id, user_id)}](https://osu.ppy.sh/users/{user_id})'


class WizardModal(discord.ui.Modal):
    """A modal opened from the setup wizard, which updates the wizard when submitted"""

    def __init__(self, wizard: SetupWizard, title: str):
        """
        Parameters
        ----------
        wizard (SetupWizard): The wizard the modal belongs to
        title (str): The modal title
        """

        super().__init__(title=title)
        self.wizard = wizard

    async def on_submit(self, interaction: discord.Interaction):
        """
        Apply the input to the wizard, unless the wizard has stopped in the meantime

        Parameters
        ----------
        interaction (discord.Interaction): The modal submit interaction
        """

        if self.wizard.is_finished():
            embed = embed_templates.error_warning('This setup has ended. Run `/setup` to start again')
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        self.wizard.interaction = interaction
        self.wizard.timeout = self.wizard.timeout  # Restart the timeout, as the user was busy in the modal
        await self.apply(interaction)
        await self.wizard._show(interaction)

    async def apply(self, interaction: discord.Interaction):
        """
        Apply the input to the wizard

        Parameters
        ----------
        interaction (discord.Interaction): The modal submit interaction
        """

        raise NotImplementedError

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """
        Handle errors the same way as the wizard does

        Parameters
        ----------
        interaction (discord.Interaction): The modal submit interaction
        error (Exception): The error
        """

        await self.wizard.on_error(interaction, error, None)


class WhitelistModal(WizardModal):
    """Edit the country whitelist as text"""

    def __init__(self, wizard: SetupWizard):
        """
        Parameters
        ----------
        wizard (SetupWizard): The wizard the modal belongs to
        """

        super().__init__(wizard, title='Country whitelist')
        self.countries = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            default=', '.join(wizard.whitelist),
            placeholder='NO, SE, Denmark',
            required=False,
            max_length=MAX_INPUT_LENGTH
        )
        self.add_item(discord.ui.Label(
            text='Countries',
            description='Country codes or English names, separated by commas. Leave empty to allow all countries',
            component=self.countries
        ))

    async def apply(self, interaction: discord.Interaction):
        """
        Replace the whitelist with the valid countries entered

        Parameters
        ----------
        interaction (discord.Interaction): The modal submit interaction
        """

        whitelist, invalid = [], []
        for entry in _split_entries(self.countries.value):
            try:
                code = countries.get(entry).alpha2
            except KeyError:
                invalid.append(entry)
                continue
            if code not in whitelist:
                whitelist.append(code)

        self.wizard.whitelist = whitelist
        if invalid:
            self.wizard.notice = (
                f'⚠️ Couldn\'t find these countries, so they were left out: {_shorten(invalid)}\n' +
                '-# Country codes are listed [here](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)'
            )


class BlacklistModal(WizardModal):
    """Edit the osu! user blacklist as text"""

    def __init__(self, wizard: SetupWizard):
        """
        Parameters
        ----------
        wizard (SetupWizard): The wizard the modal belongs to
        """

        super().__init__(wizard, title='Blacklist')
        self.users = discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            default=wizard.blacklist_text(),
            placeholder='peppy, 2',
            required=False,
            max_length=MAX_INPUT_LENGTH
        )
        self.add_item(discord.ui.Label(
            text='osu! users',
            description='Usernames or user IDs, separated by commas',
            component=self.users
        ))

    async def apply(self, interaction: discord.Interaction):
        """
        Replace the blacklist with the osu! users entered, looking up the ones that aren't known yet

        Parameters
        ----------
        interaction (discord.Interaction): The modal submit interaction
        """

        # Looking up many users can take longer than Discord waits for a response
        await interaction.response.defer()

        known = {name.lower(): user_id for user_id, name in self.wizard.usernames.items()}
        blacklist, invalid, failed = [], [], []
        for entry in _split_entries(self.users.value):
            # Keep blacklisted IDs without looking them up, as restricted or deleted accounts can't be looked up
            if entry.isdigit() and int(entry) in self.wizard.blacklist:
                user_id = int(entry)
            elif entry.lower() in known:
                user_id = known[entry.lower()]
            else:
                try:
                    user = await OsuApi.get_user(entry, Gamemode.from_name('standard'))
                except aiohttp.ClientError:
                    failed.append(entry)
                    continue
                if not user:
                    invalid.append(entry)
                    continue
                user_id = user['id']
                self.wizard.usernames[user_id] = user['username']
                known[user['username'].lower()] = user_id

            if user_id not in blacklist:
                blacklist.append(user_id)

        self.wizard.blacklist = blacklist
        notices = []
        if invalid:
            notices.append(f'⚠️ Couldn\'t find these osu! users, so they were left out: {_shorten(invalid)}')
        if failed:
            notices.append(f'⚠️ Couldn\'t reach osu! to look up these users, so they were left out: {_shorten(failed)}')
        self.wizard.notice = '\n'.join(notices) or None
