import pandas as pd
from datetime import datetime
import os
import warnings

warnings.filterwarnings("ignore")

def bop_quarterly() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_init = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='BoP edit')

    path_dict = dict()
    list_1 = ['IMF BOP Annual.xlsx', 'IMF BOP Quarterly.xlsx']
    # directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    for filename in os.listdir(directory_path):
        if filename in ['01 Emerging Market', '02 G7 Countries']:
            continue
        file_path = os.path.join(directory_path, filename)
        list_temp = []
        for filename2 in os.listdir(file_path):
            if any(word in str(filename2) for word in list_1):            
                list_temp.append(filename2)
                path_dict[filename] = list_temp
            else:
                continue

    df_path = []
    for k, v in path_dict.items():
        df_path.append(os.path.join(directory_path, k, v[1]))
        print(v[1]) ## to check the file name

    df_all_annual = pd.DataFrame()
    for x, y in enumerate(df_path):
        df = pd.read_excel(y)
        df = df[df[df.columns[0]].isin(df_init['desc'])]
        df_all_annual = pd.concat([df_all_annual, df]) 

    df_all_annual.rename(columns={df_all_annual.columns[0]: 'Type'}, inplace=True)

    df_all_annual_2 = df_all_annual[df_all_annual.columns[:4].to_list() + [dt for dt in df_all_annual.columns[4:].sort_values(ascending=True).to_list() if dt >= datetime(2019, 1, 1)]]

    def sg_row(df:pd.DataFrame, main:bool = True) -> pd.DataFrame:
        var = df.columns[:4] if main else df.columns[4:]
        return df[var]

    sg_add = {
    'FDI Assets':{'FDI Equity Assets': 0.74,'FDI Debt Assets': 0.26},
    'FDI Liabilities': {'FDI Equity Liabilities': 0.85,'FDI Debt Liabilities': 0.15},
    'Portfolio Assets': {'Portfolio Equity Assets': 0.57, 'Portfolio Debt Assets': 0.43}, 
    'Portfolio Liabilities': {'Portfolio Equity Liabilities': 0.67, 'Portfolio Debt Liabilities': 0.33},
    'Other Investment Assets': {'Currency and Deposits Assets': 0.5, 'Loans Assets': 0.29, 'Insurance and Pension Assets': 0.02, 'Trade Credits and Advances Assets': 0.09, 'OI Others Assets': 0.1},
    'Other Investment Liabilities': {'Currency and Deposits Liabilities': 0.5, 'Loans Liabilities': 0.29, 'Insurance and Pension Liabilities': 0.02, 'Trade Credits and Advances Liabilities': 0.09, 'OI Others Liabilities': 0.1},
    }

    m = df_all_annual_2[(df_all_annual_2['Region']== 'Singapore')]['Type'].to_list()
    df_init[(df_init['desc'].isin(m))]['group'].unique().tolist()

    sg_item = [ 'BoP: Financial Account: Direct Investment: Assets',
                'BoP: Financial Account: Direct Investment: Liabilities',
                'BoP: Financial Account: Portfolio Investment: Assets',
                'BoP: Financial Account: Portfolio Investment: Liabilities',
                'BoP: Financial Account: Other Investment: Assets',
                'BoP: Financial Account: Other Investment: Liabilities']

    sg_df = pd.DataFrame(columns=df_all_annual_2.columns)

    # ensure the zip between sg_item and sg_add is correct
    for x, y in zip(sg_item, sg_add.values()):
        multiplier = list(y.values())
        row_type = list(y.keys())
        df_temp = df_all_annual_2[(df_all_annual_2['Type'] == x) &(df_all_annual_2['Region']== 'Singapore')]
        # print(multiplier, row_type)
        for n in range(len(row_type)):
            col1 = sg_row(df_temp, main=True)
            col1.iat[0, 0] = list(df_init[(df_init['short_title']==row_type[n])]['desc'])[0]
            col2 = sg_row(df_temp, main=False) * multiplier[n]
            merged = pd.concat([col1, col2], axis=1)
            sg_df = pd.concat([sg_df, merged], axis=0)

    df_init_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='Taiwan BoP')
    df_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data\Chinese Taipei (Taiwan) (TW)\TW CB BOP Quarterly.xlsx")
    df_tw.rename(columns={df_tw.columns[0]: 'Type'}, inplace=True)
    df_tw = df_tw[df_tw['Type'].isin(df_init_tw['desc'])]

    for x, y in enumerate(df_tw['Type'].to_list()):
        df_tw.iat[x,0] = list(df_init_tw[(df_init_tw['desc'] == y)]['desc2'])[0]

    selected_columns = [col for col in df_tw.columns[4:] if pd.to_datetime(col) >= datetime(2019, 1, 1)]
    final_columns = list(df_tw.columns[:4]) + selected_columns
    df_tw = df_tw[final_columns]

    # concat to the main df
    df_all_annual_2 = pd.concat([df_all_annual_2, sg_df, df_tw], axis=0)

    seacen_country = ['Papua New Guinea', 'Vietnam', 'Nepal', 'India', 'Indonesia', 'Laos', 'Sri Lanka', 'Hong Kong SAR (China)', 'Philippines', 'Taiwan', 'Malaysia', 'Mongolia', 'China', 'Cambodia', 'Thailand', 'Singapore', 'South Korea', 'Brunei', 'Myanmar']

    for x in df_all_annual_2['Type'].values:
        var1 = list(set(df_all_annual_2[(df_all_annual_2['Type'] == x)]['Region'].values).symmetric_difference(set(seacen_country)))
        if len(var1) > 0:
            for y in var1:
                df_temp1 = pd.DataFrame({"Type": [x], "Region": [y]})
                df_all_annual_2 = pd.concat([df_all_annual_2, df_temp1], axis=0)
        else:
            continue
    df_all_annual_2.replace('South Korea', 'Korea', inplace=True)
    df_all_annual_2.sort_values(by=['Type', 'Region'], inplace=True)
    df_all_annual_2.reset_index(drop=True, inplace=True)

    init_dict = df_init.to_dict()
    df_dict = dict()
    for x in init_dict['desc'].values():
        df_temp = df_all_annual_2[(df_all_annual_2[df_all_annual_2.columns[0]] == x)].reset_index(drop=True)
        df_dict[x] = df_temp

    # calculate the sum of the columns (1H and 2H) for each year
    num1, num2 = 0, 1
    df_col = df_all_annual_2.columns[4:][:-1]
    df_temp_col_1 = df_all_annual_2[df_all_annual_2.columns[:4]].reset_index(drop=True)

    for x in range(len(df_col)//2):
        df_col_temp = (df_all_annual_2[df_col[num1]] + df_all_annual_2[df_col[num1 + 1]]).div(1000)
        year = df_col[num1].year
        df_col_temp.reset_index(drop=True, inplace=True)
        df_temp_col_1[f'{num2}H{year}'] = df_col_temp
        num1 += 2
        num2 += 1
        if num2 == 3:
            num2 = 1

    df_temp_col_1.drop(columns=['Last Update Time', 'Unit'], inplace=True)

    calc_dict = {'Asia-Pacific': seacen_country,
             'Asian Advance Economies': ['Hong Kong SAR (China)', 'South Korea', 'Singapore', 'Taiwan'],
             'ASEAN5 Economies': ['Indonesia', 'Malaysia', 'Philippines', 'Thailand', 'Vietnam'],
             'Asian EDMEs': ['Brunei', 'Cambodia', 'Laos', 'Mongolia', 'Nepal', 'Sri Lanka', 'Papua New Guinea', 'Myanmar'],
             'China': ['China'],
             'India': ['India'],
             }

    ###################### this is for equity ######################

    asset_row = df_init.iloc[[0,4,5,6, 8, 9,10,11,12,13,14]]['desc'].to_list()
    asset_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Receivable','Reserve Assets', ]
    sum_rows = df_init[(df_init['short_title'].isin(['OI Equity Assets','Insurance and Pension Assets','OI Others Assets',]))]['desc'].to_list()
    order = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments','Reserve Assets',]
    df_by_region_main = pd.DataFrame(columns=df_temp_col_1.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_temp_col_1[(df_temp_col_1['Region'].isin(y)) & (df_temp_col_1['Type'].isin(asset_row))]
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(asset_row, asset_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order)}))
        df_by_region_temp['Region'] = x

        df_by_region_main = pd.concat([df_by_region_main, df_by_region_temp], axis = 0)  


    df_by_region_main.reset_index(inplace = True, drop=True)
    df_by_region_main.insert(loc=0, column='Group', value='Assets')

    ###################### this is for equity ######################

    ###################### this is for debt ######################

    debt_row = df_init.iloc[[20,24,25,26,28,29,30,31,32,33,34]]['desc'].to_list()
    debt_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Payable','SDR Liabilities', ]
    sum_rows2 = df_init[(df_init['short_title'].isin(['OI Equity Liabilities', 'Insurance and Pension Liabilities', 'OI Others Liabilities', 'SDR Liabilities']))]['desc'].to_list()
    order2 = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments']
    df_by_region_main2 = pd.DataFrame(columns=df_temp_col_1.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_temp_col_1[(df_temp_col_1['Region'].isin(y)) & (df_temp_col_1['Type'].isin(debt_row))]
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows2].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows2))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(debt_row, debt_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order2)}))
        df_by_region_temp['Region'] = x

        df_by_region_main2 = pd.concat([df_by_region_main2, df_by_region_temp], axis = 0)  

    df_by_region_main2.reset_index(inplace = True, drop=True)
    df_by_region_main2.insert(loc=0, column='Group', value='Liabilities')

    ###################### this is for debt ######################

    ###################### this is for caq data ######################

    caq_data = df_temp_col_1[(df_temp_col_1['Type'].isin(df_init[(df_init['group'] == 'Current Account')]['desc'].to_list()[1:]))]
    caq_data_calc = caq_data.groupby(['Type']).sum()
    caq_data_calc.loc['Current Account Balance'] = caq_data_calc.sum()
    caq_data_calc['Region'] = 'Asia-Pacific'
    caq_data_calc.reset_index(inplace=True)
    rename_to = ['Goods Trade', 'Services Trade','Primary Income','Secondary Income',]
    rename_from = ['BoP: Current Account: Goods','BoP: Current Account: Services','BoP: Current Account: Primary Income','BoP: Current Account: Secondary Income',]
    caq_data_calc['Type'] = caq_data_calc['Type'].replace(rename_from, rename_to)
    caq_data_calc = caq_data_calc.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(rename_to)}))
    caq_data_calc.reset_index(drop=True, inplace=True)
    caq_data_calc.insert(loc=0, column='Group', value='Current Account')

    ###################### this is for caq data ######################

    df_main = pd.concat([df_by_region_main, df_by_region_main2, caq_data_calc], axis = 0) ## combine
    df_main.reset_index(drop=True, inplace=True)

    return df_temp_col_1, df_all_annual_2, df_main

