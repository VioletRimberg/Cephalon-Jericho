from message_provider import MessageProvider
from settings import Settings
from state import State

SETTINGS = Settings()
STATE: State = State.load()
MESSAGE_PROVIDER = MessageProvider.from_gsheets(SETTINGS.MESSAGE_PROVIDER_URL)
