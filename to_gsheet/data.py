import pandas as pd
from pandasql import sqldf
import datetime
import numpy as np
import warnings
from arch import arch_model
import requests
from io import BytesIO
warnings.filterwarnings("ignore")
# use min max()


class Data:
    def __init__(self):
        pass

    def gdp_growth(self) -> pd.DataFrame:
        """     
        This function processes GDP growth data from an Excel file and returns a DataFrame with the growth rates for various regions and countries.   
        Returns:
            pd.DataFrame: A DataFrame containing the GDP growth rates for different regions and countries.
        """
        def convert_date_to_quarter(date_str, dtq=True):
            if not dtq:
                year = date_str[:4]
                quarter = date_str[5:7]
                qd_dict = {"03": "1Q", "06": "2Q", "09": "3Q", "12": "4Q"}
            else:
                year = date_str[-4:]
                quarter = date_str[0]
                qd_dict = {"1": "31/3/", "2": "30/6/", "3": "30/9/", "4": "31/12/"}
            if quarter in qd_dict.keys():
                return f"{qd_dict.get(quarter)}{year}"
            else:
                return date_str

        def fd_calc(fd: pd.DataFrame, cal=True) -> pd.DataFrame:
            sum_row = fd.sum()
            fd.loc["Total"] = sum_row
            if cal:
                fd = fd.apply(lambda x: x / fd.loc["Total"], axis=1)
            return fd

        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Growth and Inflation 3Q2024.xlsx",
            sheet_name=1,
            header=1,
        )

        fd = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Growth and Inflation 3Q2024.xlsx",
            sheet_name=2,
            nrows=12,
        )

        col_name = list(map(convert_date_to_quarter, fd.columns))
        fd.rename({fd.columns[0]: "Region"}, axis=1, inplace=True)
        fd.set_index("Region", inplace=True)
        fd.loc["Total"] = fd.sum()
        df2 = df.copy()
        df2 = df2.drop([0, 1], axis=0)
        ch_df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Growth and Inflation 3Q2024.xlsx",
            sheet_name=0,
            header=1,
        )
        ch_df = (
            ch_df.drop([0, 1])[["Region", "China"]]
            .set_index("Region")
            .rename(columns={"Region": "Date"})
        )
        df2 = df2[df2.columns[:13]].rename(columns={"Region": "Date"}).set_index("Date")
        df2["China"] = ch_df["China"]
        df3 = df2[
            [
                "China",
                "India",
                "Malaysia",
                "Mongolia",
                "Philippines",
                "Taiwan",
                "Thailand",
            ]
        ].apply(lambda x: ((x / x.shift(4)) - 1) * 100)
        df3 = pd.concat(
            [
                df2[
                    [
                        "Hong Kong SAR (China)",
                        "Indonesia",
                        "South Korea",
                        "Singapore",
                        "Vietnam",
                    ]
                ],
                df3,
            ],
            axis=1,
        )
        df3.reset_index(inplace=True)
        df3["Date"] = pd.to_datetime(df3["Date"]) + pd.offsets.MonthEnd(0)
        select_row = len(fd.columns)
        df4 = df3[-select_row:]

        df4["Date"] = list(
            df4["Date"].apply(lambda x: convert_date_to_quarter(str(x), False))
        )
        df4 = (
            df4.set_index("Date")
            .transpose()
            .reset_index()
            .rename(columns={"index": "Region"})
        )  # this is bullshit
        df4.set_index("Region", inplace=True)
        df4.rename(
            index={
                "Hong Kong SAR (China)": "Hong Kong",
                "South Korea": "Korea",
                "Taiwan": "Taipei",
            },
            inplace=True,
        )
        df4 = df4.reindex(fd.index[:12])

        asean5 = fd_calc(
            fd.loc[["Indonesia", "Malaysia", "Philippines", "Thailand", "Vietnam"]]
        ) * fd_calc(
            df4.loc[["Indonesia", "Malaysia", "Philippines", "Thailand", "Vietnam"]],
            cal=False,
        )
        asean5.drop("Total", inplace=True)
        asean5_sum = asean5.sum()
        asean5.loc["ASEAN-5"] = asean5_sum

        adv_asia = fd_calc(
            fd.loc[["Hong Kong", "Korea", "Singapore", "Taipei"]]
        ) * fd_calc(df4.loc[["Hong Kong", "Korea", "Singapore", "Taipei"]], cal=False)
        adv_asia.drop("Total", inplace=True)
        adv_asia_sum = adv_asia.sum()
        adv_asia.loc["Asia Advanced Economies"] = adv_asia_sum

        asia = fd.apply(lambda x: x / fd.loc["Total"], axis=1) * df4
        asia_sum = asia.sum()
        asia.loc["Asia"] = asia_sum

        gdp_growth = (
            pd.concat(
                [
                    asia.loc["Asia"],
                    df4.loc["China"],
                    df4.loc["India"],
                    asean5.loc["ASEAN-5"],
                    adv_asia.loc["Asia Advanced Economies"],
                ],
                axis=1,
            )
            .reset_index()
            .rename(columns={"index": "Quarter"})
        )
        gdp_growth = gdp_growth.melt(
            id_vars="Quarter", var_name="Region", value_name="Value"
        )
        return gdp_growth

    def vix_history(self) -> pd.DataFrame:
        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\download zip\VIX_History.xlsx",
            sheet_name=1,
        )
        df["Date"] = df["Month"].astype(str) + "-" + df["Year"].astype(str)
        df["Date"] = pd.to_datetime(df["Date"]) + pd.offsets.MonthEnd(0)
        df = df.rename(columns={"avg(CLOSE)": "CLOSE"})
        df = df[["Date", "CLOSE"]]  # .iloc#[::-1]#[360:]
        return df

    def policy_rate(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\SEACEN CFM Data.xlsx",
            sheet_name=5,
            nrows=14,
        )
        df = df.drop(df.columns[[0, 2, 3]], axis=1)
        date = df.columns[1:]
        date2 = [x.date().strftime("%Y-%m") for x in date]
        df = df.rename(columns={k: v for (k, v) in zip(date, date2)})
        # df = df.drop(date2[:84], axis=1)
        df = df.melt(id_vars="Region", var_name="Date", value_name="Value")
        df["Date"] = pd.to_datetime(df["Date"]) + pd.offsets.MonthEnd(0)
        df2 = sqldf(
            'select * from df where Region in ("United States", "Euro Area", "Mongolia", "Nepal", "Philippines", "Korea", "Sri Lanka", "Thailand", "China")'
        )
        df2["Date"] = pd.to_datetime(df2["Date"]) + pd.offsets.MonthEnd(0)
        df3 = sqldf(
            'select * from df where Region in ("Indonesia", "India", "Malaysia", "Chinese Taipei", "Vietnam")'
        )
        df3["Date"] = pd.to_datetime(df3["Date"]) + pd.offsets.MonthEnd(0)
        return df, df2, df3

    def monthly_inflation(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Growth and Inflation 3Q2024.xlsx",
            sheet_name=3,
            nrows=17,
        )
        df = df.drop(df.columns[[0, 2, 3]], axis=1)
        date = df.columns[1:]
        date_new = [x for x in date if isinstance(x, datetime.date)]
        df = df[["Region", *date_new]]
        date2 = [x.date().strftime("%Y-%m") for x in date]
        df = df.rename(columns={k: v for (k, v) in zip(date, date2)})
        df = df.melt(id_vars="Region", var_name="Date", value_name="Value")
        df2 = sqldf(
            'select * from df where Region not in ("Cambodia", "China", "Hong Kong SAR (China)", "Malaysia", "Vietnam", "Thailand")'
        )
        df3 = sqldf(
            'select * from df where Region in ("Cambodia", "China", "Hong Kong SAR (China)", "Malaysia", "Vietnam", "Thailand")'
        )
        return df, df2, df3

    def forex_exchange(self) -> pd.DataFrame:
        df1 = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx",
            sheet_name=3,
            header=1,
        )
        df1 = df1.iloc[:, :12]
        df2 = df1.copy()
        df2 = df2.drop([0, 1], axis=0).reset_index(drop=True)
        df2 = df2.rename(columns={"Region": "Date"})
        date_new = [x for x in df2.Date if isinstance(x, datetime.datetime)]
        df2 = df2.iloc[: len(date_new)]
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2["Date"] = pd.to_datetime(df2["Date"]) + pd.offsets.MonthEnd(0)
        df2["Year"] = df2["Date"].apply(lambda x: x.date().strftime("%Y"))
        df2["Date2"] = df2["Date"].apply(lambda x: x.date().strftime("%Y-%m"))
        year_now = datetime.date.today().year
        year2 = [str(x) for x in range(2020, year_now + 1)]
        latest_year = int(sorted(df2["Year"].unique())[-1])
        country = df2["Region"].unique()

        df2 = sqldf(
            f'select Date2 as Date, Year, Region, Value, row_number() over(partition by Region, Year order by Date2) as row_num from df2 where Year in ("{'", "'.join(year2)}")'
        )

        df2 = df2.groupby("Year").apply(
            lambda x: x[x["row_num"].isin([x["row_num"].min(), x["row_num"].max()])]
        )
        year2 = df2['Year'].unique()
        df2.reset_index(drop=True, inplace=True)
        df2.fillna(0, inplace=True)
        calc_country = dict()

        for x in country:
            for y in year2:
                if len(df2[(df2["Region"] == x) & (df2["Year"] == str(y))]) == 1:
                    continue
                df_temp = df2[
                    (df2["Region"] == x)
                    & (df2["Year"] == str(y))
                ]
                nomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].min())
                    ]["Value"].values[0]
                )
                denomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].max())
                    ]["Value"].values[0]
                )
                calc = 0 if nomi == 0 and denomi == 0 else ((nomi / denomi) - 1) * 100
                if calc_country.get(x) == None:
                    calc_country.update({x: {y: calc}})
                else:
                    calc_country[x].update({y: calc})
        df = pd.DataFrame(calc_country).reset_index()
        df = df.melt(id_vars="index", var_name="Region", value_name="Value").rename(
            {"index": "Year"}, axis=1
        )
        region_sort = list(
            df[(df["Year"] == df["Year"].unique()[-1])].sort_values(
                by="Value", ascending=False
            )["Region"]
        )
        df["Region"] = pd.Categorical(
            df["Region"], categories=region_sort, ordered=True
        )
        df = df.sort_values(by=["Region", "Year"], ascending=False)
        return df

    def cds(self) -> pd.DataFrame:
        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx",
            sheet_name=5,
            header=1,
        )
        col = df.columns[:10]
        df2 = df[[*col]]
        i = [s.find(":") for s in col]
        col2 = [x[:y] for x, y in zip(col[1:], i[1:])]
        df2 = df2.rename({k: v for (k, v) in zip(col[1:], col2)}, axis=1).rename(
            {".DESC": "Date"}, axis=1
        )
        to_include = [x for x in df2.China if isinstance(x, float)]
        df2 = df2[df2.China.isin(to_include)].reset_index(drop=True)
        drop_index = [x for x in df2["Date"].isna()].index(True)
        df2 = df2.drop(index=[x for x in range(drop_index, len(df2))])
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2["Date"] = pd.to_datetime(df2["Date"]) + pd.offsets.MonthEnd(0)
        df2 = df2.fillna("")
        return df2

    def liquidity(self) -> pd.DataFrame:
        df = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\download zip\BIS Liquidity data.xlsx"
        )
        df = df[["TIME_PERIOD", "OBS_VALUE"]]
        return df
    
    def financial_stress_index(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        yield_data1 = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\00 dlx.xlsx", header=1)
        yield_data1 = yield_data1[[*yield_data1.columns[[0,1,3]]]]
        yield_data1.drop([0,1,2], inplace=True)
        yield_data1.rename(columns={'.DESC': 'Date',
                                'Indonesia: 10 Year Treasury Bond Mid Yield (% p.a.)': 'Indonesia',
                                'Philippines: 10 Year Treasury Bond Mid Yield (% p.a.)': 'Philippines'},
                            inplace=True)

        # yield_data1["Date"] = pd.to_datetime(yield_data1["Date"], errors='coerce') + pd.offsets.MonthEnd(0)
        yield_data1['Month'] = yield_data1['Date'].apply(lambda x: x[:3])
        yield_data1['Year'] = yield_data1['Date'].apply(lambda x: x[-2:])
        yield_data1["Date"] = yield_data1.apply(lambda x: pd.to_datetime(f"{x['Month']} {x['Year']}", format='%b %y') + pd.offsets.MonthEnd(0), axis=1)
        yield_data1.drop(['Month', 'Year'], axis=1, inplace=True)
        yield_data2 = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Financial Stress Indices.xlsx"
                                    , sheet_name='Yields2'
                                    , header=1)
        yield_data2=yield_data2[yield_data2.columns[:11]]
        yield_data2.drop([0,1], inplace=True)
        yield_data2.rename(columns={'Region': 'Date'}, inplace=True)
        yield_data2["Date"] = pd.to_datetime(yield_data2["Date"]) + pd.offsets.MonthEnd(0)
        yield_data2.drop('Philippines', axis=1, inplace=True)

        yield_data = yield_data2.join(yield_data1.set_index('Date'), on='Date')
        yield_data.set_index('Date', inplace=True)

        yield_data_calc = yield_data.apply(lambda x : x - x['United States'], axis =1)
        yield_data_calc.drop('United States', axis=1, inplace=True)
        yield_data_calc = yield_data_calc.loc[yield_data_calc.index >= "2010-01-31"]
        yield_data_calc['Asia'] = yield_data_calc.mean(axis= 1)
        yield_data_calc = (yield_data_calc - yield_data_calc.mean()) / yield_data_calc.std()
        
        key_dict = {
            'Select this link and click Refresh/Edit Download to update data and add or remove series': 'Date',
            'Index: Shenzhen Stock Exchange: Composite': 'China',
            'Equity Market Index: Month End: Hang Seng': 'Hong Kong SAR (China)',
            'Equity Market Index: Month End: BSE: Sensitive 30 (Sensex)': 'India',
            'Equity Market Index: Month End: Jakarta Composite': 'Indonesia',
            'Equity Market Index: Month End: FTSE Bursa Malaysia: Composite': 'Malaysia',
            'Equity Market Index: Month End: PSEi': 'Philippines',
            'Equity Market Index: Month End: FTSE Strait Times': 'Singapore',
            'Equity Market Index: Month End: KOSPI': 'South Korea',
            'TWSE: Equity Market Index: TAIEX Capitalization Weighted: Month Avg': 'Taiwan',
            'Equity Market Index: Month End: SET': 'Thailand',
        }


        stock_data = pd.read_excel(r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Financial Stress Indices.xlsx', sheet_name='Stock Price Indexes')
        stock_data = stock_data[key_dict.keys()]
        stock_data.drop([0,1,2], inplace=True)
        stock_data.rename(columns=key_dict, inplace=True)
        stock_data2 = stock_data.copy()
        stock_data2["Date"] = pd.to_datetime(stock_data2["Date"]) + pd.offsets.MonthEnd(0)
        stock_data2.set_index('Date', inplace=True)
        stock_data2 = stock_data2.loc[stock_data2.index >= "2008-12-01"]
        stock_data2 = stock_data2.astype(float)

        stock_data_calc = stock_data2.apply(lambda x : np.log(x))
        stock_data_calc = (stock_data_calc.shift(1) - stock_data_calc) * 100 ## can use pandas .diff() function
        # stock_data_calc = stock_data_calc.loc[stock_data_calc.index >= "2009-01-01"] ##2010-01-01
        stock_data_calc['Asia'] = stock_data_calc.mean(axis=1)
        stock_data_calc2 = (stock_data_calc - stock_data_calc.mean())/stock_data_calc.std()
        stock_data_calc2 = stock_data_calc2.loc[stock_data_calc2.index >= "2009-12-01"] ##2010-01-01

        key_dict_fb = {
            'Select this link and click Refresh/Edit Download to update data and add or remove series': 'Date',
            'Index: Shenzhen Stock Exchange: Financials': 'China',
            'Index: Hang Seng Finance': 'Hong Kong SAR (China)',
            'BSE: Index: Bankex': 'India',
            '(DC)IDX: Index: Finance': 'Indonesia1',
            'IDX: Index: Financials': 'Indonesia2',
            'Bursa Malaysia: Index: Financial Services': 'Malaysia',
            'Index: BankingFinancial Services': 'Philippines',
            'Equity Market Index: Month End: FTSE Strait Times':'Singapore1',
            'Singapore Exchange Turnover: Value: Mainboard': 'Singapore2',
            'Singapore Exchange Turnover: Value: Mainboard: Financials': 'Singapore3',
            'Index: KOSPI: Financial Institutions': 'South Korea',
            'TWSE: Equity Market Index: Finance and Insurance': 'Taiwan',
            'SET: Index: Banking': 'Thailand1', #T
            'SET: Index: Finance and Securities': 'Thailand2', #V
            'SET: Index: Insurance': 'Thailand3', #U
            'SET: Market Capitalization: Banking': 'Thailand4', #X
            'SET: Market Capitalization: Finance and Securities': 'Thailand5', #Y
            'SET: Market Capitalization: Insurance': 'Thailand6', #Z
            'Financial Index': 'Financial Index1',
            }
        fb = pd.read_excel(r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Financial Stress Indices.xlsx', sheet_name='Stock Price Indexes')
        fb = fb[key_dict_fb.keys()]
        fb.drop([0,1,2], inplace=True)
        fb.rename(columns=key_dict_fb, inplace=True)
        fb.reset_index(drop=True, inplace=True)
        fb['Date'] = pd.to_datetime(fb['Date']) + pd.offsets.MonthEnd(0) 
        fb_sg = fb[['Date', 'Singapore1', 'Singapore2', 'Singapore3']]
        fb_sg['Date'] = pd.to_datetime(fb_sg['Date']) + pd.offsets.MonthEnd(0) 
        fb_sg['Nonfinancials'] = fb_sg['Singapore2'] - fb_sg['Singapore3']
        fb_sg['weigths_financial'] = fb_sg['Singapore3'] / fb_sg['Singapore2']
        fb_sg['weigths_nonfinancial'] = fb_sg['Nonfinancials'] / fb_sg['Singapore2']
        fb_sg['Price_Growth'] = ((fb_sg['Singapore1'] / fb_sg['Singapore1'].shift(1))-1) * 100
        fb_sg['Financial_Growth'] = fb_sg['Price_Growth'] * fb_sg['weigths_financial']
        fb_sg['Financial Index - SG'] = np.nan
        fb_sg.reset_index(drop=True, inplace=True)
        fb_sg.at[0, 'Financial Index - SG'] = 100

        set_base_sg = pd.to_datetime('2008-12-01') + pd.offsets.MonthEnd(0)
        for i in range(1, len(fb_sg)):
            if set_base_sg is not None:
                if fb_sg.at[i, 'Date'] == set_base_sg: # set when the base date 
                    fb_sg.at[i, 'Financial Index - SG'] = 100
                else:
                    fb_sg.at[i, 'Financial Index - SG'] = fb_sg.at[i-1, 'Financial Index - SG'] * ((fb_sg.at[i, 'Financial_Growth'] / 100) + 1)
            else:
                fb_sg.at[i, 'Financial Index - SG'] = fb_sg.at[i-1, 'Financial Index - SG'] * ((fb_sg.at[i, 'Financial_Growth'] / 100) + 1)

        fb_th = fb[['Date', 'Thailand1', 'Thailand2', 'Thailand3', 'Thailand4', 'Thailand5', 'Thailand6']]
        fb_th['Date'] = pd.to_datetime(fb_th['Date']) + pd.offsets.MonthEnd(0) 
        fb_th['growth_banking'] = ((fb_th['Thailand1'] / fb_th['Thailand1'].shift(1))-1) * 100
        fb_th['growth_finance'] = ((fb_th['Thailand2'] / fb_th['Thailand2'].shift(1))-1) * 100
        fb_th['growth_insurance'] = ((fb_th['Thailand3'] / fb_th['Thailand3'].shift(1))-1) * 100   
        fb_th['weight_banking'] = fb_th['Thailand4'] / (fb_th['Thailand4'] + fb_th['Thailand5'] + fb_th['Thailand6'])
        fb_th['weight_finance'] = fb_th['Thailand5'] / (fb_th['Thailand4'] + fb_th['Thailand5'] + fb_th['Thailand6'])
        fb_th['weight_insurance'] = fb_th['Thailand6'] / (fb_th['Thailand4'] + fb_th['Thailand5'] + fb_th['Thailand6'])
        fb_th['financial_growth'] = fb_th['growth_banking'] * fb_th['weight_banking']  + fb_th['growth_finance'] * fb_th['weight_finance'] + fb_th['growth_insurance'] * fb_th['weight_insurance']
        fb_th['Financial Index - TH'] = np.nan
        fb_th.reset_index(drop=True, inplace=True)
        fb_th.at[0, 'Financial Index - TH'] = 100

        set_base_th = None
        for i in range(1, len(fb_th)):
            if set_base_th is not None:
                if fb_th.at[i, 'Date'] == pd.to_datetime('2008-12-01') + pd.offsets.MonthEnd(0): # set when the base date 
                    fb_th.at[i, 'Financial Index - TH'] = 100
                else:
                    fb_th.at[i, 'Financial Index - TH'] = fb_th.at[i-1, 'Financial Index - TH'] * ((fb_th.at[i, 'financial_growth'] / 100) + 1)
            else:
                fb_th.at[i, 'Financial Index - TH'] = fb_th.at[i-1, 'Financial Index - TH'] * ((fb_th.at[i, 'financial_growth'] / 100) + 1)

        fb_id_index = fb['Indonesia1'].isna().idxmax()
        fb_id1 = fb[['Date', 'Indonesia1']]
        fb_id1 = fb_id1[fb_id1.index < fb_id_index]
        fb_id2 = fb[['Date', 'Indonesia2']]
        fb_id2 = fb_id2[fb_id2.index >= fb_id_index]
        fb_id1.rename(columns={'Indonesia1': 'Indonesia'}, inplace=True)
        fb_id2.rename(columns={'Indonesia2': 'Indonesia'}, inplace=True)
        fb_id = pd.concat([fb_id1, fb_id2])

        fb_compile = pd.concat([fb[['Date', 'China', 'Hong Kong SAR (China)', 'India']], fb_id[['Indonesia']], fb[['Malaysia', 'Philippines']], fb_sg[['Financial Index - SG']], fb[['South Korea', 'Taiwan']], fb_th[['Financial Index - TH']]], axis=1)
        fb_compile.set_index('Date', inplace=True)
        fb_compile.rename(columns={'Financial Index - SG': 'Singapore', 'Financial Index - TH': 'Thailand'}, inplace=True)
        fb_compile = fb_compile.astype(float)

        fb_compile_calc = fb_compile.apply(lambda x : np.log(x))
        fb_compile_calc = (fb_compile_calc.shift(1) - fb_compile_calc) * 100
        fb_compile_calc['Asia'] = fb_compile_calc.mean(axis=1)

        covariance = pd.DataFrame(index=stock_data_calc.index, columns=stock_data_calc.columns)
        date_dict = {k:v for k,v in enumerate(stock_data_calc.index)}
        for x in stock_data_calc.columns:
            for i in range(1, len(stock_data_calc)-12):
                covariance.at[date_dict[i+12], x] = np.cov(stock_data_calc.loc[date_dict[i]:date_dict[i+12], x].values, fb_compile_calc.loc[date_dict[i]:date_dict[i+12], x].values, bias=True)[0, 1]

        variance = pd.DataFrame(index=stock_data_calc.index, columns=stock_data_calc.columns)
        for x in stock_data_calc.columns:
            for i in range(1, len(stock_data_calc)-12):
                variance.at[date_dict[i+12], x] = np.var(stock_data_calc.loc[date_dict[i]:date_dict[i+12], x].values, ddof=1)

        financial_sector_beta = covariance / variance
        financial_sector_beta = (financial_sector_beta - financial_sector_beta.mean()) / financial_sector_beta.std()
        financial_sector_beta = financial_sector_beta.applymap(lambda x: x if x > 1 else 0)

        country_list = ['Region', 'China', 'Hong Kong SAR (China)', 'India', 'Indonesia', 'Malaysia', 'Philippines', 'Singapore', 'South Korea', 'Taiwan', 'Thailand']
        fx = pd.read_excel(r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Financial Stress Indices.xlsx', sheet_name='FX', header=1)
        fx.drop([0,1], inplace=True)
        fx = fx[country_list]
        fx.rename(columns={'Region': 'Date'}, inplace=True)
        fx["Date"] = pd.to_datetime(fx["Date"]) + pd.offsets.MonthEnd(0) 
        fx.set_index('Date', inplace=True) 
        fx = fx.loc[fx.index >= "2009-12-31"]
        fx = fx.astype(float)
        fx = ((fx / fx.shift(1))-1) * 100
        fx['Asia'] = fx.mean(axis=1)
        fx = (fx - fx.mean())/fx.std()

        ora = pd.read_excel(r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Financial Stress Indices.xlsx', sheet_name='ORA', header=1)
        ora.drop([0,1], inplace=True)
        ora = ora[country_list]
        ora.rename(columns={'Region': 'Date'}, inplace=True)
        ora["Date"] = pd.to_datetime(ora["Date"]) + pd.offsets.MonthEnd(0)
        ora.set_index('Date', inplace=True)
        ora = ora.loc[ora.index >= "2009-12-31"]
        ora = ora.astype(float)
        ora = ora/1000
        ora = ((ora.shift(1) / ora)-1) * 100
        ora['Asia'] = ora.mean(axis=1)
        ora = (ora - ora.mean())/ora.std()

        empi = fx - ora
        yield_data_calc = yield_data_calc[stock_data_calc2.columns]

        si_dict = stock_data_calc2.to_dict('list')
        for x in si_dict:
            am = arch_model(si_dict[x], lags=1, vol='GARCH', p=1, q=1) ##need to review maybe mean = 'AR'
            res = am.fit(disp='off')
            conditional_volatility = res.conditional_volatility
            conditional_variance = conditional_volatility**2
            si_dict[x] = conditional_variance

        garch = pd.DataFrame(si_dict)
        garch.set_index(stock_data_calc2.index, inplace=True)
        garch = (garch - garch.mean()) / garch.std()

        stock_data_calc2 = stock_data_calc2.loc[stock_data_calc2.index >= "2010-01-01"]
        empi = empi.loc[empi.index >= "2010-01-01"]
        financial_sector_beta = financial_sector_beta.loc[financial_sector_beta.index >= "2010-01-01"]
        garch = garch.loc[garch.index >= "2010-01-01"]
        yield_data_calc.fillna(0, inplace=True)

        fsi = yield_data_calc + stock_data_calc2 + empi + financial_sector_beta + garch
        fsi['Asia Advanced Economies'] = fsi[['Hong Kong SAR (China)', 'Singapore', 'South Korea', 'Taiwan']].mean(axis=1)
        fsi['ASEAN-4'] = fsi[['Indonesia', 'Malaysia', 'Philippines', 'Thailand']].mean(axis=1)
        

        return yield_data_calc, stock_data_calc2, empi, financial_sector_beta, garch, fsi

    def sovereign_bond_yields(self) -> pd.DataFrame:
        df1 = pd.read_excel(
            r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx",
            sheet_name='Yields YTD',
            header=1,
        )
        df2 = df1.drop([0, 1, 2]).reset_index(drop=True)
        nan_ind = df2['.DESC'].isna().idxmax()
        if nan_ind > 0:
            df2 = df2.iloc[0:nan_ind]
        col_rename = {x: x.split(':')[0] for x in df2.columns[1:]}
        col_rename['.DESC'] = 'Date'
        df2.rename(columns=col_rename, inplace=True)
        df2['Date'] = pd.to_datetime(df2['Date']) + pd.offsets.MonthEnd(0)
        df2 = df2[df2['Date'] >= '2021-01-31']
        df2.fillna(0, inplace=True)
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2["Date"] = pd.to_datetime(df2["Date"]) + pd.offsets.MonthEnd(0)
        df2["Year"] = df2["Date"].apply(lambda x: x.date().strftime("%Y"))
        df2["Date2"] = df2["Date"].apply(lambda x: x.date().strftime("%Y-%m"))
        year_now = datetime.date.today().year
        year2 = [str(x) for x in range(2021, year_now + 1)]
        latest_year = int(sorted(df2["Year"].unique())[-1])
        country = df2["Region"].unique()
        df2 = sqldf(
            f'select Date2 as Date, Year, Region, Value, row_number() over(partition by Region, Year order by Date2) as row_num from df2 where Year in ("{'", "'.join(year2)}")'
        )

        df2 = df2.groupby("Year").apply(
            lambda x: x[x["row_num"].isin([x["row_num"].min(), x["row_num"].max()])]
        )
        year2 = df2['Year'].unique()
        df2.reset_index(drop=True, inplace=True)

        calc_country = dict()

        for x in country:
            for y in year2:
                if len(df2[(df2["Region"] == x) & (df2["Year"] == str(y))]) == 1:
                    continue
                df_temp = df2[
                            (df2["Region"] == x)
                            & (df2["Year"] == str(y))
                        ]
                nomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].min())
                    ]["Value"].values[0]
                )
                denomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].max())
                    ]["Value"].values[0]
                )
                calc = 0 if nomi == 0 and denomi == 0 else denomi - nomi
                if calc_country.get(x) == None:
                    calc_country.update({x: {y: calc}})
                else:
                    calc_country[x].update({y: calc})

        df = pd.DataFrame(calc_country).reset_index()
        df = df.melt(id_vars="index", var_name="Region", value_name="Value").rename(
            {"index": "Year"}, axis=1
        )
        region_sort = list(
            df[(df["Year"] == df["Year"].unique()[-1])].sort_values(
                by="Value", ascending=False
            )["Region"]
        )
        df["Region"] = pd.Categorical(
            df["Region"], categories=region_sort, ordered=True
        )
        df = df.sort_values(by=["Region", "Year"], ascending=False)
        return df 

    def stock_price_index(self) -> pd.DataFrame:
        df = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Capital Flow Monitor\SEACEN CFM January 2025\edited files\Data\Section 1 Charts.xlsx",
            sheet_name='stock indices',
            header=2)
        df2 = df.drop([0,1])
        df2.drop(columns=['Unnamed: 11', 'Unnamed: 12', '.T1'], inplace=True)
        df2.rename(columns={'Dec-2006': 'Vietnam', 'Region': 'Date'}, inplace=True)
        df2.reset_index(drop=True,inplace=True)
        df2 = df2.iloc[:df2['Date'].isna().idxmax()]
        df2 = df2.melt(id_vars="Date", var_name="Region", value_name="Value")
        df2["Date"] = pd.to_datetime(df2["Date"]) + pd.offsets.MonthEnd(0)
        df2["Year"] = df2["Date"].apply(lambda x: x.date().strftime("%Y"))
        df2["Date2"] = df2["Date"].apply(lambda x: x.date().strftime("%Y-%m"))
        year_now = datetime.date.today().year
        year2 = [str(x) for x in range(2020, year_now + 1)]
        country = df2["Region"].unique()
        df2 = sqldf(
                    f'select Date2 as Date, Year, Region, Value, row_number() over(partition by Region, Year order by Date2) as row_num from df2 where Year in ("{'", "'.join(year2)}")'
                )
        df2 = df2.groupby("Year").apply(
                    lambda x: x[x["row_num"].isin([x["row_num"].min(), x["row_num"].max()])]
                )
        year2 = df2['Year'].unique() ## add this in fx
        df2.reset_index(drop=True, inplace=True)
        df2.fillna(0, inplace=True)
        calc_country = dict()

        for x in country:
            for y in year2:
                if len(df2[(df2["Region"] == x) & (df2["Year"] == str(y))]) == 1:
                    continue
                df_temp = df2[
                    (df2["Region"] == x)
                    & (df2["Year"] == str(y))
                ]
                denomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].min())
                    ]["Value"].values[0]
                )
                nomi = float(
                    df_temp[(df_temp["row_num"] == df_temp["row_num"].max())
                    ]["Value"].values[0]
                )
                calc = 0 if nomi == 0 and denomi == 0 else ((nomi / denomi) - 1) * 100
                if calc_country.get(x) == None:
                    calc_country.update({x: {y: calc}})
                else:
                    calc_country[x].update({y: calc})

        df3 = pd.DataFrame(calc_country).reset_index()
        df3 = df3.melt(id_vars="index", var_name="Region", value_name="Value").rename(
            {"index": "Year"}, axis=1
        )
        region_sort = list(
            df3[(df3["Year"] == df3["Year"].unique()[-1])].sort_values(
                by="Value", ascending=False
            )["Region"]
        )
        df3["Region"] = pd.Categorical(
            df3["Region"], categories=region_sort, ordered=True
        )
        df3 = df3.sort_values(by=["Region", "Year"], ascending=False)
        return df3
    
    def capital_flows(self) -> pd.DataFrame:
        file_url = 'https://www.iif.com/Portals/0/Files/Databases/monthly_em_portfolio_flows_database.xlsx?ver=2025-03-13-063222-833'
        response = requests.get(file_url)

        if response.headers.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            excel_data = BytesIO(response.content)
            df = pd.read_excel(excel_data, sheet_name='Country Flows_nw', header=3)
        else:
            print("Failed to download a valid Excel file. The URL might not be a direct link.")
        
        equity = df[df.columns[[0,1,3,5,7,9,11,13,14,16,45,60]]]
        equity.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
        equity['Date'].fillna(0, inplace=True)
        date_new = [x for x in equity['Date'] if isinstance(x, datetime.date)]
        equity = equity[equity['Date'].isin(date_new)]

        debt = df[df.columns[[0,2,4,6,8,10,12,15,61]]]
        debt.rename(columns={'Unnamed: 0': 'Date'}, inplace=True)
        debt['Date'].fillna(0, inplace=True)
        date_new = [x for x in debt['Date'] if isinstance(x, datetime.date)]
        debt = debt[debt['Date'].isin(date_new)]
        debt.rename(columns={k:v for (k,v) in zip(debt.columns, equity.columns.drop(['Taiwan, China', 'Vietnam', 'Sri lanka']))}, inplace=True)

        equity.set_index('Date', inplace=True)
        debt.set_index('Date', inplace=True)

        df_cf = pd.DataFrame(index=debt.index)

        df_cf['Portfolio Debt'] = debt.sum(axis=1)/1000
        df_cf['Portfolio Equity'] = equity.sum(axis=1)/1000
        df_cf.reset_index(inplace=True)
        return df_cf

    def all_df(self) -> dict[str, pd.DataFrame]:
        """Get all dataframes as a dictionary."""
        vix = self.vix_history()
        policy_rate1, policy_rate2, policy_rate3 = self.policy_rate()
        monthly_inflation1, monthly_inflation2, monthly_inflation3 = (
            self.monthly_inflation()
        )
        forex_exchange = self.forex_exchange()
        cds = self.cds()
        df_dict = {
            "vix": vix,
            "policy_rate1": policy_rate1,
            "policy_rate2": policy_rate2,
            "policy_rate3": policy_rate3,
            "monthly_inflation1": monthly_inflation1,
            "monthly_inflation2": monthly_inflation2,
            "monthly_inflation3": monthly_inflation3,
            "forex_exchange": forex_exchange,
            "cds": cds,
        }
        return df_dict