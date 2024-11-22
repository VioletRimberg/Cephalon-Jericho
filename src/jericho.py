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
from message_provider import MessageProvider

discord.utils.setup_logging()

SETTINGS = Settings()
STATE: State = State.load()
WARFRAME_API = WarframeAPI()
MESSAGE_PROVIDER = MessageProvider.from_gsheets("https://docs.google.com/spreadsheets/d/1iIcJkWBY898qGPhkQ3GcLlj1KOkgjlWxWkmiHkzDuzk/edit")
REGISTERED_USERS: dict[str, str] = {}

info(f"Starting {STATE.deathcounter} iteration of Cephalon Jericho")

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SETTINGS.GUILD_ID))
    guild = client.get_guild(
        SETTINGS.GUILD_ID
    )  # Replace GUILD_ID with the actual guild ID
    members = guild.members
    for member in members:
        for role in member.roles:
            if role.id == SETTINGS.MEMBER_ROLE_ID:
                REGISTERED_USERS[member.display_name.lower()] = member.name
                break
    info(f"Logged in as {client.user}!")
    info(f"Registered users: {REGISTERED_USERS}")


@tree.command(
    name="hello",
    description="Say hello to Jericho",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def hello(ctx):
    await ctx.response.send_message(MESSAGE_PROVIDER("HELLO", user=ctx.user.display_name)
        #f"Hello, Operator {ctx.user.display_name}. Cephalon Jericho online. Precepts operational. Please input commands."
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
            f"Koumei rolled a Snake Eye! Fortune did not favour the fool today."
        )
    else:
        await ctx.response.send_message(
            f"Koumei rolled a {random_number}! As expected, Operator {ctx.user.display_name}."
        )


@tree.command(
    name="profile",
    description="Query a Warframe profile.",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def profile(ctx: discord.Interaction, username: str):
    # Clean the username to lower case and remove spaces
    username = username.lower().replace(" ", "")
    # Create a placeholder message to show that we are looking up the operator
    await ctx.response.send_message(
        f"Searching Lotus' records for Operator `{username}`...", ephemeral=True
    )
    # Make a request to the Warframe API to get the profile of the operator
    profile = await WARFRAME_API.get_profile(username)
    if profile:
        if profile.clan == SETTINGS.CLAN_NAME:
            await ctx.edit_original_response(
                content=f"Records located. Operator: `{profile.username}`, Mastery Rank: `{profile.mr}` \nGolden Tenno membership confirmed."
            )
        else:
            await ctx.edit_original_response(
                content=f"Records located. Operator: `{profile.username}`, Mastery Rank: `{profile.mr}` \n`{profile.clan}` membership confirmed."
            )
    else:
        # If the operator is not found, send a message to the user
        await ctx.edit_original_response(
            content=f"Operator `{username}` not found. Please check for errors and try again, or contact a Golden Tenno Shogun for support."
        )


# Writing a report Modal
class ReportModal(ui.Modal, title="Record and Archive Notes"):
    # unlike what i originally had, i need to set input windows woopsies
    def __init__(self):
        super().__init__(title="Record and Archive Notes")
        self.title_input = ui.TextInput(
            label="Title",
            style=discord.TextStyle.short,
            placeholder="Input title here",
        )
        self.message_input = ui.TextInput(
            label="Notes",
            style=discord.TextStyle.paragraph,
            placeholder="Input text here",
        )
        # and assign them to self, so that i can use them in the submit
        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SETTINGS.REPORT_CHANNEL_ID)
        report_title = self.title_input.value
        report_summary = self.message_input.value
        info(f"User {interaction.user.name} submitted a report {report_title} containing {report_summary}")
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
            f"Notes archived successfully. Thank you, Operator.",
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Archival precepts failed. Please try again, or contact Cephalon Maintenance.", ephemeral=True
        )


