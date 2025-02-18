import discord
import time
from discord import app_commands
from discord import ui
from discord import ButtonStyle
from discord.ui import View
from discord.app_commands import Choice
from discord import Interaction
from discord.utils import get
import random
from warframe import WarframeAPI
from logging import info
from settings import Settings
from state import State
from message_provider import MessageProvider
from sources import WeaponLookup, WarframeWiki, RivenRecommendationProvider

discord.utils.setup_logging()

SETTINGS = Settings()
STATE: State = State.load()
WARFRAME_API = WarframeAPI()
MESSAGE_PROVIDER = MessageProvider.from_gsheets(SETTINGS.MESSAGE_PROVIDER_URL)
REGISTERED_USERS: dict[str, str] = {}
WEAPON_LOOKUP = WeaponLookup()
WARFRAME_WIKI = WarframeWiki(weapon_lookup=WEAPON_LOOKUP)
RIVEN_PROVIDER = RivenRecommendationProvider()


info(f"Starting {STATE.deathcounter} iteration of Cephalon Jericho")

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

async def refresh():
    global WEAPON_LOOKUP
    global WARFRAME_WIKI
    global RIVEN_PROVIDER

    info("Refreshing Data...")
    WEAPON_LOOKUP = WeaponLookup()
    WARFRAME_WIKI = WarframeWiki(weapon_lookup=WEAPON_LOOKUP)
    await WARFRAME_WIKI.refresh()
    RIVEN_PROVIDER = RivenRecommendationProvider()
    await RIVEN_PROVIDER.refresh(WEAPON_LOOKUP, force_download=True)
    await WARFRAME_API.get_median_prices(WEAPON_LOOKUP)
    WEAPON_LOOKUP.rebuild_weapon_relations()
    info("Data Refreshed!")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=SETTINGS.GUILD_ID))
    guild = client.get_guild(SETTINGS.GUILD_ID)
    members = guild.members
    for member in members:
        for role in member.roles:
            if role.id == SETTINGS.MEMBER_ROLE_ID:
                REGISTERED_USERS[member.display_name.lower()] = member.name
                break

    info(f"Logged in as {client.user}!")
    info(f"Registered users: {REGISTERED_USERS}")

    await refresh()


async def weapon_autocomplete(
    interaction: Interaction, current: str, can_have_rivens: bool = False
):
    matches = WEAPON_LOOKUP.fuzzy_search(current, n=25, can_have_rivens=can_have_rivens)
    choices = [
        Choice(name=weapon.display_name, value=weapon.display_name)
        for weapon in matches
    ]
    return choices


