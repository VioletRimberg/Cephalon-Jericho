# This imports discord side api
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
import random
import httpx
import urllib.parse
from os import environ
from warframe import WarframeAPI
from dotenv import load_dotenv 

load_dotenv()

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# This is the Token and Server ID
TOKEN = environ.get("DISCORD_TOKEN")
GUILD_ID = int (environ.get("GUILD_ID"))
CLAN = environ.get("CLAN_NAME")
REPORT_CH = int (environ.get("REPORT_CH"))
WARFRAME_API = WarframeAPI()


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Logged in as {client.user}!")


@tree.command(
    name="hello", description="A simple hello function", guild=discord.Object(GUILD_ID)
)
async def hello(ctx):
    await ctx.response.send_message(
        f"Cephalon Jericho online. Precepts operational. Input command, Operator {ctx.user.display_name}?"
    )


@tree.command(name="koumei", description="Roll a dice", guild=discord.Object(GUILD_ID))
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
    guild=discord.Object(GUILD_ID),
)
async def profile(ctx: discord.Interaction, username: str):
    # Clean the username to lower case and remove spaces
    username = username.lower().replace(" ", "")
    # Create a placeholder message to show that we are looking up the operator
    await ctx.response.send_message(f"I'm looking up operator: `{username}` ...", ephemeral=True) 
    # Make a request to the Warframe API to get the profile of the operator
    profile = await WARFRAME_API.get_profile(username)
    if profile:
        if profile.clan == CLAN:
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

#Writing a report Modal
class ReportModal(ui.Modal, title='Cephalon Jericho awaits your report...'):
    title = ui.TextInput(label='Report Title', required=False, placeholder="Give your report a title")
    message = ui.TextInput(label='Report Summery', style=discord.TextStyle.paragraph, placeholder="Input your report summery here")

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(REPORT_CH)
        interaction.user = interaction.user
        embed = discord.Embed(title="New Report", description=self.message.value, colour=discord.Colour.yellow())
        embed.set_author(name=interaction.user.nick)
        channel.send(embed=embed)
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Redirection precepts nominal, I appreciate your submission Operator!', ephemeral=True)
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Redirection precepts nominal, I appreciate your submission Operator!', ephemeral=True)

@tree.command(name="report", description="Task Cephalon Jericho with sending a report", guild=discord.Object(GUILD_ID))
async def feedback_command(interaction: discord.Interaction):
    modal = ReportModal()
    await interaction.response.send_modal(modal)

client.run(TOKEN)
