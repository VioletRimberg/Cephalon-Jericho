from discord import User, Interaction, TextStyle, SelectOption, ButtonStyle
from discord.ui import Button, TextInput, Select, View, Modal
from settings import Clan, Role
from constants import SETTINGS, MESSAGE_PROVIDER


class ErrorHandlingButton(Button):
    async def _callback(self, interaction: Interaction):
        raise NotImplementedError

    async def callback(self, interaction: Interaction):
        try:
            await self._callback(interaction)
        except Exception as e:
            await interaction.edit_original_response(
                content=MESSAGE_PROVIDER("ROLE_ERROR", error=e), view=None
            )


class RoleDeclineButton(ErrorHandlingButton):
    def __init__(self, user: User, clan: Clan, wf_name: str):
        super().__init__(label="Decline")
        self.user = user
        self.clan = clan
        self.wf_name = wf_name

    async def _callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=False)
        await self.user.send(content=MESSAGE_PROVIDER("ROLE_DECLINE_USER"))
        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER("ROLE_DECLINE_BACKEND", 
                                     user = self.user.mention, 
                                     clan = self.clan.name, 
                                     wfname = self.wf_name, 
                                     interactionuser = interaction.user.mention),
            view=None,
        )


class RoleAssignButton(ErrorHandlingButton):
    def __init__(self, user: User, role: Role, clan: Clan, wf_name: str):
        super().__init__(label=role.name, style=ButtonStyle.primary)
        self.user = user
        self.role = role
        self.clan = clan
        self.wf_name = wf_name

    async def _callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=False)

        guild = interaction.guild
        for role_id in self.role.ids:
            guild_role = guild.get_role(role_id)
            if guild_role:
                await self.user.add_roles(guild_role)

        await self.user.send(
            content=MESSAGE_PROVIDER("ROLE_ACCEPT_USER", 
                                     role = self.role.name, 
                                     clan = self.clan.name, 
                                     wfname = self.wf_name)
        )

        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER("ROLE_ACCEPT_BACKEND", 
                                     role = self.role.name, 
                                     clan = self.clan.name, 
                                     wfname = self.wf_name,
                                     user = self.user.mention,
                                     interactionuser = interaction.user.mention),
            view=None,
        )


class AssignRoleView(View):
    def __init__(self, user: User, clan: Clan, wf_name: str):
        super().__init__(timeout=None)
        self.assign_buttons = []
        for role in clan.roles:
            button = RoleAssignButton(user, role, clan, wf_name=wf_name)
            self.assign_buttons.append(button)
            self.add_item(button)

        self.decline = RoleDeclineButton(user, clan, wf_name=wf_name)
        self.add_item(self.decline)


class ProfileModal(Modal, title="Confirm Clan Membership"):
    def __init__(self, clan: Clan):
        super().__init__(title="Confirm Clan Membership")
        self.clan = clan
        self.title_input = TextInput(
            label="Warframe Username",
            style=TextStyle.short,
            placeholder="Input Warframe username here.",
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: Interaction):
        # we need to prevent the timeoutTM, otherwise its re-adding original message again
        await interaction.response.defer(ephemeral=True)
        wf_name = self.title_input.value.strip()
        guild = interaction.guild
        channel = guild.get_channel(SETTINGS.REPORT_CHANNEL_ID)
        member = interaction.user

        if not wf_name or len(wf_name) == 0:
            await interaction.edit_original_response(
                content=MESSAGE_PROVIDER("ROLE_NOT_FOUND", user=wf_name),
                view=None,
            )
            return

        await channel.send(
            content= MESSAGE_PROVIDER("ROLE_CLAIM", member = member.mention, clan = self.clan.name, wfname = wf_name),
            view=AssignRoleView(user=member, clan=self.clan, wf_name=wf_name),
        )

        # assign guest in the meantime
        role = guild.get_role(SETTINGS.GUEST_ROLE_ID)
        await member.add_roles(role)

        # Send message to user
        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER("ROLE_REGISTERED", user=wf_name), view=None
        )

    async def on_error(self, interaction: Interaction, error: Exception):
        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER("ROLE_ERROR", error=error), view=None
        )


class ClanDropdown(Select):
    def __init__(self):
        options = []
        for clan in SETTINGS.CLANS:
            options.append(
                SelectOption(
                    label=clan.name, value=clan.name, description=clan.description
                )
            )
        options.append(
            SelectOption(
                label=SETTINGS.GUEST_NAME,
                value=SETTINGS.GUEST_NAME,
                description=MESSAGE_PROVIDER("ROLE_JOIN_GUEST"),
            )
        )
        super().__init__(
            placeholder="Choose your Clan", options=options, min_values=1, max_values=1
        )

    async def callback(self, interaction: Interaction):
        try:
            selection = self.values[0]
            if selection == SETTINGS.GUEST_NAME:
                guild = interaction.guild
                role = guild.get_role(SETTINGS.GUEST_ROLE_ID)
                member = interaction.user
                await member.add_roles(role)
                await interaction.response.edit_message(
                    content=MESSAGE_PROVIDER("ROLE_GUEST"), view=None
                )
            else:
                clan = [c for c in SETTINGS.CLANS if c.name == selection][0]
                modal = ProfileModal(clan)
                await interaction.response.send_modal(modal)

        except Exception as e:
            await interaction.response.send_message(
                MESSAGE_PROVIDER("ROLE_ERROR", error=e), ephemeral=True
            )


class RoleView(View):
    def __init__(self):
        super().__init__()
        self.add_item(ClanDropdown())