def bop_annual() -> tuple[pd.DataFrame, pd.DataFrame]:

    df_init = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='BoP edit')

    path_dict = dict()
    list_1 = ['IMF BOP Annual.xlsx', 'IMF BOP Quarterly.xlsx']
    # directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    for filename in os.listdir(directory_path):
        if filename in ['01 Emerging Market', '02 G7 Countries']:
            continue
        file_path = os.path.join(directory_path, filename)
        list_temp = []
        for filename2 in os.listdir(file_path):
            if any(word in str(filename2) for word in list_1):            
                list_temp.append(filename2)
                path_dict[filename] = list_temp
            else:
                continue

    df_path = []
    for k, v in path_dict.items():
        df_path.append(os.path.join(directory_path, k, v[0]))
        print(v[0]) ## to check the file name

    df_all_annual = pd.DataFrame()
    for x, y in enumerate(df_path):
        df = pd.read_excel(y)
        df = df[df[df.columns[0]].isin(df_init['desc'])]
        df_all_annual = pd.concat([df_all_annual, df]) 

    df_all_annual.rename(columns={df_all_annual.columns[0]: 'Type'}, inplace=True)

    df_all_annual_2 = df_all_annual[df_all_annual.columns[:4].to_list() + [dt for dt in df_all_annual.columns[4:].sort_values(ascending=True).to_list() if dt >= datetime(2019, 1, 1)]]

    df_init_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='Taiwan BoP')
    df_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data\Chinese Taipei (Taiwan) (TW)\TW CB BOP Annual.xlsx")
    df_tw = df_tw.applymap(lambda x: x[:x.find(' (f')] if isinstance(x, str) and ' (f' in x else x)
    df_tw.rename(columns={df_tw.columns[0]: 'Type'}, inplace=True)
    df_tw = df_tw[df_tw['Type'].isin(df_init_tw['desc'])]

    for x, y in enumerate(df_tw['Type'].to_list()):
        df_tw.iat[x,0] = list(df_init_tw[(df_init_tw['desc'] == y)]['desc2'])[0]

    selected_columns = [col for col in df_tw.columns[4:] if pd.to_datetime(col) >= datetime(2019, 1, 1)]
    final_columns = list(df_tw.columns[:4]) + selected_columns
    df_tw = df_tw[final_columns]

    # concat to the main df
    df_all_annual_2 = pd.concat([df_all_annual_2, df_tw], axis=0)

    seacen_country = ['Papua New Guinea', 'Vietnam', 'Nepal', 'India', 'Indonesia', 'Laos', 'Sri Lanka', 'Hong Kong SAR (China)', 'Philippines', 'Taiwan', 'Malaysia', 'Mongolia', 'China', 'Cambodia', 'Thailand', 'Singapore', 'South Korea', 'Brunei', 'Myanmar']

    for x in df_all_annual_2['Type'].values:
        var1 = list(set(df_all_annual_2[(df_all_annual_2['Type'] == x)]['Region'].values).symmetric_difference(set(seacen_country)))
        if len(var1) > 0:
            for y in var1:
                df_temp1 = pd.DataFrame({"Type": [x], "Region": [y]})
                df_all_annual_2 = pd.concat([df_all_annual_2, df_temp1], axis=0)
        else:
            continue
    df_all_annual_2.replace('South Korea', 'Korea', inplace=True)
    df_all_annual_2.sort_values(by=['Type', 'Region'], inplace=True)
    df_all_annual_2.reset_index(drop=True, inplace=True)

    init_dict = df_init.to_dict()
    df_dict = dict()
    for x in init_dict['desc'].values():
        df_temp = df_all_annual_2[(df_all_annual_2[df_all_annual_2.columns[0]] == x)].reset_index(drop=True)
        df_dict[x] = df_temp

    calc_dict = {'Asia-Pacific': seacen_country,
                'Asian Advance Economies': ['Hong Kong SAR (China)', 'South Korea', 'Singapore', 'Taiwan'],
                'ASEAN5 Economies': ['Indonesia', 'Malaysia', 'Philippines', 'Thailand', 'Vietnam'],
                'Asian EDMEs': ['Brunei', 'Cambodia', 'Laos', 'Mongolia', 'Nepal', 'Sri Lanka', 'Papua New Guinea', 'Myanmar'],
                'China': ['China'],
                'India': ['India'],
                }

    ###################### this is for equity ######################

    asset_row = df_init.iloc[[0,4,5,6, 8, 9,10,11,12,13,14]]['desc'].to_list()
    asset_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Receivable','Reserve Assets', ]
    sum_rows = df_init[(df_init['short_title'].isin(['OI Equity Assets','Insurance and Pension Assets','OI Others Assets',]))]['desc'].to_list()
    order = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments','Reserve Assets',]
    df_by_region_main = pd.DataFrame(columns=df_all_annual_2.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_all_annual_2[(df_all_annual_2['Region'].isin(y)) & (df_all_annual_2['Type'].isin(asset_row))]
        df_by_region_temp.drop(columns=['Last Update Time', 'Region', 'Unit'], inplace=True)
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(asset_row, asset_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order)}))
        df_by_region_temp['Region'] = x

        df_by_region_main = pd.concat([df_by_region_main, df_by_region_temp], axis = 0)  


    df_by_region_main.reset_index(inplace = True, drop=True)
    df_by_region_main.insert(loc=0, column='Group', value='Assets')

    ###################### this is for equity ######################

    ###################### this is for debt ######################

    debt_row = df_init.iloc[[20,24,25,26,28,29,30,31,32,33,34]]['desc'].to_list()
    debt_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Payable','SDR Liabilities', ]
    sum_rows2 = df_init[(df_init['short_title'].isin(['OI Equity Liabilities', 'Insurance and Pension Liabilities', 'OI Others Liabilities', 'SDR Liabilities']))]['desc'].to_list()
    order2 = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments']
    df_by_region_main2 = pd.DataFrame(columns=df_all_annual_2.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_all_annual_2[(df_all_annual_2['Region'].isin(y)) & (df_all_annual_2['Type'].isin(debt_row))]
        df_by_region_temp.drop(columns=['Last Update Time', 'Region', 'Unit'], inplace=True)
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows2].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows2))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(debt_row, debt_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order2)}))
        df_by_region_temp['Region'] = x

        df_by_region_main2 = pd.concat([df_by_region_main2, df_by_region_temp], axis = 0)  

    df_by_region_main2.reset_index(inplace = True, drop=True)
    df_by_region_main2.insert(loc=0, column='Group', value='Liabilities')

    ###################### this is for debt ######################

    ###################### this is for caq data ######################

    caq_data = df_all_annual_2[(df_all_annual_2['Type'].isin(df_init[(df_init['group'] == 'Current Account')]['desc'].to_list()[1:]))]
    caq_data.drop(columns=['Last Update Time', 'Region', 'Unit'], inplace=True)
    caq_data_calc = caq_data.groupby(['Type']).sum()
    caq_data_calc.loc['Current Account Balance'] = caq_data_calc.sum()
    caq_data_calc['Region'] = 'Asia-Pacific'
    caq_data_calc.reset_index(inplace=True)
    rename_to = ['Goods Trade', 'Services Trade','Primary Income','Secondary Income',]
    rename_from = ['BoP: Current Account: Goods','BoP: Current Account: Services','BoP: Current Account: Primary Income','BoP: Current Account: Secondary Income',]
    caq_data_calc['Type'] = caq_data_calc['Type'].replace(rename_from, rename_to)
    caq_data_calc = caq_data_calc.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(rename_to)}))
    caq_data_calc.reset_index(drop=True, inplace=True)
    caq_data_calc.insert(loc=0, column='Group', value='Current Account')

    ###################### this is for caq data ######################

    df_main = pd.concat([df_by_region_main, df_by_region_main2, caq_data_calc], axis = 0) ## combine
    df_main.reset_index(drop=True, inplace=True)

    return df_all_annual_2, df_main

