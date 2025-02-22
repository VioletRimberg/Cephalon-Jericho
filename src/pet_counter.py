import gspread
from google.oauth2.service_account import Credentials
import os
from settings import Settings

SETTINGS = Settings()

# Authenticate
creds = Credentials.from_service_account_info(
    SETTINGS.GOOGLE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)


def get_pet_sheet():
    """Retrieve the pet tracking sheet."""
    return client.open_by_key(SETTINGS.GOOGLE_SHEET_PET_ID).sheet1


def get_pet_count(user_id: str) -> int:
    """Retrieve the pet count for a given user ID."""
    sheet = get_pet_sheet()
    records = sheet.get_all_records()

    for row in records:
        if str(row.get("User ID")) == str(user_id):
            return row.get("Pet Count", 0)
    return 0  # User not found


def update_pet_count(user_id: str):
    sheet = get_pet_sheet()
    data = sheet.get_all_records()

    user_id = str(user_id)  # Convert user ID to string for consistent matching
    global_count_cell = sheet.cell(2, 3).value

    global_count = int(global_count_cell) if global_count_cell else 0

    for i, row in enumerate(data):
        if str(row["User ID"]) == user_id:  # Compare as strings
            new_count = int(row["Pet Count"]) + 1
            sheet.update_cell(i + 2, 2, new_count)  # Update pet count
            global_count += 1
            sheet.update_cell(2, 3, global_count)  # Update global count
            return new_count, global_count

    # If user is not found, add them
    new_count = 1
    global_count += 1
    sheet.append_row(
        [user_id, new_count, ""]
    )  # Append user, new pet count, empty global counter
    sheet.update_cell(2, 3, global_count)  # Update global counter

    return new_count, global_count
