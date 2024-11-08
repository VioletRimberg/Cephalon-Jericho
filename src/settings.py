from dynaconf import Dynaconf

class Settings:
    # The token used to authenticate with the Discord API
    DISCORD_TOKEN: str
    
    # The ID of the Discord guild (server) the bot will operate in
    GUILD_ID: int
    
    # The name of the clan associated with the bot
    CLAN_NAME: str
    
    # The ID of the channel where reports will be sent
    REPORT_CH: int
    
    # The ID of the role assigned to members of the clan
    MEMBER_ROLE_ID: int
    
    # The ID of the role assigned to guests
    GUEST_ROLE_ID: int

def load_settings()->Settings:
    """
    Load settings from settings.toml and .env files.
    """
    settings_loader = Dynaconf(
        settings_files=['settings.toml', '.env'],
        environments=True,
        envvar_prefix="",
        load_dotenv=True,
    )

    settings = Settings()
    settings_loader.populate_obj(settings)
    return settings

    
