# shiny run --reload --launch-browser cfm-nlp/section2.py
# shiny run --reload --launch-browser section2.py
# SHIFT + END to go to end of line
from shiny import App, ui, render, reactive, req
import pandas as pd
from processed_data import dfs, dfs1, dfs2, dfs3
from faicons import icon_svg as icon

# import shinyswatch
from shinywidgets import render_plotly, output_widget, render_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

all_df = dfs2() # for production
# all_df = dfs3() # for live
years = sorted(set([str(x)[:4] for x in all_df[1].columns[5:].to_list()]))

dict1 = ['Balance of Payment', 'International Investment Position']
dict2 = ['Annually', 'Quarterly', 'Half-Yearly']
dict3 = {'Balance of Payment':['BoP Quarterly', 'BoP Annual'],
         'International Investment Position':['IIP Quarterly', 'IIP Annual']}
dict4 = ['by Region', 'by Category', 'by Country']

capital_flow = all_df[3]["Group"].unique().tolist()
capital_flow2 = ['Resident Capital Flows', 'Non-Resident Capital Flows', 'Current Account']
change = {k:v for k,v in zip(capital_flow, capital_flow2)}

app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        "**Instructions**: to **Select Year(s)**, hold down the Ctrl (windows) or Command (Mac) button to select multiple options."
    ),
    ui.layout_columns(
        ui.div(
            ui.input_select(
                "sc2_df",
                label="Select DataFrame",
                choices=dict1,
                selected=dict1[0],
                # inline=True,
            ),
            ui.input_select(
                "sc2_df2",
                "Select Frequency",
                choices=dict2,
                selected=dict1[0],
                # inline=True,
            ),
            ui.input_select(
                "sc2_df3",
                "Select Segmentation",
                choices=dict4,
                selected=dict1[0],
                # inline=True,
            ),
        class_ = 'hh'
        ),
        ui.input_select(
            "years",
            "Select Year(s)",
            choices=sorted(years, reverse=True),
            selected=years,
            multiple=True,
            size=6,
        ),
        ui.input_select(
            "country",
            # "Select Countries for Segmentation by Country",
            label=ui.tags.span("Select Countries  ",
                                ui.tooltip(
                                    icon("circle-info"),
                                    "for Segmentation by Country filtering."
                                )),
            choices=all_df[0]["Region"].unique().tolist(),
            selected=all_df[0]["Region"].unique().tolist(),
            multiple=True,
            selectize=True,
            width="100%",
        ),
        ui.input_select(
            "types",
            # "Select Type for Segmentation by Country",
            label=ui.tags.span("Select Type  ",
                                ui.tooltip(
                                    icon("circle-info"),
                                    "for Segmentation by Country filtering."
                                )),
            choices=all_df[2],
            # choices=dict1,
            selected='FDI Assets',
            # multiple=True,
        ), 
        ui.input_select(
            "group",
            # "Select Group(s) for DataFrame Balance of Payment",
            label=ui.tags.span("Select Group  ",
                                ui.tooltip(
                                    icon("circle-info"),
                                    "for DataFrame filtering."
                                )),
            choices=capital_flow,
            selected=capital_flow[0],
            # multiple=True,
        ),
        ui.div(
            ui.input_select(
            "region",
            # "Select Region for df_main table",
            label=ui.tags.span("Select Region  ",
                                ui.tooltip(
                                    icon("circle-info"),
                                    'for Segmetation by Region filtering if Multiple Region filter set to "No".'
                                )),
            choices=all_df[3]['Region'].unique().tolist(),
            selected=all_df[3]["Region"].unique().tolist()[0],
            # multiple=True,
            ),
            ui.input_radio_buttons(
                "include_region",
                "Include Multiple Region filter",
                choices={True: "No", False: "Yes"},
                selected=False,
                inline=True,
            ),
        ),
        ui.card(ui.output_data_frame("summary_data"), height="400px"),
        output_widget("hist1"),
        # ui.card(output_widget("country_detail_pop"), height="400px"),
        # ui.card(output_widget("country_detail_percap"), height="400px"),
        col_widths=[2,1,3,2,2,2, 6,6],
        row_heights=["auto", 1],
    ),
)

