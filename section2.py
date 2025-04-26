# shiny run --reload --launch-browser cfm-nlp/section2.py
# shiny run --reload --launch-browser section2.py
# SHIFT + END to go to end of line
from shiny import App, ui, render, reactive, req
import pandas as pd
from processed_data import dfs, dfs1, dfs2

# import shinyswatch
from shinywidgets import render_plotly, output_widget, render_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

all_df = dfs2()
years = sorted(set([str(x)[:4] for x in all_df[1].columns[4:].to_list()]))
print(years)

app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        "**Instructions**: to **Select Year(s)** and **Select Region(s)**, hold down the Ctrl (windows) or Command (Mac) button to select multiple options."
    ),
    ui.layout_columns(
        ui.div(
            ui.input_radio_buttons(
                "sc2_df",
                "Select DataFrame",
                choices=["sc2_half", "sc2_quarter", 'df_main'],
                selected="sc2_half",
                inline=True,
            ),
            ui.input_checkbox_group(
                "view_type",
                "Select View Type",
                choices=["DataFrame", "Figure"],
                selected=["DataFrame"],
                inline=True,
            ),
        class_ = 'hh'
        ),
        ui.input_select(
            "years",
            "Select Year(s)",
            choices=sorted(years, reverse=True),
            selected=years,
            multiple=True,
        ),
        ui.input_select(
            "country",
            "Select Region(s) for scr2 table",
            choices=all_df[0]["Region"].unique().tolist(),
            selected=all_df[0]["Region"].unique().tolist(),
            multiple=True,
        ),
        ui.input_select(
            "types",
            "Select Type for scr2 table",
            choices=all_df[2],
            selected=all_df[0]["Type"].unique().tolist()[0],
            # multiple=True,
        ),
        ui.input_select(
            "group",
            "Select Group(s) for df_main table",
            choices=all_df[3]["Group"].unique().tolist(),
            selected=all_df[3]["Group"].unique().tolist()[0],
            # multiple=True,
        ),
        ui.input_select(
            "region",
            "Select Region for df_main table",
            choices=all_df[3]['Region'].unique().tolist(),
            selected=all_df[3]["Region"].unique().tolist()[0],
            # multiple=True,
        ),
        ui.card(ui.output_data_frame("summary_data"), height="400px"),
        output_widget("hist1"),
        # ui.card(output_widget("country_detail_pop"), height="400px"),
        # ui.card(output_widget("country_detail_percap"), height="400px"),
        col_widths=[2,2,2,2,2,2, 6,6],
        row_heights=["auto", 1],
    ),
)


def server(input, output, session):
    def parent_filtered_df(df: pd.DataFrame, input_country: tuple[list|tuple|str], input_types: str, input_year: list, df_int:int, vars:bool, grouping:tuple[list|tuple]) -> pd.DataFrame:
        
        filt_df = df[(df["Type"]==input_types) & (df["Region"].isin(input_country))] if vars else df[(df["Region"]==input_country)&(df["Group"]==grouping)]
        selected_years = [x for x in filt_df.columns.to_list() if any(m in x for m in input_year)]
        selected_col = list(filt_df.columns[0:df_int]) + selected_years
        filt_df = filt_df[selected_col]
        return filt_df

    filltered_df1 = reactive.Calc(
        lambda: parent_filtered_df(all_df[0], input.country(), input.types(), input.years(), 2, True, input.group())
    )
    filltered_df2 = reactive.Calc(
        lambda: parent_filtered_df(all_df[1], input.country(), input.types(), input.years(), 4, True, input.group())
    )
    filltered_df3 = reactive.Calc(
        lambda: parent_filtered_df(df=all_df[3], input_types='none',input_country=input.region(), input_year=input.years(), df_int=3, vars=False, grouping=input.group() )
    )

    @render.data_frame
    def summary_data():
        df_dict = {'sc2_half': filltered_df1(),
                   'sc2_quarter': filltered_df2(),
                   'df_main': filltered_df3(),}
        df = df_dict[input.sc2_df()]
        return render.DataGrid(df)

    @render_plotly
    def hist1():
        dataF = filltered_df3().drop(['Group','Region'], axis=1)
        dataF = dataF.melt(id_vars="Type", var_name="Date", value_name="Value")
        fig = px.bar( #or px.histogram
            dataF,
            x="Date",
            y="Value",
            color="Type",
            # barmode="group",
            # orientation="h",
            title="Nonresident Portfolio Flows",
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