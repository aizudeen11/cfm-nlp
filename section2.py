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
                choices=["sc2_half", "sc2_quarter"],
                selected="sc2_half",
                inline=True,
            ),
            ui.input_radio_buttons(
                "view_type",
                "Select View Type",
                choices=["DataFrame", "Figure"],
                selected="DataFrame",
                inline=True,
            ),
        class_ = 'hh'
        ),
        ui.input_select(
            "years",
            "Select Year(s)",
            choices=sorted(years, reverse=True),
            selected=years[-4:],
            multiple=True,
        ),
        ui.input_select(
            "country",
            "Select Region(s)",
            choices=all_df[0]["Region"].unique().tolist(),
            selected=all_df[0]["Region"].unique().tolist(),
            multiple=True,
        ),
        ui.input_select(
            "types",
            "Select Type",
            choices=all_df[2],
            selected=all_df[0]["Type"].unique().tolist()[0],
            # multiple=True,
        ),
        ui.card(ui.output_data_frame("summary_data"), height="400px"),
        # ui.card(output_widget("country_detail_pop"), height="400px"),
        # ui.card(output_widget("country_detail_percap"), height="400px"),
        col_widths=[3,3,3,3, 12],
        row_heights=["auto", 1],
    ),
)


def server(input, output, session):
    def parent_filtered_df(df: pd.DataFrame, input_country, input_types, input_year, df_int) -> pd.DataFrame:
        filt_df = df[(df["Type"]==input_types) & (df["Region"].isin(input_country))]
        selected_years = [x for x in filt_df.columns.to_list() if any(m in x for m in input_year)]
        selected_col = list(filt_df.columns[0:df_int]) + selected_years
        filt_df = filt_df[selected_col]
        return filt_df

    filltered_df1 = reactive.Calc(
        lambda: parent_filtered_df(all_df[0], input.country(), input.types(), input.years(), 2)
    )
    filltered_df2 = reactive.Calc(
        lambda: parent_filtered_df(all_df[1], input.country(), input.types(), input.years(), 4)
    )

    @render.data_frame
    def summary_data():
        if input.sc2_df() == "sc2_half":
            df = filltered_df1()
        else:
            df = filltered_df2()
        return render.DataGrid(df)

    # @reactive.calc
    # def filtered_df():
    #     data_selected = summary_data.data_view(selected=True)
    #     req(not data_selected.empty)
    #     countries = data_selected["country"]
    #     # Filter data for selected countries
    #     return df[df["country"].isin(countries)]

    # @render_widget
    # def country_detail_pop():
    #     return px.line(
    #         filtered_df(),
    #         x="year",
    #         y="pop",
    #         color="country",
    #         title="Population Over Time",
    #     )

    # @render_widget
    # def country_detail_percap():
    #     return px.line(
    #         filtered_df(),
    #         x="year",
    #         y="gdpPercap",
    #         color="country",
    #         title="GDP per Capita Over Time",
    #     )


app = App(app_ui, server)