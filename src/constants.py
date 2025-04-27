from message_provider import MessageProvider
from settings import Settings
from state import State

SETTINGS = Settings()
STATE: State = State.load()

MESSAGE_PROVIDER = MessageProvider.from_gsheets(
    sheet_id=SETTINGS.GOOGLE_SHEET_MESSAGEPROVIDER_ID,
    worksheet_name="message_list"  
)