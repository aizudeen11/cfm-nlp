# youtube - https://www.youtube.com/watch?v=zCEJurLGFRk&t=14s
# % pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread_dataframe import set_with_dataframe

from data import Data
from data_section_2 import main
from cache_pandas import timed_lru_cache
import logging

@timed_lru_cache(seconds=None, maxsize=None)
def dataF():
    df = Data()
    vix_data = df.vix_history()
    policy_rate1, policy_rate2, policy_rate3 = df.policy_rate()
    fx = df.forex_exchange()
    cds = df.cds()
    liquidity = df.liquidity()
    gdp_growth = df.gdp_growth()
    yield_data_calc, stock_data_calc2, empi, financial_sector_beta, garch, fsi = df.financial_stress_index()
    stock_price_index = df.stock_price_index()
    sovereign_bond_yields = df.sovereign_bond_yields()
    capital_flows = df.capital_flows()
    return (
        vix_data, #use this
        policy_rate1, #use this
        policy_rate2,
        policy_rate3,
        fx, #use this
        cds, #use this
        liquidity, #use this
        gdp_growth, #use this
        yield_data_calc, 
        stock_data_calc2, 
        empi, 
        financial_sector_beta, 
        garch, 
        fsi,
        stock_price_index, #use this
        sovereign_bond_yields, #use this
        capital_flows, #use this
    )

@timed_lru_cache(seconds=None, maxsize=None)
def dataF2():
    quarterly_type_half, quarterly_type_quarter, quarterly_region_half, annual_type_full, annual_region_full = main()
    return quarterly_type_half, quarterly_type_quarter, quarterly_region_half, annual_type_full, annual_region_full

# vix_data, policy_rate1, policy_rate2, policy_rate3, fx, cds, liquidity, gdp_growth, yield_data_calc, stock_data_calc2, empi, financial_sector_beta, garch, fsi, stock_price_index, sovereign_bond_yields, capital_flows = dataF()
quarterly_type_half, quarterly_type_quarter, quarterly_region_half, annual_type_full, annual_region_full = dataF2()

id_test = '11Ora6_5EoQJdgnUpjjZgFZyrILguo1c32mde_uQwupw'
id_fsi = '1IK1wbkFNaRH9vFwXfhBYh_RSK-UXKbaGzbCoAQWWRjY'
id_sc2 = '1hKGm154j2OEaGZ3Gi7Qr7uADKupNP_raQ0vV70OlTkk'

# ws1 = {'vix_data': vix_data, 'policy_rate1': policy_rate1, 'fx': fx, 'cds': cds, 'liquidity': liquidity, 'gdp_growth': gdp_growth, 'stock_price_index': stock_price_index
    #    , 'sovereign_bond_yields': sovereign_bond_yields, 'capital_flows': capital_flows}
# ws2 = {'yield_data_calc': yield_data_calc, 'stock_data_calc2': stock_data_calc2, 'empi': empi, 'financial_sector_beta': financial_sector_beta, 'garch': garch, 'fsi': fsi}

ws3 = {'quarterly_type_half': quarterly_type_half, 'quarterly_type_quarter': quarterly_type_quarter, 'quarterly_region_half': quarterly_region_half,
       'annual_type_full': annual_type_full, 'annual_region_full': annual_region_full}

# for x in ws2:
#     ws2[x] = ws2[x].reset_index()
#     ws2[x]['Date'] = ws2[x]['Date'].dt.strftime('%Y-%m')

def process(id, worksheet_data_dict):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('credential.json', scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(id)

    # Get list of existing worksheet titles
    worksheet_list = [ws.title for ws in sheet.worksheets()]

    for worksheet_name, data in worksheet_data_dict.items():
        # If worksheet exists, delete it
        if worksheet_name in worksheet_list:
            ws_to_delete = sheet.worksheet(worksheet_name)
            sheet.del_worksheet(ws_to_delete)

        # Create new worksheet
        new_ws = sheet.add_worksheet(title=worksheet_name, rows=10, cols=10)

        # Write dataframe to new worksheet
        set_with_dataframe(new_ws, data)

# process(id_test, ws1) # uncomment if need to update test sheet
# process(id_fsi, ws2) # uncomment if need to update fsi sheet
if __name__ == "__main__":
    process(id_sc2, ws3)

# df = Data()
# capital_flows = df.capital_flows()
# ws_temp = {'capital_flows': capital_flows}
# process(id_test, ws_temp)
# print(capital_flows)

# sheet.worksheet(new_worksheet_name) -- to select worksheet page
# sheet.add_worksheet(new_worksheet_name, rows=10, cols=10) -- add new worksheet page