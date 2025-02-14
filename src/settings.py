from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class Role(BaseModel):
    name: str
    id: int

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

    # The ID of the role assigned to members of the clan
    MEMBER_ROLE_ID: int

    # The ID of the role assigned to guests
    GUEST_ROLE_ID: int

    # The ID of the maintenance role assigned to administration
    MAINTENANCE_ROLE_ID: int

    # The URL assigned to the Message Provider
    MESSAGE_PROVIDER_URL: str = "https://docs.google.com/spreadsheets/d/1iIcJkWBY898qGPhkQ3GcLlj1KOkgjlWxWkmiHkzDuzk/edit"

    # Possible Roles per Clan for the onboarding process
    CLAN_ROLES: dict[str, list[Role]] = {"Golden Tenno": [Role(name="Member", id=0)]}


