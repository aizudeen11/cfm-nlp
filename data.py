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
        return df, df2, df3
    def forex_exchange(self):
        df1 = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx", sheet_name=3, header=1)
        df1 = df1.iloc[:,:12]
        df2 = df1.copy()
        row = [x for x in range(362)]
        df2 = df2.drop([0,1,*row], axis=0).reset_index().drop('index', axis=1)
        df2 = df2.rename(columns={'Region':'Date'})
        date_new =[x for x in df2.Date if isinstance(x, datetime.datetime)]
        df2 = df2.iloc[:len(date_new)]
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2['Year'] = df2['Date'].apply(lambda x : x.date().strftime("%Y"))
        df2['Date2'] = df2['Date'].apply(lambda x : x.date().strftime("%Y-%m"))
        latest_year = int(sorted(df2['Year'].unique())[-1])
        country = df2['Region'].unique()
        country_year, all_same, year_use = dict(), True, latest_year

        for x in country:    
            if len(df2[(df2['Region']==x) & (df2['Year']==str(latest_year))]) > 0:
                country_year.update({x:latest_year})
            else:
                all_same = False
                year_use = df2[(df2['Region']==x)]['Year'].unique()[-1]
                country_year.update({x:year_use}) 

        country_year.update({'info':{'all_same': all_same, 'year_use': year_use}})      
        year1 = country_year['info']['year_use']
        df2 = sqldf(f'select Date2 as Date, Year, Region, Value, row_number() over(partition by Region, Year order by Date2) as row_num from df2 where Year in ("{year1}", "{year1 - 1}")')
        num_list = sorted(df2[(df2['Region']=='China') & (df2['Year']==str(year1))]['row_num'].unique())
        num1, num2 =num_list[0] , num_list[-1]
        df2 = df2[(df2['Region'].isin(country))&(df2['row_num'].isin([num1, num2]))&(df2['Year'].isin([str(year1), str(year1-1)]))]
        calc_country, year_list = dict(), [str(year1), str(year1 -1)]

        for x in country:
            for y in year_list:
                nomi = float(df2[(df2['Region'] == x)&(df2['row_num']==1)&(df2['Year']==str(y))]['Value'].values[0])
                denomi = float(df2[(df2['Region'] == x)&(df2['row_num']!=1)&(df2['Year']==str(y))]['Value'].values[0])
                calc = ((nomi/denomi)-1)*100
                if calc_country.get(x) == None:
                    calc_country.update({x:{y:calc}})
                else:
                    calc_country[x].update({y:calc})
        df = pd.DataFrame(calc_country).reset_index()
        df = df.melt(id_vars="index", var_name="Region", value_name="Value").rename({'index': 'Year'})
        return df
    def cds(self):
        df = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx", sheet_name=5, header=1)
        col =df.columns[:10]
        df2= df[[*col]]
        i= [s.find(':') for s in col]
        col2 = [x[:y] for x, y in zip(col[1:], i[1:])]
        df2 = df2.rename({k:v for (k,v) in zip(col[1:],col2)}, axis=1).rename({'.DESC' : 'Date'}, axis=1)
        to_include =[x for x in df2.China if isinstance(x, float)]
        df2 = df2[df2.China.isin(to_include)].reset_index(drop=True)
        drop_index =[x for x in df2['Date'].isna()].index(True)
        df2 = df2.drop(index=[x for x in range(drop_index, len(df2))])
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2 = df2.fillna('')        
        return df2
    def liquidity(self):
        df = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\download zip\BIS Liquidity data.xlsx")
        df = df[['TIME_PERIOD','OBS_VALUE']]
        return df
    def all_df(self):
        vix = self.vix_history()
        policy_rate1,policy_rate2,policy_rate3 = self.policy_rate()
        monthly_inflation1,monthly_inflation2,monthly_inflation3 = self.monthly_inflation()
        forex_exchange = self.forex_exchange()
        cds = self.cds()
        df_dict = {'vix':vix,
                   'policy_rate1': policy_rate1,
                   'policy_rate2': policy_rate2,
                   'policy_rate3': policy_rate3,
                   'monthly_inflation1': monthly_inflation1,
                   'monthly_inflation2': monthly_inflation2,
                   'monthly_inflation3': monthly_inflation3,
                   'forex_exchange': forex_exchange,
                   'cds':cds}
        return df_dict
