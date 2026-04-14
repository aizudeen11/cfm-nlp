# section 2 CFM data export to excel

import pandas as pd
import xlwings as xw
from datetime import datetime
from data_section_2 import *

def bopq_data():
    start_date = datetime(2023, 3, 1)
    # x,y,z = bop_quarterly ####### select which one to use
    y = to_combine_bopq() ####### select which one to use
    index = y.columns.tolist().index(start_date)
    df = y.copy()[y.columns[:4].tolist()+y.columns[index:index+11].tolist()]

    asset_position = ['B'+ str(x) for x in range(2,311,22)]
    liabi_position = ['Z'+ str(x) for x in range(2,311,22)]

    asset_item =['FDI Assets', 'FDI Equity Assets', 'FDI Debt Assets', 'Portfolio Assets', 'Portfolio Equity Assets', 'Portfolio Debt Assets', 'Financial Derivative Assets', 'Other Investment Assets', 'OI Equity Assets', 'Currency and Deposits Assets', 'Loans Assets', 'Insurance and Pension Assets', 'Trade Credits and Advances Assets', 'OI Others Assets', 'Official Reserve Assets']
    liabi_item =['FDI Liabilities', 'FDI Equity Liabilities', 'FDI Debt Liabilities', 'Portfolio Liabilities', 'Portfolio Equity Liabilities', 'Portfolio Debt Liabilities', 'Financial Derivative Liabilities', 'Other Investment Liabilities', 'OI Equity Liabilities', 'Currency and Deposits Liabilities', 'Loans Liabilities', 'Insurance and Pension Liabilities', 'Trade Credits and Advances Liabilities', 'OI Others Liabilities', 'SDR Liabilities']

    asset_item_position = dict(zip(asset_item, asset_position))
    liabi_item_position = dict(zip(liabi_item, liabi_position))

    wb = xw.Book(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Documents\[Template]\Figures BoP H1025 v2.xlsx")

    def func(dict1:dict):
        for item, position in dict1.items():
            df_temp = df[df['Type'] == item]
            df_temp = df_temp[df_temp.columns[4:]]
            wb.sheets['BOPQ data'][position].options(index=False, header=False).value = df_temp

    func(asset_item_position)
    func(liabi_item_position)

    date_list = []
    y_to_q = {3 : 1, 6 : 2, 9 : 3, 12 : 4}
    for x in y.columns[index:index+11].tolist():
        date_list.append(str(y_to_q[x.month]) + 'Q' + str(x.year))

    wb.sheets['BOPQ data']['B1'].value = date_list

def iipq_data():
    start_date = datetime(2023, 3, 1)
    # x,y,z = iip_quarterly ####### select which one to use
    y = to_combine_iipq() ####### select which one to use
    index = y.columns.tolist().index(start_date)
    df = y.copy()[y.columns[:4].tolist()+y.columns[index:index+11].tolist()]

    asset_position = ['B'+ str(x) for x in range(2,311,22)]
    liabi_position = ['Z'+ str(x) for x in range(2,311,22)]

    asset_item =['FDI Assets', 'FDI Equity Assets', 'FDI Debt Assets', 'Portfolio Assets', 'Portfolio Equity Assets', 'Portfolio Debt Assets', 'Financial Derivative Assets', 'Other Investment Assets', 'OI Equity Assets', 'Currency and Deposits Assets', 'Loans Assets', 'Insurance and Pension Assets', 'Trade Credits and Advances Assets', 'OI Others Assets', 'Official Reserve Assets', 'International Investment Assets']
    liabi_item =['FDI Liabilities', 'FDI Equity Liabilities', 'FDI Debt Liabilities', 'Portfolio Liabilities', 'Portfolio Equity Liabilities', 'Portfolio Debt Liabilities', 'Financial Derivative Liabilities', 'Other Investment Liabilities', 'OI Equity Liabilities', 'Currency and Deposits Liabilities', 'Loans Liabilities', 'Insurance and Pension Liabilities', 'Trade Credits and Advances Liabilities', 'OI Others Liabilities', 'SDR Liabilities', 'International Investment Liabilities']

    asset_item_position = dict(zip(asset_item, asset_position))
    liabi_item_position = dict(zip(liabi_item, liabi_position))

    wb = xw.Book(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Documents\[Template]\Figures IIP H0125 v2.xlsx")

    def func(dict1:dict):
        for item, position in dict1.items():
            df_temp = df[df['Type'] == item]
            df_temp = df_temp[df_temp.columns[4:]]
            wb.sheets['IIPQ data'][position].options(index=False, header=False).value = df_temp

    func(asset_item_position)
    func(liabi_item_position)

    date_list = []
    y_to_q = {3 : 1, 6 : 2, 9 : 3, 12 : 4}
    for x in y.columns[index:index+11].tolist():
        date_list.append(str(y_to_q[x.month]) + 'Q' + str(x.year))

    wb.sheets['IIPQ data']['B1'].value = date_list

iipq_data()