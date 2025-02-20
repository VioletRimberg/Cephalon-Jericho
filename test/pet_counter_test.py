import pytest
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Google Sheets client
SHEET_ID = os.getenv("GOOGLE_SHEET_PET_ID")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

@pytest.mark.skip(reason="Can't provide Keyfile")
def get_google_sheets_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

@pytest.mark.skip(reason="Can't provide Keyfile")
def test_can_authenticate():
    client = get_google_sheets_client()
    assert client is not None, "Failed to authenticate Google Sheets client."

@pytest.mark.skip(reason="Can't provide Keyfile")
def test_can_access_sheet():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    assert sheet is not None, "Failed to access Google Sheet."

@pytest.mark.skip(reason="Can't provide Keyfile")
def test_can_read_data():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    data = sheet.get_all_values()
    assert isinstance(data, list), "Sheet data should be a list of rows."
    print("Sheet Data:", data)

@pytest.mark.skip(reason="Can't provide Keyfile")
def test_can_write_data():
    client = get_google_sheets_client()
    sheet = client.open_by_key(SHEET_ID).sheet1
    test_data = ["TestUser", "1"]

    sheet.append_row(test_data)
    data = sheet.get_all_values()

    data = [row[:len(test_data)] for row in data]

    assert test_data in data, "Failed to write data to Google Sheet."

    # Cleanup: Find the row index and delete it
    for i, row in enumerate(data, start=1):  
        if row[:len(test_data)] == test_data:
            sheet.delete_rows(i)
            break  # Stop after deleting the first match