import pandas as pd 
from pandasql import sqldf
import datetime

class Data:
    def __init__(self):
        pass
    def vix_history(self):
        df = pd.read_excel(r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\download zip\VIX_History.xlsx',sheet_name=1)
        df['Date'] = df['Month'].astype(str) + '/' + df['Year'].astype(str)
        df = df.rename(columns={'avg(CLOSE)': 'CLOSE'})
        df = df[['Date', 'CLOSE']].iloc[::-1][360:]
        return df
    def policy_rate(self):
        df = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\SEACEN CFM Data.xlsx",sheet_name=5, nrows=14)
        df = df.drop(df.columns[[0,2,3]], axis = 1)
        date = df.columns[1:]
        date2 = [x.date().strftime("%Y-%m") for x in date]
        df = df.rename(columns={k:v for (k,v) in zip(date,date2)})
        df = df.drop(date2[:84], axis=1)
        df = df.melt(id_vars="Region", var_name="Date", value_name="Value")
        df2 = sqldf('select * from df where Region in ("United States", "Euro Area", "Mongolia", "Nepal", "Philippines", "Korea", "Sri Lanka", "Thailand", "China")')
        df3 = sqldf('select * from df where Region in ("Indonesia", "India", "Malaysia", "Chinese Taipei", "Vietnam")')
        return df, df2, df3
    def monthly_inflation(self):
        df = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Growth and Inflation 3Q2024.xlsx", sheet_name=3, nrows=17)
        df = df.drop(df.columns[[0,2,3]], axis = 1)
        date = df.columns[1:]
        date_new =[x for x in date if isinstance(x, datetime.date)]
        df = df[['Region', *date_new]]
        date2 = [x.date().strftime("%Y-%m") for x in date]
        df = df.rename(columns={k:v for (k,v) in zip(date,date2)})
        df = df.melt(id_vars="Region", var_name="Date", value_name="Value")
        df2 = sqldf('select * from df where Region not in ("Cambodia", "China", "Hong Kong SAR (China)", "Malaysia", "Vietnam", "Thailand")')
        df3 = sqldf('select * from df where Region in ("Cambodia", "China", "Hong Kong SAR (China)", "Malaysia", "Vietnam", "Thailand")')