def iip_quarterly() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_init = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='IIP edit')

    path_dict = dict()
    list_1 = ['IMF IIP Annual.xlsx', 'IMF IIP Quarterly.xlsx']
    # directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    directory_path= r'C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    for filename in os.listdir(directory_path):
        if filename in ['01 Emerging Market', '02 G7 Countries']:
            continue
        file_path = os.path.join(directory_path, filename)
        list_temp = []
        for filename2 in os.listdir(file_path):
            if any(word in str(filename2) for word in list_1):            
                list_temp.append(filename2)
                path_dict[filename] = list_temp
            else:
                continue

    df_path = []
    for k, v in path_dict.items():
        df_path.append(os.path.join(directory_path, k, v[1]))
        print(v[1]) ## to check the file name

    df_all_annual = pd.DataFrame()
    for x, y in enumerate(df_path):
        df = pd.read_excel(y)
        df = df[df[df.columns[0]].isin(df_init['desc'])]
        df_all_annual = pd.concat([df_all_annual, df]) 

    df_all_annual.rename(columns={df_all_annual.columns[0]: 'Type'}, inplace=True)

    df_all_annual_2 = df_all_annual[df_all_annual.columns[:4].to_list() + [dt for dt in df_all_annual.columns[4:].sort_values(ascending=True).to_list() if dt >= datetime(2019, 1, 1)]]

    df_init_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='Taiwan IIP')
    df_tw = pd.read_excel(r"C:\Users\AhmadAizudeen\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data\Chinese Taipei (Taiwan) (TW)\TW CB IIP Annual.xlsx")
    df_tw.rename(columns={df_tw.columns[0]: 'Type'}, inplace=True)
    df_tw = df_tw[df_tw['Type'].isin(df_init_tw['desc'])]

    for x, y in enumerate(df_tw['Type'].to_list()):
        df_tw.iat[x,0] = list(df_init_tw[(df_init_tw['desc'] == y)]['desc2'])[0]

    selected_columns = [col for col in df_tw.columns[4:] if pd.to_datetime(col) >= datetime(2019, 1, 1)]
    final_columns = list(df_tw.columns[:4]) + selected_columns
    df_tw = df_tw[final_columns]

    # concat to the main df
    df_all_annual_2 = pd.concat([df_all_annual_2, df_tw], axis=0)

    seacen_country = ['Papua New Guinea', 'Vietnam', 'Nepal', 'India', 'Indonesia', 'Laos', 'Sri Lanka', 'Hong Kong SAR (China)', 'Philippines', 'Taiwan', 'Malaysia', 'Mongolia', 'China', 'Cambodia', 'Thailand', 'Singapore', 'South Korea', 'Brunei', 'Myanmar']

    for x in df_all_annual_2['Type'].values:
        var1 = list(set(df_all_annual_2[(df_all_annual_2['Type'] == x)]['Region'].values).symmetric_difference(set(seacen_country)))
        if len(var1) > 0:
            for y in var1:
                df_temp1 = pd.DataFrame({"Type": [x], "Region": [y]})
                df_all_annual_2 = pd.concat([df_all_annual_2, df_temp1], axis=0)
        else:
            continue

    df_all_annual_2.sort_values(by=['Type', 'Region'], inplace=True)
    df_all_annual_2.reset_index(drop=True, inplace=True)

    init_dict = df_init.to_dict()
    df_dict = dict()
    for x in init_dict['desc'].values():
        df_temp = df_all_annual_2[(df_all_annual_2[df_all_annual_2.columns[0]] == x)].reset_index(drop=True)
        df_dict[x] = df_temp

    # calculate the sum of the columns (1H and 2H) for each year
    num1, num2 = 0, 1
    df_col = df_all_annual_2.columns[4:][:-1]
    df_temp_col_1 = df_all_annual_2[df_all_annual_2.columns[:4]].reset_index(drop=True)

    for x in range(len(df_col)//2):
        df_col_temp = (df_all_annual_2[df_col[num1]] + df_all_annual_2[df_col[num1 + 1]]).div(1000)
        year = df_col[num1].year
        df_col_temp.reset_index(drop=True, inplace=True)
        df_temp_col_1[f'{num2}H{year}'] = df_col_temp
        num1 += 2
        num2 += 1
        if num2 == 3:
            num2 = 1

    df_temp_col_1.drop(columns=['Last Update Time', 'Unit'], inplace=True)

    calc_dict = {'Asia-Pacific': seacen_country,
             'Asian Advance Economies': ['Hong Kong SAR (China)', 'South Korea', 'Singapore', 'Taiwan'],
             'ASEAN5 Economies': ['Indonesia', 'Malaysia', 'Philippines', 'Thailand', 'Vietnam'],
             'Asian EDMEs': ['Brunei', 'Cambodia', 'Laos', 'Mongolia', 'Nepal', 'Sri Lanka', 'Papua New Guinea', 'Myanmar'],
             'China': ['China'],
             'India': ['India'],
             }

    ###################### this is for equity ######################

    asset_row = df_init.iloc[[0,4,5,6, 8, 9,10,11,12,13,14]]['desc'].to_list()
    asset_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Receivable','Reserve Assets', ]
    sum_rows = df_init[(df_init['short_title'].isin(['OI Equity Assets','Insurance and Pension Assets','OI Others Assets',]))]['desc'].to_list()
    order = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments','Reserve Assets',]
    df_by_region_main = pd.DataFrame(columns=df_temp_col_1.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_temp_col_1[(df_temp_col_1['Region'].isin(y)) & (df_temp_col_1['Type'].isin(asset_row))]
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(asset_row, asset_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order)}))
        df_by_region_temp['Region'] = x

        df_by_region_main = pd.concat([df_by_region_main, df_by_region_temp], axis = 0)  


    df_by_region_main.reset_index(inplace = True, drop=True)
    df_by_region_main.insert(loc=0, column='Group', value='Assets')

    ###################### this is for equity ######################

    ###################### this is for debt ######################

    debt_row = df_init.iloc[[20,24,25,26,28,29,30,31,32,33,34]]['desc'].to_list()
    debt_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Payable','SDR Liabilities', ]
    sum_rows2 = df_init[(df_init['short_title'].isin(['OI Equity Liabilities', 'Insurance and Pension Liabilities', 'OI Others Liabilities', 'SDR Liabilities']))]['desc'].to_list()
    order2 = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments']
    df_by_region_main2 = pd.DataFrame(columns=df_temp_col_1.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_temp_col_1[(df_temp_col_1['Region'].isin(y)) & (df_temp_col_1['Type'].isin(debt_row))]
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows2].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows2))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(debt_row, debt_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order2)}))
        df_by_region_temp['Region'] = x

        df_by_region_main2 = pd.concat([df_by_region_main2, df_by_region_temp], axis = 0)  

    df_by_region_main2.reset_index(inplace = True, drop=True)
    df_by_region_main2.insert(loc=0, column='Group', value='Liabilities')

    ###################### this is for debt ######################

    ###################### this is for caq data ######################

    caq_data = df_temp_col_1[(df_temp_col_1['Type'].isin(df_init[(df_init['group'] == 'Current Account')]['desc'].to_list()[1:]))]
    caq_data_calc = caq_data.groupby(['Type']).sum()
    caq_data_calc.loc['Current Account Balance'] = caq_data_calc.sum()
    caq_data_calc['Region'] = 'Asia-Pacific'
    caq_data_calc.reset_index(inplace=True)
    rename_to = ['Goods Trade', 'Services Trade','Primary Income','Secondary Income',]
    rename_from = ['BoP: Current Account: Goods','BoP: Current Account: Services','BoP: Current Account: Primary Income','BoP: Current Account: Secondary Income',]
    caq_data_calc['Type'] = caq_data_calc['Type'].replace(rename_from, rename_to)
    caq_data_calc = caq_data_calc.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(rename_to)}))
    caq_data_calc.reset_index(drop=True, inplace=True)
    caq_data_calc.insert(loc=0, column='Group', value='Current Account')

    ###################### this is for caq data ######################

    df_main = pd.concat([df_by_region_main, df_by_region_main2, caq_data_calc], axis = 0) ## combine
    df_main.reset_index(drop=True, inplace=True)

    return df_temp_col_1, df_all_annual_2, df_main

