import pandas as pd
import requests
from io import BytesIO
import concurrent.futures as cf  # MultiThreaded code processing
import time
from cache_pandas import timed_lru_cache
# from data import Data

from pathlib import Path

path = Path(__file__).parent
path1 = path / "test.xlsx"
path2 = path / "financial stress index.xlsx"
path3 = path / "section 2.xlsx"
path4 = path / "Automation.xlsx"

print(path)


@timed_lru_cache(seconds=None, maxsize=None)
def dfs2() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df_init = pd.read_excel(path4, sheet_name='BoP edit')
    short_title = df_init['short_title'].to_list()
    description = df_init['desc'].to_list()
    sc2_half = pd.read_excel(path3, sheet_name="sc2_half")
    sc2_quarter = pd.read_excel(path3, sheet_name="sc2_quarter")
    date_temp = sc2_quarter.columns[4:].to_list()
    date_temp2 = [dt.strftime("%Y-%m") for dt in date_temp]
    rename_date = {k: v for k, v in zip(date_temp, date_temp2)}
    sc2_quarter.rename(columns=rename_date, inplace=True)
    sc2_quarter[list(rename_date.values())] = sc2_quarter[list(rename_date.values())].apply(lambda x: round(x, 2))
    sc2_quarter['Last Update Time'] = pd.to_datetime(sc2_quarter['Last Update Time']).dt.strftime("%Y-%m-%d")
    sc2_quarter['Type'] = sc2_quarter['Type'].replace(description, short_title)
    sc2_half[sc2_half.columns[2:]] = sc2_half[sc2_half.columns[2:]].apply(lambda x: round(x,2))
    sc2_half['Type'] = sc2_half['Type'].replace(description, short_title)

    dict1 = df_init[['group', 'short_title']].groupby("group")["short_title"].apply(list).reset_index().to_dict(orient='list')
    dict2 = {k: {item: item for item in v} for k, v in zip(dict1['group'], dict1['short_title'])}

    return sc2_half, sc2_quarter, dict2

# vix, policy_rate1, policy_rate2, policy_rate3, fx, cds, liquidity, gdp_growth
@timed_lru_cache(seconds=None, maxsize=None)
def dfs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    t1 = time.perf_counter()
    vix_data = pd.read_excel(path1, sheet_name="vix_data")
    policy_rate1 = pd.read_excel(path1, sheet_name="policy_rate1")
    fx = pd.read_excel(path1, sheet_name="fx")
    fx['Year'] = fx['Year'].astype(str)
    cds = pd.read_excel(path1, sheet_name="cds")
    liquidity = pd.read_excel(path1, sheet_name="liquidity")
    gdp_growth = pd.read_excel(path1, sheet_name="gdp_growth")
    stock_price_index = pd.read_excel(path1, sheet_name="stock_price_index")
    stock_price_index = stock_price_index.astype({'Year': 'object', 'Region': 'object'})
    sovereign_bond_yields = pd.read_excel(path1, sheet_name="sovereign_bond_yields")
    sovereign_bond_yields = sovereign_bond_yields.astype({'Year': 'object', 'Region': 'object'})
    fsi = pd.read_excel(path2, sheet_name="fsi")
    capital_flows = pd.read_excel(path1, sheet_name="capital_flows")
    t2 = time.perf_counter()
    policy_rate2 = policy_rate1[
        policy_rate1["Region"].isin(
            [
                "United States",
                "Euro Area",
                "Mongolia",
                "Nepal",
                "Philippines",
                "Korea",
                "Sri Lanka",
                "Thailand",
                "China",
            ]
        )
    ]
    policy_rate3 = policy_rate1[
        policy_rate1["Region"].isin(
            ["Indonesia", "India", "Malaysia", "Chinese Taipei", "Vietnam"]
        )
    ]
    print(f"Read excel method:{t2 - t1} seconds")

    return (
        vix_data,
        policy_rate1,
        policy_rate2,
        policy_rate3,
        fx,
        cds,
        liquidity,
        gdp_growth,
        fsi,
        stock_price_index,
        sovereign_bond_yields,
        capital_flows
    )

@timed_lru_cache(seconds=None, maxsize=None)
def dfs1() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    t1 = time.perf_counter()
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5DDYL_MTv8b1AsgYvUEDuxiIFq81-CR9Yccc4sL1pvv1wD2GyHNabQQiixJsRpwaxG59Qyg-Asr11/pub?output=xlsx"
    url2 = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSRMFoOOi8AXat4kH62KTNp56FbRc7XN9sSioYbfzOzPU0TDYWqkNqxhu8rWtnUy6erG9WVp9noknFp/pub?output=xlsx'
    response = requests.get(url)
    response2 = requests.get(url2)
    vix_data = pd.read_excel(BytesIO(response.content), sheet_name="vix_data")
    policy_rate1 = pd.read_excel(BytesIO(response.content), sheet_name="policy_rate1")
    fx = pd.read_excel(BytesIO(response.content), sheet_name="fx")
    fx['Year'] = fx['Year'].astype(str)
    cds = pd.read_excel(BytesIO(response.content), sheet_name="cds")
    liquidity = pd.read_excel(BytesIO(response.content), sheet_name="liquidity")
    gdp_growth = pd.read_excel(BytesIO(response.content), sheet_name="gdp_growth")
    stock_price_index = pd.read_excel(BytesIO(response.content), sheet_name="stock_price_index")
    stock_price_index = stock_price_index.astype({'Year': 'object', 'Region': 'object'})
    sovereign_bond_yields = pd.read_excel(BytesIO(response.content), sheet_name="sovereign_bond_yields")
    sovereign_bond_yields = sovereign_bond_yields.astype({'Year': 'object', 'Region': 'object'})
    fsi = pd.read_excel(BytesIO(response2.content), sheet_name="fsi")
    capital_flows = pd.read_excel(BytesIO(response.content), sheet_name="capital_flows")
    t2 = time.perf_counter()
    policy_rate2 = policy_rate1[
        policy_rate1["Region"].isin(
            [
                "United States",
                "Euro Area",
                "Mongolia",
                "Nepal",
                "Philippines",
                "Korea",
                "Sri Lanka",
                "Thailand",
                "China",
            ]
        )
    ]
    policy_rate3 = policy_rate1[
        policy_rate1["Region"].isin(
            ["Indonesia", "India", "Malaysia", "Chinese Taipei", "Vietnam"]
        )
    ]
    print(f"BytesIO method:{t2 - t1} seconds")

    return (
        vix_data,
        policy_rate1,
        policy_rate2,
        policy_rate3,
        fx,
        cds,
        liquidity,
        gdp_growth,
        fsi,
        stock_price_index,
        sovereign_bond_yields,
        capital_flows
    )

# @timed_lru_cache(seconds=None, maxsize=None)
# def dataF():
#     df = Data()
#     vix_data = df.vix_history()
#     policy_rate1, policy_rate2, policy_rate3 = df.policy_rate()
#     fx = df.forex_exchange()
#     cds = df.cds()
#     liquidity = df.liquidity()
#     gdp_growth = df.gdp_growth()
#     return (
#         vix_data,
#         policy_rate1,
#         policy_rate2,
#         policy_rate3,
#         fx,
#         cds,
#         liquidity,
#         gdp_growth,
#     )