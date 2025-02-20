import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_PET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Authenticate
creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)

def get_pet_sheet():
    """Retrieve the pet tracking sheet."""
    return client.open_by_key(SHEET_ID).sheet1

def get_pet_count(user_id: str) -> int:
    """Retrieve the pet count for a given user ID."""
    sheet = get_pet_sheet()
    records = sheet.get_all_records()

    for row in records:
        if str(row.get("User ID")) == str(user_id):  
            return row.get("Pet Count", 0)  
    return 0  # User not found

def update_pet_count(user_id: str):
    sheet = get_pet_sheet()  # Replace with your function to access the sheet

    # Fetch all data from the sheet
    data = sheet.get_all_records()

    # Find the user row
    for i, row in enumerate(data):
        if row["User ID"] == user_id:
            # Update existing user's count
            new_count = row["Pets"] + 1
            sheet.update_cell(i + 2, 2, new_count)  # +2 because Google Sheets index starts at 1, and there's a header row
            global_count = int(sheet.cell(2, 2).value) + 1  # Assuming global count is at B2
            sheet.update_cell(2, 2, global_count)
            return new_count, global_count

    # If user is not found, add them
    new_count = 1
    sheet.append_row([user_id, new_count])
    global_count = int(sheet.cell(2, 2).value) + 1
    sheet.update_cell(2, 2, global_count)
    
    return new_count, global_count
