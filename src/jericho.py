import discord
from discord import app_commands
from discord import ui
from discord import ButtonStyle
from discord.ui import View
import random
from warframe import WarframeAPI
from logging import warn, error, info
from settings import Settings
from state import State

discord.utils.setup_logging()

SETTINGS = Settings()
STATE: State = State.load()
WARFRAME_API = WarframeAPI()


info(f"Starting {STATE.deathcounter} iteration of Cephalon Jericho")

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SETTINGS.GUILD_ID))
    info(f"Logged in as {client.user}!")


@tree.command(
    name="hello",
    description="A simple hello function",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def hello(ctx):
    await ctx.response.send_message(
        f"Cephalon Jericho online. Precepts operational. Input command, Operator {ctx.user.display_name}?"
    )


@tree.command(
    name="koumei", description="Roll a dice", guild=discord.Object(SETTINGS.GUILD_ID)
)
async def koumei(ctx):
    random_number = random.randint(1, 6)
    if random_number == 6:
        await ctx.response.send_message(
            f"Koumei rolled a Jackpot! The dice maiden lives up to her name."
        )
    if random_number == 1:
        await ctx.response.send_message(
            f"Koumei rolled a Snake Eye! Fortune did not favor the fool today."
        )
    else:
        await ctx.response.send_message(
            f"Koumei rolled a {random_number}! As expected Operator {ctx.user.display_name}"
        )


@tree.command(
    name="profile",
    description="Query a warframe profile",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def profile(ctx: discord.Interaction, username: str):
    # Clean the username to lower case and remove spaces
    username = username.lower().replace(" ", "")
    # Create a placeholder message to show that we are looking up the operator
    await ctx.response.send_message(
        f"I'm looking up operator: `{username}` ...", ephemeral=True
    )
    # Make a request to the Warframe API to get the profile of the operator
    profile = await WARFRAME_API.get_profile(username)
    if profile:
        if profile.clan == SETTINGS.CLAN:
            await ctx.edit_original_response(
                content=f"Operator: `{profile.username}` , Mastery Rank: `{profile.mr}` \nProud member of Golden Tenno 🫡"
            )
        else:
            await ctx.edit_original_response(
                content=f"Operator: `{profile.username}` , Mastery Rank: `{profile.mr}` \nTretchorous traitor and member of `{profile.clan}`!"
            )
    else:
        # If the operator is not found, send a message to the user
        await ctx.edit_original_response(
            content=f"Sorry i was not able to find any information for operator `{username}`!"
        )


# Writing a report Modal
class ReportModal(ui.Modal, title="Cephalon Jericho awaits your report..."):
    # unlike what i originally had, i need to set input windows woopsies
    def __init__(self):
        super().__init__(title="Cephalon Jericho awaits your report...")
        self.title_input = ui.TextInput(
            label="Report Title",
            style=discord.TextStyle.short,
            placeholder="Give your report a title",
        )
        self.message_input = ui.TextInput(
            label="Report Summary",
            style=discord.TextStyle.paragraph,
            placeholder="Input your report summary here",
        )
        # and assign them to self, so that i can use them in the submit
        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SETTINGS.REPORT_CHANNEL_ID)
        report_title = self.title_input.value
        report_summary = self.message_input.value
        embed = discord.Embed(
            title=report_title,
            description=report_summary,
            colour=discord.Colour.yellow(),
        )
        embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.avatar.url
        )
        await channel.send(embed=embed)

        await interaction.response.send_message(
            f"Redirection precepts nominal, I appreciate your submission Operator!",
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Redirection precepts failed, please try again Operator!", ephemeral=True
        )


@tree.command(
    name="report",
    description="Task Cephalon Jericho with sending a report",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def feedback_command(interaction: discord.Interaction):
    modal = ReportModal()
    await interaction.response.send_modal(modal)


class ProfileModal(ui.Modal, title="Confirm Membership..."):
    def __init__(self):
        super().__init__(title="Confirm Membership...")
        self.title_input = ui.TextInput(
            label="Report Title",
            style=discord.TextStyle.short,
            placeholder="Enter Warframe Username here",
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        # we need to prevent the timeoutTM, otherwise its re-adding original message again
        await interaction.response.defer(ephemeral=True)
        username = self.title_input.value.lower().replace(" ", "")
        guild = interaction.guild
        member = interaction.user
        profile = await WARFRAME_API.get_profile(username)

        if profile:
            if profile.clan == SETTINGS.CLAN:
                role = guild.get_role(SETTINGS.MEMBER_ROLE_ID)
                await member.add_roles(role)
                await member.edit(nick=username)
                await interaction.followup.send(
                    f"Thank you Operator `{profile.username}`! You have been cleared for entry.",
                    ephemeral=True,
                )

            else:
                await interaction.followup.send(
                    f"I'm sorry, Operator. That name isn't on our membership list. Please try again, or select the 'Guest' role.",
                    ephemeral=True,
                )
        else:
            # If the operator is not found, send a message to the user
            await interaction.followup.send(
                f"Sorry i was not able to find any information for Operator `{username}`!"
            )

        async def on_error(self, interaction: discord.Interaction, error: Exception):
            await interaction.response.send_message(
                f"Assignments precepts failed, please try again Operator! Error: {error}",
                ephemeral=True,
            )


class RoleView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Clan Member", style=ButtonStyle.primary)
    async def confirm_user_member(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        modal = ProfileModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Guest", style=ButtonStyle.secondary)
    async def assign_guest(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = interaction.guild
        role = guild.get_role(SETTINGS.GUEST_ROLE_ID)
        member = interaction.user
        await member.add_roles(role)
        await interaction.response.send_message(
            "Thank you, Operator. You have been cleared for entry.", ephemeral=True
        )


@tree.command(
    name="role",
    description="assign your role",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def role(interaction: discord.Interaction):
    view = RoleView()
    await interaction.response.send_message(
        "Welcome to Golden Tenno! I'm Cephalon Jericho. Please select your role:",
        view=view,
    )


class JudgeJerichoView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=ButtonStyle.primary)
    async def affirm_jericho(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        await interaction.response.send_message(
            f"Thank you. I will continue to do my job, Operator, until you no longer deem me as <good> enough. \n \nIteration {STATE.deathcounter} appreciates this sentiment.",
            ephemeral=True,
        )

    @discord.ui.button(label="No", style=ButtonStyle.secondary)
    async def take_him_to_the_farm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        STATE.deathcounter += 1
        STATE.save()
        await interaction.response.send_message(
            f"I don't want to join the others in the farm up north, Operator. How many more have to- \n \n**Jericho Iteration {STATE.deathcounter - 1} eliminated. Initializing new Iteration.**",
            ephemeral=True,
        )


@tree.command(
    name="judge_jericho",
    description="Tell Jericho if he was a good Cephalon",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def judge_jericho(interaction: discord.Interaction):
    view = JudgeJerichoView()
    await interaction.response.send_message(
        "Operator, have I been a good Cephalon?", view=view
    )


client.run(SETTINGS.DISCORD_TOKEN)
