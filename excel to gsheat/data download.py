# youtube - https://www.youtube.com/watch?v=zCEJurLGFRk&t=14s
# % pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread_dataframe import set_with_dataframe

from data import Data
from cache_pandas import timed_lru_cache
import logging

@timed_lru_cache(seconds=None, maxsize=None)
def dataF():
    logging.info("Fetching data in dataF()")
    df = Data()
    vix_data = df.vix_history()
    policy_rate1, policy_rate2, policy_rate3 = df.policy_rate()
    fx = df.forex_exchange()
    cds = df.cds()
    liquidity = df.liquidity()
    gdp_growth = df.gdp_growth()
    logging.info("Completed fetching data in dataF()")
    return (
        vix_data, #use this
        policy_rate1, #use this
        policy_rate2,
        policy_rate3,
        fx, #use this
        cds, #use this
        liquidity, #use this
        gdp_growth, #use this
    )


vix_data, policy_rate1, policy_rate2, policy_rate3, fx, cds, liquidity, gdp_growth, = dataF()

scopes = [
    'https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file(
    'credential.json', scopes=scopes)

client = gspread.authorize(creds)

# 1PP6gpBcoOHjjgCx7LuHLa3dv4ET6ufKvpSY4UDvBczQ
sheet_id = '11Ora6_5EoQJdgnUpjjZgFZyrILguo1c32mde_uQwupw'
sheet = client.open_by_key(sheet_id)

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 40]
})

set_with_dataframe(sheet.sheet1, df) 

values_list = sheet.sheet1.get_all_values()
print(values_list)

worksheet_list = map(lambda x: x.title, sheet.worksheets())
worksheet_name = {'vix_data': vix_data, 'policy_rate1': policy_rate1, 'fx': fx, 'cds': cds, 'liquidity': liquidity, 'gdp_growth': gdp_growth}
for new_worksheet_name, data in worksheet_name.items():
    if new_worksheet_name in worksheet_list:
        sheet1 = sheet.worksheet(new_worksheet_name)
    else:
        sheet1 = sheet.add_worksheet(title=new_worksheet_name, rows=10, cols=10)
    set_with_dataframe(sheet1, data)

# sheet.worksheet(new_worksheet_name) -- to select worksheet page
# sheet.add_worksheet(new_worksheet_name, rows=10, cols=10) -- add new worksheet page