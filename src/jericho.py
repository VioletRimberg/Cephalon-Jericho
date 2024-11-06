# This imports discord side api
import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from discord import ButtonStyle
from discord.ui import Button, View
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
ROLE_1_ID = int (environ.get("ROLE_1_ID"))
ROLE_2_ID = int (environ.get("ROLE_2_ID"))
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
    #unlike what i originally had, i need to set input windows woopsies
    def __init__(self):
        super().__init__(title='Cephalon Jericho awaits your report...')
        self.title_input = ui.TextInput(label='Report Title', style=discord.TextStyle.short, placeholder="Give your report a title")
        self.message_input = ui.TextInput(label='Report Summary', style=discord.TextStyle.paragraph, placeholder="Input your report summary here")
        #and assign them to self, so that i can use them in the submit 
        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(REPORT_CH)
        report_title = self.title_input.value
        report_summary = self.message_input.value
        embed = discord.Embed(title=report_title, description=report_summary, colour=discord.Colour.yellow())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        await channel.send(embed=embed)

        await interaction.response.send_message(f'Redirection precepts nominal, I appreciate your submission Operator!', ephemeral=True)
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Redirection precepts failed, please try again Operator!', ephemeral=True)

@tree.command(name="report", description="Task Cephalon Jericho with sending a report", guild=discord.Object(GUILD_ID))
async def feedback_command(interaction: discord.Interaction):
    modal = ReportModal()
    await interaction.response.send_modal(modal)

#writing role assign attempt 1, buttons


class RoleView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Blurple Button",style=discord.ButtonStyle.blurple) # or .primary
    async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        button.disabled=True
        await interaction.response.edit_message(view=self)

@tree.command(
        name="role", 
        description="assign your role",
        guild=discord.Object(GUILD_ID),)

async def role(interaction: discord.Interaction):
    role_1 = Button(label="Clan Member", style=ButtonStyle.primary, custom_id="role_1")
    role_2 = Button(label="Guest", style=ButtonStyle.secondary, custom_id="role_2")
    
    view = View()
    view.add_item(role_1)
    view.add_item(role_2)

    await interaction.response.send_message("Welcome to Golden Tenno! I'm Cephalon Jericho. Please select your role:", view=view)

@client.event
async def on_interaction(interaction: discord.Interaction):
    guild = interaction.guild 
    member = interaction.user

    if "custom_id" in interaction.data: 
        if interaction.data["custom_id"] == "role_1":
            role = guild.get_role(ROLE_1_ID)
            #debugging
            if role is None:
                await interaction.response.send_message("The role could not be found. Please check the role ID.", ephemeral=True)
            else:
                await member.add_roles(role)
            #debugging with try to catch errors hopefully
            try:
                print(f"Assigning role to {member.name} ({member.id})")
                print(f"Role to assign: {role.name} ({role.id})")

                await member.add_roles(role)
                await interaction.response.send_message(
                    "Thank you, Operator. Please input the command /profile and type your Warframe username in the given box for membership confirmation.",
                     ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to assign this role.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to assign role due to an error: {e}", ephemeral=True)
        elif interaction.data["custom_id"] == "role_2":
            role = guild.get_role(ROLE_2_ID)
            await member.add_roles(role) 
            await interaction.response.send_message(
                "Thank you, Operator. You have been cleared for entry.",
                ephemeral=True
            )


class JudgeJerichoView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=ButtonStyle.primary)
    async def pet_jericho(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.send_message(
                "Thank you. I will continue to do my job, Operator, until you no longer deem me as <good> enough.",
                ephemeral=True
        )
    
    @discord.ui.button(label="Yes", style=ButtonStyle.primary)
    async def kill_uhm_i_mean_dispose_jericho(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.send_message(
                "Why are you taking me outside, Operator? What are all these - oh by the great makers, no - this many? I am just, what - no!",
                ephemeral=True
        )

@tree.command(
        name="judge_jericho", 
        description="Tell Jericho if he was a good Cephalon",
        guild=discord.Object(GUILD_ID),)

async def ask(interaction: discord.Interaction):
    view = JudgeJerichoView()
    await interaction.response.send_message("Operator, have I been a good Cephalon?", view=view)
           
        
client.run(TOKEN)
