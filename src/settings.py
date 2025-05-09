from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class Role(BaseModel):
    name: str
    ids: list[int]


class Clan(BaseModel):
    name: str
    description: str
    channel: int
    roles: list[Role]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )
    # The token used to authenticate with the Discord API
    DISCORD_TOKEN: str

    # The ID of the Discord guild (server) the bot will operate in
    GUILD_ID: int

    # The ID of the channel where reports will be sent
    REPORT_CHANNEL_ID: int

    # The ID of the role assigned to guests
    GUEST_ROLE_ID: int

    # Display name of the guest rank
    GUEST_NAME: str = "Guest"

    # The ID of the maintenance role assigned to administration
    MAINTENANCE_ROLE_ID: int

    MESSAGE_PROVIDER_URL: str

    # Possible Roles per Clan for the onboarding process
    CLANS: list[Clan] = [
        Clan(
            name="Fractus Vitrum",
            description="Join the server as a Fractus Vitrum clan member.",
            channel=1363427533009457262,
            roles=[Role(name="Member", ids=[1363422761074298943])],
        )
    ]
    # The Google Credentials Path
    GOOGLE_CREDENTIALS: dict[str, str]

    #The Google Pet Sheet ID
    GOOGLE_SHEET_PET_ID: str

    #The Message Provider Sheet ID
    GOOGLE_SHEET_MESSAGEPROVIDER_ID: str

    #Milestones for pet function
    PERSONAL_MILESTONES: list[int] = [10, 25, 50]
    GLOBAL_MILESTONES: list[int] = [50, 100, 250, 500]
    