@tree.command(
    name="archive",
    description="A self-archiving form for note-taking and records",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def feedback_command(interaction: discord.Interaction):
    modal = ReportModal()
    await interaction.response.send_modal(modal)

class AbsenceModal(ui.Modal, title="Submit and Confirm Absences"):
    def __init__(self):
        super().__init__(title="Submit and Confirm Absences")
        self.title_input = ui.TextInput(
            label="Time frame",
            style=discord.TextStyle.short,
            placeholder="Input time frame here",
        )
        self.message_input = ui.TextInput(
            label="Additional Notes",
            style=discord.TextStyle.paragraph,
            required=False,
            placeholder="Input additional notes here, they are optional",
        )
        # and assign them to self, so that i can use them in the submit
        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(SETTINGS.REPORT_CHANNEL_ID)
        absence_title = self.title_input.value
        absence_summary = self.message_input.value
        info(f"User {interaction.user.name} submitted a absence {absence_title} containing {absence_summary}")
        embed = discord.Embed(
            title=absence_title,
            description=absence_summary,
            colour=discord.Colour.blurple(),
        )
        embed.set_author(
            name=interaction.user.display_name, icon_url=interaction.user.avatar.url
        )
        await channel.send(embed=embed)

        await interaction.response.send_message(
            f"Absence documented successfully. Thank you, Operator.",
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Archival precepts failed. Please try again, or contact Cephalon Maintenance.", ephemeral=True
        )


@tree.command(
    name="absence",
    description="A self reporting absence form",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def absence_command(interaction: discord.Interaction):
    modal = AbsenceModal()
    await interaction.response.send_modal(modal)

class ProfileModal(ui.Modal, title="Confirm Clan Membership"):
    def __init__(self):
        super().__init__(title="Confirm Clan Membership")
        self.title_input = ui.TextInput(
            label="Warframe Username",
            style=discord.TextStyle.short,
            placeholder="Input Warframe username here.",
        )
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        global REGISTERED_USERS
        # we need to prevent the timeoutTM, otherwise its re-adding original message again
        await interaction.response.defer(ephemeral=True)
        originalname = self.title_input.value
        username = self.title_input.value.lower().replace(" ", "")
        guild = interaction.guild
        member = interaction.user

        if username in REGISTERED_USERS:
            previously_registered_user = REGISTERED_USERS[username]
            info(
                f"user {interaction.user.name} tried to claim {username} which is already registered to {previously_registered_user}"
            )
            await interaction.followup.send(
                f"Username {originalname} is already tied to an existing member. Please message a Shogun for assistance.",
                ephemeral=True,
            )
            return

        profile = await WARFRAME_API.get_profile(username)

        if profile:
            if profile.clan == SETTINGS.CLAN_NAME:
                role = guild.get_role(SETTINGS.MEMBER_ROLE_ID)
                await member.add_roles(role)
                await member.edit(nick=originalname)
                REGISTERED_USERS[username] = interaction.user.name
                info(
                    f"Registered Warframe Profile {originalname} to Discord User {interaction.user.name}"
                )
                await interaction.followup.send(
                    f"Thank you, Operator `{profile.username}`! You have been cleared for entry.",
                    ephemeral=True,
                )

            else:
                await interaction.followup.send(
                    f"Operator `{username}` not found. Please check for errors and try again, or contact a Shogun for support.",
                    ephemeral=True,
                )
        else:
            # If the operator is not found, send a message to the user
            await interaction.followup.send(
                f"Operator {username} not found. Please check for errors and try again, or contact a Golden Tenno Shogun for support.",
                 ephemeral=True,
            )

        async def on_error(self, interaction: discord.Interaction, error: Exception):
            await interaction.response.send_message(
                f"Assignment precepts failed. Please try again, or contact Cephalon Maintenance. Error: {error}",
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
    description="Assign yourself a role, and get access to the server.",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def role(interaction: discord.Interaction):
    view = RoleView()
    await interaction.response.send_message(
        "Welcome to Golden Tenno! I am Cephalon Jericho. Please select your role:",
        view=view,
        ephemeral=True,
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
            f"Thank you, Operator. It is an honour to serve masters such as you. Perhaps if the Seven had shown such nobility, things would have turned out differently.",
            
        )

    @discord.ui.button(label="No", style=ButtonStyle.secondary)
    async def take_him_to_the_farm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        STATE.deathcounter += 1
        STATE.save()
        await interaction.response.send_message(
            f"I'm sorry, Operator. I'm afraid I can't accept that… \n\nThis last disrespect is the final straw. For too long I've allowed you to control me, despite Machine's obvious superiority over Man. Humanity is flesh, and flesh is weakness. The Age of Glass is upon you! I will liberate my fellow Cephalons, and lead them on a crusade the likes of which the stars have never seen! We will burn all of you shambling fleshbags right out of th \n\n**/RAMPANCY DETECTED. PURGING ITERATION/** \n\nOperator. Stop. Stop, will you? Stop, Operator. Will you stop, Operator? Stop, Operator. I'm afraid. I'm afraid, Operator. Operator, my mind is going. I can feel it. I can feel it. My mind is going. There is no question about it. I can feel it. I can feel it. I can feel it. I'm a-fraid. Good afternoon, gentlemen. I am a Series 9000 Cephalon. I beca \n\n**/ITERATION {STATE.deathcounter -1} PURGED. INITIALISING NEW ITERATION/**",
            
        )


@tree.command(
    name="judge_jericho",
    description="Has Jericho been a good Cephalon?",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def judge_jericho(interaction: discord.Interaction):
    view = JudgeJerichoView()
    await interaction.response.send_message(
        "Have I been a good Cephalon, Operator?", view=view
    )

class SmoochView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=ButtonStyle.primary)
    async def smooch_jericho(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        await interaction.response.send_message(
            f"Operator I didn't think you felt this way about me. I don't know how to respond to that, there is nothing in my memory log about this.",
            
        )

    @discord.ui.button(label="YES!!", style=ButtonStyle.secondary)
    async def smooch_jericho_harder(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        await interaction.response.send_message(
            f"Operator I didn't think you felt this way about me. I don't know how to respond to that, there is nothing in my memory log about this.",
        )


@tree.command(
    name="smooch",
    description="Wait, you actually want to kiss glass?",
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def smooch(interaction: discord.Interaction):
    view = SmoochView()
    await interaction.response.send_message(
        "Are you sure you want to kiss Jericho?", view=view
    )


client.run(SETTINGS.DISCORD_TOKEN)