def iip_annual():

    df_init = pd.read_excel(r"C:\Users\Admin\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='IIP edit')

    path_dict = dict()
    list_1 = ['IMF IIP Annual.xlsx', 'IMF IIP Quarterly.xlsx']
    # directory_path= r'C:\Users\Admin\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    directory_path= r'C:\Users\Admin\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data'
    for filename in os.listdir(directory_path):
        if filename in ['01 Emerging Market', '02 G7 Countries']:
            continue
        file_path = os.path.join(directory_path, filename)
        list_temp = []
        for filename2 in os.listdir(file_path):
            if any(word in str(filename2) for word in list_1):            
                list_temp.append(filename2)
                path_dict[filename] = list_temp
            else:
                continue

    df_path = []
    for k, v in path_dict.items():
        df_path.append(os.path.join(directory_path, k, v[0]))
        print(v[0]) ## to check the file name

    df_all_annual = pd.DataFrame()
    for x, y in enumerate(df_path):
        df = pd.read_excel(y)
        df = df[df[df.columns[0]].isin(df_init['desc'])]
        df_all_annual = pd.concat([df_all_annual, df]) 

    df_all_annual.rename(columns={df_all_annual.columns[0]: 'Type'}, inplace=True)

    df_all_annual_2 = df_all_annual[df_all_annual.columns[:4].to_list() + [dt for dt in df_all_annual.columns[4:].sort_values(ascending=True).to_list() if dt >= datetime(2019, 1, 1)]]

    df_init_tw = pd.read_excel(r"C:\Users\Admin\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Desktop\NLP Project\cfm-nlp\Automation.xlsx", sheet_name='Taiwan BoP')
    df_tw = pd.read_excel(r"C:\Users\Admin\OneDrive - The SOUTH-EAST ASIAN CENTRAL BANKS (SEACEN) RESEARCH AND TRAINING\Roger and Aizudeen\Country BoP and IIP Data\Chinese Taipei (Taiwan) (TW)\TW CB IIP Annual.xlsx")
    df_tw.rename(columns={df_tw.columns[0]: 'Type'}, inplace=True)
    df_tw = df_tw[df_tw['Type'].isin(df_init_tw['desc'])]

    for x, y in enumerate(df_tw['Type'].to_list()):
        df_tw.iat[x,0] = list(df_init_tw[(df_init_tw['desc'] == y)]['desc2'])[0]

    selected_columns = [col for col in df_tw.columns[4:] if pd.to_datetime(col) >= datetime(2019, 1, 1)]
    final_columns = list(df_tw.columns[:4]) + selected_columns
    df_tw = df_tw[final_columns]

    # concat to the main df
    df_all_annual_2 = pd.concat([df_all_annual_2, df_tw], axis=0)

    seacen_country = ['Papua New Guinea', 'Vietnam', 'Nepal', 'India', 'Indonesia', 'Laos', 'Sri Lanka', 'Hong Kong SAR (China)', 'Philippines', 'Taiwan', 'Malaysia', 'Mongolia', 'China', 'Cambodia', 'Thailand', 'Singapore', 'South Korea', 'Brunei', 'Myanmar']

    for x in df_all_annual_2['Type'].values:
        var1 = list(set(df_all_annual_2[(df_all_annual_2['Type'] == x)]['Region'].values).symmetric_difference(set(seacen_country)))
        if len(var1) > 0:
            for y in var1:
                df_temp1 = pd.DataFrame({"Type": [x], "Region": [y]})
                df_all_annual_2 = pd.concat([df_all_annual_2, df_temp1], axis=0)
        else:
            continue

    df_all_annual_2.sort_values(by=['Type', 'Region'], inplace=True)
    df_all_annual_2.reset_index(drop=True, inplace=True)
    df_all_annual_2.rename(columns={k:v for (k,v) in zip(df_all_annual_2.columns[4:], [x.year for x in df_all_annual_2.columns[4:]])}, inplace=True) ######### only for annnual data, dont use for quarterly data

    init_dict = df_init.to_dict()
    df_dict = dict()
    for x in init_dict['desc'].values():
        df_temp = df_all_annual_2[(df_all_annual_2[df_all_annual_2.columns[0]] == x)].reset_index(drop=True)
        df_dict[x] = df_temp

    calc_dict = {'Asia-Pacific': seacen_country,
             'Asian Advance Economies': ['Hong Kong SAR (China)', 'South Korea', 'Singapore', 'Taiwan'],
             'ASEAN5 Economies': ['Indonesia', 'Malaysia', 'Philippines', 'Thailand', 'Vietnam'],
             'Asian EDMEs': ['Brunei', 'Cambodia', 'Laos', 'Mongolia', 'Nepal', 'Sri Lanka', 'Papua New Guinea', 'Myanmar'],
             'China': ['China'],
             'India': ['India'],
             }

    ###################### this is for equity ######################

    asset_row = df_init.iloc[[0,4,5,6, 8, 9,10,11,12,13,14]]['desc'].to_list()
    asset_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Receivable','Reserve Assets', ]
    sum_rows = df_init[(df_init['short_title'].isin(['OI Equity Assets','Insurance and Pension Assets','OI Others Assets',]))]['desc'].to_list()
    order = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments','Reserve Assets',]
    df_by_region_main = pd.DataFrame(columns=df_all_annual_2.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_all_annual_2[(df_all_annual_2['Region'].isin(y)) & (df_all_annual_2['Type'].isin(asset_row))]
        df_by_region_temp = df_by_region_temp.drop(columns=['Last Update Time', 'Unit']) ############## this is new 
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(asset_row, asset_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order)}))
        df_by_region_temp['Region'] = x

        df_by_region_main = pd.concat([df_by_region_main, df_by_region_temp], axis = 0)  


    df_by_region_main.reset_index(inplace = True, drop=True)
    df_by_region_main.insert(loc=0, column='Group', value='Assets')

    ###################### this is for debt ######################

    debt_row = df_init.iloc[[16,20,21,22,24,25,26,27,28,29,30]]['desc'].to_list()
    debt_row2 = ['Direct Investment', 'Portfolio Equity', 'Portfolio Debt','Financial Derivatives', 'Other Equity','Currency & Deposits','Loans','Insurance, Pension & Standardized Guarantee Schemes'
                ,'Trade Credit & Advances','Other Accounts Payable','SDR Liabilities', ]
    sum_rows2 = df_init[(df_init['short_title'].isin(['OI Equity Liabilities', 'Insurance and Pension Liabilities', 'OI Others Liabilities', 'SDR Liabilities']))]['desc'].to_list()
    order2 = ['Direct Investment','Portfolio Equity','Portfolio Debt','Financial Derivatives','Currency & Deposits','Loans','Trade Credit & Advances','Other Investments']
    df_by_region_main2 = pd.DataFrame(columns=df_all_annual_2.columns)

    for x,y in calc_dict.items():
        # print(x,y)
        df_by_region_temp = df_all_annual_2[(df_all_annual_2['Region'].isin(y)) & (df_all_annual_2['Type'].isin(debt_row))]
        df_by_region_temp = df_by_region_temp.drop(columns=['Last Update Time', 'Unit']) ############## this is new 
        df_by_region_temp = df_by_region_temp.groupby(['Type']).sum()
        df_by_region_temp.loc[str(x) + ' Total'] = df_by_region_temp.sum()
        df_by_region_temp.loc['Other Investments'] = df_by_region_temp.loc[sum_rows2].sum()
        df_by_region_temp.reset_index(inplace = True)
        df_by_region_temp = df_by_region_temp[(~df_by_region_temp['Type'].isin(sum_rows2))] #####  the symbol of '~' use similar like notin, the oposite of isin. this is build in python operator
        df_by_region_temp['Type'] = df_by_region_temp['Type'].replace(debt_row, debt_row2)
        df_by_region_temp = df_by_region_temp.sort_values(by='Type', key=lambda x: x.map({k:i for i, k in enumerate(order2)}))
        df_by_region_temp['Region'] = x

        df_by_region_main2 = pd.concat([df_by_region_main2, df_by_region_temp], axis = 0)  

    df_by_region_main2.reset_index(inplace = True, drop=True)
    df_by_region_main2.insert(loc=0, column='Group', value='Liabilities')

    ###################### this is for debt ######################

    df_main = pd.concat([df_by_region_main, df_by_region_main2], axis = 0) ## combine
    df_main.reset_index(drop=True, inplace=True)

    return df_main