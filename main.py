# shiny run --reload --launch-browser cfm-nlp/main.py
# shiny run --reload --launch-browser main.py

from shiny import App, ui, render, reactive
from data import Data
import logging
import pandas as pd

# import shinyswatch
from shinywidgets import render_plotly, output_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go

@timed_lru_cache(seconds=None, maxsize=None)
def dataF():
    logging.info("Fetching data in dataF()")
    df = Data()
    vix_data = df.vix_history()
    policy_rate1, policy_rate2, policy_rate3 = df.policy_rate()
    fx = df.forex_exchange()
    cds = df.cds()
    liquidity = df.liquidity()
    logging.info("Completed fetching data in dataF()")
    return vix_data, policy_rate1, policy_rate2, policy_rate3, fx, cds, liquidity

all_var = dataF()

app_ui = ui.page_fixed(
    ui.navset_tab(
        ui.nav_panel(
            "Section 1",
            ui.page_sidebar(
                ui.sidebar(
                    ui.input_selectize(
                        "var",
                        "Policy Rate",
                        choices=[
                            "All region",
                            "Selected region 1",
                            "Selected region 2",
                        ],
                    ),
                    ui.input_date_range("date_range", "Select Date Range:", 
                        start=all_var[0]["Date"].min(), end=all_var[0]["Date"].max())
                ),
                output_widget("hist"),
                output_widget("hist1"),
                output_widget("hist2"),
                output_widget("hist3"),
                output_widget("hist4"),
            ),
        )
    )
)


def server(input, output, session):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    @reactive.calc
    def filtered_data():
        start_date, end_date = input.date_range()
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)
        return all_var[0][(all_var[0]["Date"] >= start_date) & (all_var[0]["Date"] <= end_date)]

    @render_plotly
    def hist():
        vix = filtered_data()#all_var[0]
        # vix_df = filtered_data(vix)
        return px.line(vix, x="Date", y="CLOSE", title="VIX Liquidity")

    @render_plotly
    def hist1():
        policy_rate1, policy_rate2, policy_rate3 = all_var[1],all_var[2],all_var[3]
        policy_dict = {
            "All region": policy_rate1,
            "Selected region 1": policy_rate2,
            "Selected region 2": policy_rate3,
        }
        policy_rate = policy_dict.get(input.var(), policy_rate1)
        return px.line(
            policy_rate,
            x="Date",
            y="Value",
            color="Region",
            markers=True,
            title="Policy Rate",
        )

    @render_plotly
    def hist2():
        fx = all_var[4]
        fig = px.histogram(
            fx,
            x="Value",
            y="Region",
            color="index",
            barmode="group",
            # orientation="h",
            height=400,
            title="Forex Exchange",
        )
        return fig

    @render_plotly
    def hist3():
        cds = all_var[5]
        return px.line(
            cds, x="Date", y="Value", color="Region", markers=True, title="CDS"
        )

    @render_plotly
    def hist4():
        liquidity = all_var[6]
        fig = px.histogram(
            liquidity,
            x="TIME_PERIOD",
            y="OBS_VALUE",
            # color='index', barmode='group',
            # orientation="h",
            height=400,
            title="Liquidity",
        )
        return fig


app = App(app_ui, server)