num=1
def server(input, output, session):
    exclude = ['Asian EDMEs Total', 'India Total', 'China Total', 'Asian Advance Economies Total', 'ASEAN5 Economies Total', 'Asia-Pacific Total']
    exclude2 = {'Last Update Time', 'Unit'}
    def parent_filtered_df(df: pd.DataFrame, input_country: tuple[list|tuple|str]=None, df_int:int=None, include_region: bool=False) -> pd.DataFrame:
        col = df.columns.to_list()
        filt_df = df[df['Group2'].isin(dict3[input.sc2_df()])]        
        if input.sc2_df3() == 'by Country':
            filt_df = filt_df[(df["Region"].isin(input_country)) & (filt_df["Type"].isin([input.types()]))]
        else:
            if not include_region:
                filt_df = filt_df[(filt_df["Region"]==input.region())]
            else:
                filt_df = filt_df[(filt_df['Region'] != 'Asia-Pacific') | (filt_df['Group'] == 'Current Account')]
        # print(filt_df)
        if 'Group' in col:
            filt_df = filt_df[filt_df["Group"]==input.group()]

        if len(filt_df.columns.to_list()) > 3:
            selected_years = [x for x in filt_df.columns.to_list() if any(m in str(x) for m in input.years())]
            selected_col = list(filt_df.columns[0:df_int]) + selected_years
            filt_df = filt_df[selected_col]
        global num
        print(f'executed {num} times')
        num += 1
        # print('From function',filt_df, sep='\n')
        return filt_df
    
    def filtered_df() -> pd.DataFrame:
        if input.sc2_df2() == "Half-Yearly" and input.sc2_df3() == "by Country":
            return parent_filtered_df(all_df[0], input_country=input.country(), df_int=3)

        elif input.sc2_df2() == "Quarterly" and input.sc2_df3() == "by Country":
            return parent_filtered_df(all_df[1], input_country=input.country(), df_int=5)

        elif input.sc2_df2() == "Half-Yearly" and input.sc2_df3() in ["by Region", "by Category"]:
            return parent_filtered_df(all_df[3], input_country=input.country(), df_int=4, include_region=input.include_region())

        elif input.sc2_df2() == "Annually" and input.sc2_df3() == "by Country":
            return parent_filtered_df(all_df[4], input_country=input.country(), df_int=5)

        elif input.sc2_df2() == "Annually" and input.sc2_df3() in ["by Region", "by Category"]:
            return parent_filtered_df(all_df[5], input_country=input.country(), df_int=4, include_region=input.include_region()) 
        
        elif input.sc2_df2() == "Half-Yearly" and input.sc2_df3() in ["by Region", "by Category"]:
            return parent_filtered_df(all_df[3], input_country=input.country(), df_int=4, include_region=input.include_region())

        elif input.sc2_df2() == "Annually" and input.sc2_df3() in ["by Region", "by Category"]:
            return parent_filtered_df(all_df[5], input_country=input.country(), df_int=4, include_region=input.include_region())

    # if input.sc2_df2() == 'Annual' and input.sc2_df3() == 'by Region':
    filltered_df1 = reactive.Calc(
        lambda: filtered_df()
    )

    @render.data_frame
    def summary_data():
        df_dict = {'Annually': {'by Region':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()},
                                'by Category':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()}, 
                              'by Country':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()},
                              },
                   'Quarterly': {'by Region':{'Balance of Payment': None, 'International Investment Position': None}, 
                                 'by Category':{'Balance of Payment': None, 'International Investment Position': None}, 
                              'by Country':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()},
                              },
                   'Half-Yearly': {'by Region':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()}, 
                                   'by Category':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()}, 
                              'by Country':{'Balance of Payment': filltered_df1(), 'International Investment Position': filltered_df1()},
                              },
                   }

        df = df_dict[input.sc2_df2()][input.sc2_df3()][input.sc2_df()]
        if df is not None:
            df.rename(columns={k:str(k) for k in df.columns}, inplace=True)
            df = df.map(lambda x: '{:,.2f}'.format(x) if isinstance(x, (int, float)) else x)
        return render.DataGrid(df) if df is not None else render.DataGrid(pd.DataFrame(['No DataFrame for the selected options!'], columns=['Message']))

    @render_plotly
    def hist1():
        if input.sc2_df2() in ['Annually', 'Half-Yearly']:
            dropping = []
            dataF0 = filltered_df1()
            if input.sc2_df3() == 'by Region':
                dropping = ['Group2', 'Type']
                dataF = dataF0[~dataF0['Type'].isin(exclude)]
            if input.sc2_df3() == 'by Category':
                dataF = dataF0[dataF0['Region'] == input.region()]
                if dataF.empty:
                    dataF = dataF0
                dropping = ['Group2', 'Region']
                dataF = dataF[~dataF['Type'].isin(exclude)]
            elif input.sc2_df3() == 'by Country':
                dropping = ['Group2', 'Type']
                dataF = dataF0
                # ['Group2', 'Region' if input.sc2_df3 == 'by Country' else 'Type']
            dataF = dataF.drop(dropping, axis=1)
            
            if input.sc2_df3() == 'by Region':
                dataF = dataF.drop(['Group'], axis=1)
                dataF = dataF.groupby(['Region']).sum().reset_index().melt(id_vars=['Region'], var_name='Date', value_name='Value')
            elif input.sc2_df3() == 'by Category':
                dataF = dataF.drop(['Group'], axis=1)                
                dataF = dataF.groupby(['Type']).sum().reset_index().melt(id_vars=['Type'], var_name='Date', value_name='Value')
            elif input.sc2_df3() == 'by Country':
                # dataF = dataF.drop(['Group'], axis=1)
                col = set(dataF.columns.to_list())
                exclude3 = list(exclude2.intersection(col))
                dataF.drop(exclude3, axis=1, inplace=True)
                dataF = dataF.melt(id_vars="Region", var_name="Date", value_name="Value")
        else:
            dataF = pd.DataFrame({'A' : []})
        
        if not dataF.empty:
            var1 = {'by Region': 'Region', 'by Country': 'Region', 'by Category': 'Type'}
            # dataF = dataF.melt(id_vars=var1[input.sc2_df3()], var_name="Date", value_name="Value") 
            fig = px.bar( #or px.histogram
                dataF,
                x="Date",
                y="Value",
                color=var1[input.sc2_df3()],
                # barmode="group",
                # orientation="h",
                title=f'{input.sc2_df()} {'('+change[input.group()]+")" if input.sc2_df() == 'Balance of Payment' else ''}- {input.sc2_df2()} {input.sc2_df3()}',
            )
            fig.update_layout(
                legend=dict(
                    orientation="h",     # Horizontal layout
                    y=-0.2,              # Push it down (adjust if needed)
                    x=0.5,               # Center it
                    xanchor="center",
                    yanchor="top"
                )
            )
            return fig
        
app = App(app_ui, server)