from discord import User, Interaction, TextStyle, SelectOption, ButtonStyle, Forbidden
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
    def __init__(self, user: User, clan: Clan, wf_name: str, dm_failed: bool = False):
        super().__init__(label="Decline")
        self.user = user
        self.clan = clan
        self.wf_name = wf_name
        self.dm_failed = dm_failed  # Store DM failure status

    async def _callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=False)
        

        try:
            await self.user.send(content=MESSAGE_PROVIDER("ROLE_DECLINE_USER"))
        except Forbidden:
            pass
                

        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER(
                "ROLE_DECLINE_BACKEND",
                user=self.user.mention,
                clan=self.clan.name,
                wfname=self.wf_name,
                interactionuser=interaction.user.mention,
            ),
            view=None,
        )


class RoleAssignButton(ErrorHandlingButton):
    def __init__(self, user: User, role: Role, clan: Clan, wf_name: str, dm_failed: bool = False):
        super().__init__(label=role.name, style=ButtonStyle.primary)
        self.user = user
        self.role = role
        self.clan = clan
        self.wf_name = wf_name
        self.dm_failed = dm_failed  # Store DM failure status

    async def _callback(self, interaction: Interaction):
        await interaction.response.defer(thinking=False)
        guild = interaction.guild
        member = guild.get_member(self.user.id) 

        if not member:
            await interaction.followup.send(
                MESSAGE_PROVIDER("ROLE_ASSIGN_FAILED", user=self.user.mention),
                ephemeral=True,
            )
            return

        # Assign new role(s)
        for role_id in self.role.ids:
            guild_role = guild.get_role(role_id)
            if guild_role:
                try:
                    await member.add_roles(guild_role)
                except Forbidden:
                    await interaction.followup.send(
                        MESSAGE_PROVIDER("ROLE_ASSIGN_FAILED", user=self.user.mention),
                        ephemeral=True,
                    )
                    return

        # Remove the guest role
        guest_role = guild.get_role(SETTINGS.GUEST_ROLE_ID)
        if guest_role and guest_role in member.roles:
            try:
                await member.remove_roles(guest_role)
            except Forbidden:
                await interaction.followup.send(
                    MESSAGE_PROVIDER("ROLE_REMOVE_FAILED", user=self.user.mention),
                    ephemeral=True,
                )

        # Send DM confirmation
        try:
            await member.send(
                MESSAGE_PROVIDER(
                    "ROLE_ACCEPT_USER",
                    role=self.role.name,
                    clan=self.clan.name,
                    wfname=self.wf_name,
                )
            )
        except Forbidden:
            pass  #DM failed, catching 403

        # Edit the original message
        await interaction.edit_original_response(
            content=MESSAGE_PROVIDER(
                "ROLE_ACCEPT_BACKEND",
                role=self.role.name,
                clan=self.clan.name,
                wfname=self.wf_name,
                user=self.user.mention,
                interactionuser=interaction.user.mention,
            ),
            view=None,
        )


class AssignRoleView(View):
    def __init__(self, user: User, clan: Clan, wf_name: str, dm_failed: bool):
        super().__init__(timeout=None)
        self.assign_buttons = []
        for role in clan.roles:
            button = RoleAssignButton(user, role, clan, wf_name=wf_name, dm_failed=dm_failed)
            self.assign_buttons.append(button)
            self.add_item(button)

        self.decline = RoleDeclineButton(user, clan, wf_name=wf_name, dm_failed=dm_failed)
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
        await interaction.response.defer(ephemeral=True)
        wf_name = self.title_input.value.strip()
        guild = interaction.guild
        channel = guild.get_channel(self.clan.channel)
        member = interaction.user

        if not wf_name:
            await interaction.edit_original_response(
                content=MESSAGE_PROVIDER("ROLE_NOT_FOUND", user=wf_name),
                view=None,
            )
            return
        
        dm_failed = False
        try:
            await interaction.user.send(MESSAGE_PROVIDER("ROLE_REGISTERED", user=wf_name))
        except Forbidden:
            dm_failed = True  # Track that DM failed
            print(f"User {member.display_name} has DMs disabled.")

        await channel.send(
            content=MESSAGE_PROVIDER(
                "ROLE_CLAIM_DM_FAILED" if dm_failed else "ROLE_CLAIM",
                member=member.mention,
                clan=self.clan.name,
                wfname=wf_name,
            ),
            view=AssignRoleView(user=member, clan=self.clan, wf_name=wf_name, dm_failed=dm_failed),
        )

        # Assign guest role in the meantime
        role = guild.get_role(SETTINGS.GUEST_ROLE_ID)
        await member.add_roles(role)

        await interaction.edit_original_response(
        content=MESSAGE_PROVIDER("ROLE_REGISTERED", user=wf_name),
        view=None
        )

    async def on_error(self, interaction: Interaction, error: Exception):
        print(f"Unexpected error in ProfileModal: {repr(error)}")
        if interaction.response.is_done():
            await interaction.followup.send(
                MESSAGE_PROVIDER("ROLE_ERROR", error=error), ephemeral=True
            )
        else:
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
                clan = next(c for c in SETTINGS.CLANS if c.name == selection)
                await interaction.response.send_modal(ProfileModal(clan))
        except Exception as e:
            await interaction.response.send_message(
                MESSAGE_PROVIDER("ROLE_ERROR", error=e), ephemeral=True
            )


class RoleView(View):
    def __init__(self):
        super().__init__()
        self.add_item(ClanDropdown())