@tree.command(
    name="maintenance_sync_commands",
    description=MESSAGE_PROVIDER("MAINTENANCE_SYNC_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def sync_commands(interaction: discord.Interaction):
    # Acknowledge the interaction quickly with a reply
    if any(role.id == SETTINGS.MAINTENANCE_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message(
            MESSAGE_PROVIDER("MAINTENANCE_SYNC_INI"), ephemeral=True
        )

        try:
            # Perform the sync after acknowledging the interaction
            await tree.sync(guild=discord.Object(id=SETTINGS.GUILD_ID))
            await interaction.followup.send(
                MESSAGE_PROVIDER("MAINTENANCE_SYNC_SUCCESS"), ephemeral=True
            )  # Send follow-up response after sync
        except Exception as e:
            # Handle any potential errors
            await interaction.followup.send(
                MESSAGE_PROVIDER("MAINTENANCE_SYNC_ERROR", error={str(e)}),
                ephemeral=True,
            )
    else:
        await interaction.response.send_message(
            MESSAGE_PROVIDER(
                "MAINTENANCE_SYNC_DENIED", user=interaction.user.display_name
            ),
            ephemeral=True,
        )


@tree.command(
    name="hello",
    description=MESSAGE_PROVIDER("HELLO_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def hello(ctx):
    await ctx.response.send_message(
        MESSAGE_PROVIDER("HELLO", user=ctx.user.display_name)
    )


@tree.command(
    name="tough_love",
    description=MESSAGE_PROVIDER("TOUGH_LOVE_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def tough_love(ctx):
    await ctx.response.send_message(
        MESSAGE_PROVIDER("TOUGH_LOVE", user=ctx.user.display_name)
    )


@tree.command(
    name="feeling_lost",
    description=MESSAGE_PROVIDER("LOST_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def feeling_lost(ctx):
    await ctx.response.send_message(
        MESSAGE_PROVIDER("LOST", user=ctx.user.display_name)
    )


@tree.command(
    name="trivia",
    description=MESSAGE_PROVIDER("TRIVIA_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def trivia(ctx):
    await ctx.response.send_message(
        MESSAGE_PROVIDER("TRIVIA", user=ctx.user.display_name)
    )


@tree.command(
    name="rate_outfit",
    description=MESSAGE_PROVIDER("RATE_OUTFIT_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def rate_outfit(ctx):
    await ctx.response.send_message(
        MESSAGE_PROVIDER("RATE_OUTFIT", user=ctx.user.display_name)
    )

pet_cooldowns = {}
COOLDOWN_TIME = 10

@tree.command(
        name = "pet_jericho",
        description = MESSAGE_PROVIDER("PET_JERICHO_DESC"),
        guild = discord.Object(SETTINGS.GUILD_ID),
)
async def pet_jericho(interaction: discord.Interaction):
        
        user_id = interaction.user.id
        current_time = time.time()

        if user_id in pet_cooldowns:
            elapsed_time = current_time - pet_cooldowns[user_id]
            if elapsed_time < COOLDOWN_TIME:
                remaining_time = int(COOLDOWN_TIME - elapsed_time)
                return await interaction.response.send_message(
                    content=MESSAGE_PROVIDER("PET_JERICHO_TIMEOUT", remainingtime = remaining_time, user = interaction.user.display_name),
                    ephemeral=True 
        )
        pet_cooldowns[user_id] = current_time

        gif_path = "images/Jericho_Pet.gif"
        file = discord.File(gif_path, filename="Jericho_Pet.gif")
        await interaction.response.send_message(content=MESSAGE_PROVIDER("PET_JERICHO", user = interaction.user.display_name), file=file)


@tree.command(
    name="koumei",
    description=MESSAGE_PROVIDER("KOUMEI_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def koumei(ctx):
    random_number = random.randint(1, 6)
    if random_number == 6:
        await ctx.response.send_message(
            MESSAGE_PROVIDER(
                "KOUMEI_JACKPOT", user=ctx.user.display_name, number=random_number
            )
        )
    if random_number == 1:
        await ctx.response.send_message(
            MESSAGE_PROVIDER(
                "KOUMEI_SNAKE", user=ctx.user.display_name, number=random_number
            )
        )
    else:
        await ctx.response.send_message(
            MESSAGE_PROVIDER(
                "KOUMEI_NEUTRAL", user=ctx.user.display_name, number=random_number
            )
        )


@tree.command(
    name="profile",
    description=MESSAGE_PROVIDER("PROFILE_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def profile(ctx: discord.Interaction, username: str):
    # Create a placeholder message to show that we are looking up the operator
    await ctx.response.send_message(
        MESSAGE_PROVIDER("PROFILE_SEARCH", user=username), ephemeral=True
    )
    # Make a request to the Warframe API to get the profile of the operator
    result = await WARFRAME_API.get_profile_all_platforms(username)
    if result:
        profile = result
        if profile.clan == SETTINGS.CLAN_NAME:
            await ctx.edit_original_response(
                content=MESSAGE_PROVIDER(
                    "PROFILE_GT",
                    profile=profile,
                )
            )
        else:
            await ctx.edit_original_response(
                content=MESSAGE_PROVIDER(
                    "PROFILE_OTHER",
                    profile=profile,
                )
            )
    else:
        # If the operator is not found, send a message to the user
        await ctx.edit_original_response(
            content=MESSAGE_PROVIDER("PROFILE_MISSING", user=username)
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
        info(
            f"User {interaction.user.name} submitted a report {report_title} containing {report_summary}"
        )
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
            MESSAGE_PROVIDER("ARCHIVE_SUCCESS"), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            MESSAGE_PROVIDER("ARCHIVE_FAILURE"), ephemeral=True
        )


@tree.command(
    name="archive",
    description=MESSAGE_PROVIDER("ARCHIVE_DESC"),
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
        info(
            f"User {interaction.user.name} submitted a absence {absence_title} containing {absence_summary}"
        )
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
            MESSAGE_PROVIDER("ABSENCE_SUCCESS"), ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            MESSAGE_PROVIDER("ABSENCE_FAIL"), ephemeral=True
        )


@tree.command(
    name="absence",
    description=MESSAGE_PROVIDER("ABSENCE_DESC"),
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
                MESSAGE_PROVIDER("IMPOSTER", originalname=originalname), ephemeral=True
            )

            return

        profile = await WARFRAME_API.get_profile_all_platforms(username)

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
                    MESSAGE_PROVIDER("ROLE_REGISTERED", user=originalname),
                    ephemeral=True,
                )

            else:
                await interaction.followup.send(
                    MESSAGE_PROVIDER("ROLE_NOT_FOUND", user=originalname),
                    ephemeral=True,
                )

        else:
            # If the operator is not found, send a message to the user
            await interaction.followup.send(
                MESSAGE_PROVIDER("ROLE_NOT_FOUND", user=originalname), ephemeral=True
            )

        async def on_error(self, interaction: discord.Interaction, error: Exception):
            await interaction.response.send_message(
                MESSAGE_PROVIDER("ROLE_ERROR", error=error), ephemeral=True
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
            MESSAGE_PROVIDER("ROLE_GUEST"), ephemeral=True
        )


@tree.command(
    name="role",
    description=MESSAGE_PROVIDER("ROLE_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def role(interaction: discord.Interaction):
    view = RoleView()
    await interaction.response.send_message(
        MESSAGE_PROVIDER("ROLE_INIT"),
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
            MESSAGE_PROVIDER("AFFIRM_YES", user=interaction.user.name)
        )

    @discord.ui.button(label="No", style=ButtonStyle.secondary)
    async def take_him_to_the_farm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        STATE.deathcounter += 1
        STATE.save()
        await interaction.response.send_message(
            MESSAGE_PROVIDER("AFFIRM_NO", deathcounter=STATE.deathcounter - 1)
        )


@tree.command(
    name="judge_jericho",
    description=MESSAGE_PROVIDER("JUDGE_JERICHO_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def judge_jericho(interaction: discord.Interaction):
    view = JudgeJerichoView()
    await interaction.response.send_message(MESSAGE_PROVIDER("AFFIRM"), view=view)


class SmoochView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Yes", style=ButtonStyle.primary)
    async def smooch_jericho(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        await interaction.response.send_message(MESSAGE_PROVIDER("SMOOCH_YES"))

    @discord.ui.button(label="YES!!", style=ButtonStyle.secondary)
    async def smooch_jericho_harder(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        global STATE
        await interaction.response.send_message(MESSAGE_PROVIDER("SMOOCH_YES"))


@tree.command(
    name="smooch",
    description=MESSAGE_PROVIDER("SMOOCH_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def smooch(interaction: discord.Interaction):
    view = SmoochView()
    await interaction.response.send_message(MESSAGE_PROVIDER("SMOOCH"), view=view)


@tree.command(
    name="riven_weapon_stats",
    description=MESSAGE_PROVIDER("WEAPON_QUERY_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def weapon_look_up(interaction: discord.Interaction, weapon_name: str):
    """Look up riven stats for a given weapon."""
    if weapon_name not in WEAPON_LOOKUP:
        await interaction.response.send_message(
            MESSAGE_PROVIDER("WEAPON_NOT_FOUND", weaponname=weapon_name), ephemeral=True
        )
        return

    weapon = WEAPON_LOOKUP[weapon_name]
    if not weapon.riven_recommendations:
        await interaction.response.send_message(
            MESSAGE_PROVIDER("WEAPON_NO_RIVEN", weaponname=weapon.display_name),
            ephemeral=True,
        )
        return

    wiki_data = await WARFRAME_WIKI.weapon(weapon.normalized_name)
    if not wiki_data:
        await interaction.response.send_message(
            MESSAGE_PROVIDER("WEAPON_NO_WIKI", weaponname=weapon.display_name),
            ephemeral=True,
        )
        return

    base_weapon = weapon if weapon.is_base_weapon else WEAPON_LOOKUP[weapon.base_weapon]

    weapon_variants = []
    if base_weapon.weapon_variants:
        weapon_variants = [WEAPON_LOOKUP[v] for v in base_weapon.weapon_variants] + [
            base_weapon
        ]

        weapon_variants = sorted(
            weapon_variants, key=lambda w: (len(w.display_name), w.display_name)
        )

    embed = discord.Embed()
    embed.title = weapon.display_name
    embed.url = wiki_data.url
    description = f"**Disposition**: {wiki_data.riven_disposition.symbol} ({wiki_data.riven_disposition.disposition}x)"
    if base_weapon.median_plat_price:
        emoji = get(interaction.guild.emojis, name="plat")
        description += f"\n**Median Price**: {base_weapon.median_plat_price} {emoji if emoji else 'Platinum'}"
    embed.description = description
    embed.set_thumbnail(url=wiki_data.image)

    embed.add_field(
        name="Riven Stats",
        value="",
        inline=False,
    )

    for i, recommendation in enumerate(base_weapon.riven_recommendations.stats):
        if len(base_weapon.riven_recommendations.stats) > 1:
            embed.add_field(
                name=f"Recommendation {i+1}",
                value="",
                inline=False,
            )

        if recommendation.best:
            best_stats = ", ".join(
                [effect.render(wiki_data.mod_type) for effect in recommendation.best]
            )
            embed.add_field(name="Best", value=best_stats, inline=True)

        if recommendation.wanted:
            desired_stats = ", ".join(
                [effect.render(wiki_data.mod_type) for effect in recommendation.wanted]
            )
            embed.add_field(name="Desired", value=desired_stats, inline=True)

        if recommendation.wanted_negatives:
            negative_stats = ", ".join(
                [
                    effect.render(wiki_data.mod_type)
                    for effect in recommendation.wanted_negatives
                ]
            )
            embed.add_field(
                name="Harmless Negatives", value=negative_stats, inline=True
            )

    if len(weapon_variants) > 1:
        weapon_variants_text = ""
        for w in weapon_variants:
            weapon_variants_text += (
                f"- [{w.display_name}]({WARFRAME_WIKI.base_url + w.wiki_url})\n"
            )

        embed.add_field(
            name=f"Weapon Family: {base_weapon.display_name}",
            value=weapon_variants_text,
            inline=False,
        )

    embed.add_field(
        name="",
        value=f"[See on Warframe Market]({base_weapon.get_market_auction_url()})",
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


@weapon_look_up.autocomplete("weapon_name")
async def autocomplete_weapon_name(interaction: Interaction, current: str):
    return await weapon_autocomplete(interaction, current, can_have_rivens=True)


# @tree.command(
#     name="riven_grade",
#     description=MESSAGE_PROVIDER("RIVEN_GRADE_DESC"),
#     guild=discord.Object(SETTINGS.GUILD_ID),
# )
# async def riven_grade(interaction: discord.Interaction, weapon: str, *, stats: str):
#     # Convert the string of stats into a list
#     stats_list = stats.split()

#     weapon = weapon.strip().lower()

#     # Search for the weapon in the RIVEN_PROVIDER data
#     weapon_stats = None
#     for row in RIVEN_PROVIDER.normalized_data:
#         if row["WEAPON"].strip().lower() == weapon:
#             weapon_stats = row
#             break

#     # Validate if the weapon exists
#     if not weapon_stats:
#         await interaction.response.send_message(
#             MESSAGE_PROVIDER("INVALID_RIVEN", weaponname=weapon, stats=stats, user=interaction.user.display_name),
#         )
#         return

#     # Get weapon stats
#     weapon_stats = RIVEN_PROVIDER.get_weapon_stats(weapon)
#     best_stats = weapon_stats["BEST STATS"]
#     desired_stats = weapon_stats["DESIRED STATS"]
#     harmless_negatives = weapon_stats["NEGATIVE STATS"]

#     # Validate input
#     if not stats_list:
#         await interaction.response.send_message(
#             MESSAGE_PROVIDER("INVALID_RIVEN", weapon=weapon, stats=stats),
#             ephemeral=True,
#         )
#         return

#     # Call the grade_riven function with the stats list
#     riven_grade = RIVEN_GRADER.grade_riven(
#         stats_list, best_stats, desired_stats, harmless_negatives
#     )

#     # Determine the response based on the grade
#     if riven_grade == 5:
#         response = MESSAGE_PROVIDER(
#             "PERFECT_RIVEN",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )
#     elif riven_grade == 4:
#         response = MESSAGE_PROVIDER(
#             "PRESTIGIOUS_RIVEN",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )
#     elif riven_grade == 3:
#         response = MESSAGE_PROVIDER(
#             "DECENT_RIVEN",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )
#     elif riven_grade == 2:
#         response = MESSAGE_PROVIDER(
#             "NEUTRAL_RIVEN",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )
#     elif riven_grade == 1:
#         response = MESSAGE_PROVIDER(
#             "UNUSABLE_RIVEN",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )
#     else:
#         response = MESSAGE_PROVIDER(
#             "INVALID_RIVEN_GRADE",
#             user=interaction.user.display_name,
#             stats=stats,
#             weapon=weapon,
#         )

#     # Send the final response
#     await interaction.response.send_message(response)


# @riven_grade.autocomplete("weapon")
# async def autocomplete_weapon_name_for_riven_grade(
#     interaction: Interaction, current: str
# ):
#     return await weapon_autocomplete(interaction, current)


class RivenHelpView(View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Stats", style=ButtonStyle.primary)
    async def riven_help_stats(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            MESSAGE_PROVIDER("RIVEN_HELP_STATS"), ephemeral=True
        )

    @discord.ui.button(label="Weapons", style=ButtonStyle.secondary)
    async def riven_help_weapons(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            MESSAGE_PROVIDER("RIVEN_HELP_WEAPONS"), ephemeral=True
        )


@tree.command(
    name="riven_help",
    description=MESSAGE_PROVIDER("RIVEN_HELP_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def riven_help(interaction: discord.Interaction):
    view = RivenHelpView()
    await interaction.response.send_message(
        MESSAGE_PROVIDER("RIVEN_HELP_INITIAL"), view=view, ephemeral=True
    )


@tree.command(
    name="maintenance_text",
    description=MESSAGE_PROVIDER("MAINTENANCE_TEXT_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def text_maintenance(interaction: discord.Interaction):
    if any(role.id == SETTINGS.MAINTENANCE_ROLE_ID for role in interaction.user.roles):
        try:
            global MESSAGE_PROVIDER
            MESSAGE_PROVIDER = MessageProvider.from_gsheets(
                SETTINGS.MESSAGE_PROVIDER_URL
            )
            info(f"User {interaction.user.name} attempted to refresh google sheet data")
            await interaction.response.send_message(
                MESSAGE_PROVIDER("MAINTENANCE_INI"), ephemeral=True
            )
            await interaction.followup.send(
                MESSAGE_PROVIDER("MAINTENANCE_SUCCESS"), ephemeral=True
            )
        except Exception as e:
            info(f"Refresh failed with error: {e}")
            await interaction.followup.send(
                MESSAGE_PROVIDER("MAINTENANCE_ERROR", error=e), ephemeral=True
            )
    else:
        await interaction.response.send_message(
            MESSAGE_PROVIDER(
                "MAINTENANCE_DENIED",
                user=interaction.user.display_name,
            ),
            ephemeral=True,
        )


@tree.command(
    name="maintenance_riven",
    description=MESSAGE_PROVIDER("MAINTENANCE_RIVEN_DESC"),
    guild=discord.Object(SETTINGS.GUILD_ID),
)
async def riven_maintenance(interaction: discord.Interaction):
    if any(role.id == SETTINGS.MAINTENANCE_ROLE_ID for role in interaction.user.roles):
        try:
            await interaction.response.defer(ephemeral=True)

            maintenance_message = await interaction.followup.send(
                MESSAGE_PROVIDER("MAINTENANCE_RIVEN_INI"), ephemeral=True
            )
            info(f"Started riven update for user {interaction.user.name}")

            if maintenance_message:
                info("Maintenance message sent successfully.")
            else:
                info("Failed to send maintenance message.")
                return

            # Perform the update
            await refresh()

            info("Riven update completed successfully.")
            await maintenance_message.edit(
                content=MESSAGE_PROVIDER("MAINTENANCE_RIVEN_SUCCESS")
            )

        except discord.errors.NotFound as e:
            info(f"Failed to send the maintenance message: {e}")
            await interaction.followup.send(
                "An error occurred while trying to send the maintenance message.",
                ephemeral=True,
            )

        except Exception as e:
            info(f"Refresh failed with error: {e}")
            if maintenance_message:
                info("Editing the maintenance message to indicate failure.")
                await maintenance_message.edit(
                    content=MESSAGE_PROVIDER("MAINTENANCE_RIVEN_ERROR", error=e)
                )
            else:
                info("Failed to retrieve the maintenance message for error handling.")
    else:
        await interaction.response.send_message(
            MESSAGE_PROVIDER(
                "MAINTENANCE_RIVEN_DENIED", user=interaction.user.display_name
            ),
            ephemeral=True,
        )


client.run(SETTINGS.DISCORD_TOKEN)
