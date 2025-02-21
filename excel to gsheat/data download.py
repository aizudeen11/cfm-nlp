import gspread
from google.oauth2.service_account import Credentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(
    'credential.json', scopes=scopes)

client = gspread.authorize(creds)

sheet_id = '1PP6gpBcoOHjjgCx7LuHLa3dv4ET6ufKvpSY4UDvBczQ'
sheet = client.open_by_key(sheet_id)

values_list = sheet.sheet1.get_all_values()
print(values_list)
