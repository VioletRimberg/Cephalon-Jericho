import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Google Sheets client
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

def get_google_sheets_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

def test_can_authenticate():
    client = get_google_sheets_client()
    assert client is not None, "Failed to authenticate Google Sheets client."

def test_can_access_sheet():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    assert sheet is not None, "Failed to access Google Sheet."

def test_can_read_data():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_values()
    assert isinstance(data, list), "Sheet data should be a list of rows."
    print("Sheet Data:", data)  # Optional: shows current data for debugging

def test_can_write_data():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    test_data = ["TestUser", "1"]
    sheet.append_row(test_data)
    data = sheet.get_all_values()
    assert test_data in data, "Failed to write data to Google Sheet."