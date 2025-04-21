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


app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        "**Instructions**: Select one or more countries in the table below to see more information."
    ),
    ui.layout_columns(
        ui.input_radio_buttons(
            "sc2_df",
            "Select DataFrame",
            choices=["sc2_half", "sc2_quarter"],
            selected="sc2_half",
            inline=True,
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
        col_widths=[4,4,4, 12],
        row_heights=["auto", 1],
    ),
)


def server(input, output, session):
    def parent_filtered_df(df: pd.DataFrame, input_country, input_types) -> pd.DataFrame:
        filt_df = df[(df["Type"]==input_types) & (df["Region"].isin(input_country))]

        return filt_df

    filltered_df1 = reactive.Calc(
        lambda: parent_filtered_df(all_df[0], input.country(), input.types())
    )
    filltered_df2 = reactive.Calc(
        lambda: parent_filtered_df(all_df[1], input.country(), input.types())
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