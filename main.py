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

app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_panel(
            "Section 1",
            ui.page_sidebar(
                ui.sidebar(
                    ui.card(
                        ui.p("This is a sidebar"),                        
                    ),
                    title="Filter controls",
                ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("VIX Liquidity"),
                        ui.layout_columns(
                            ui.input_date_range(
                            "date_range",
                            "Select Date Range - Vix:",
                            start=all_var[0]["Date"].min(),
                            end=all_var[0]["Date"].max()
                            ),
                        output_widget("hist"),                      
                        col_widths={"sm": (12, 12)},
                        row_heights=['auto', 1], 
                        ),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Policy Rate"),
                        ui.layout_columns(
                            ui.input_date_range(
                            "date_range2",
                            "Select Date Range - Policy Rate:",
                            start=all_var[1]["Date"].min(),
                            end=all_var[1]["Date"].max()
                            ),   
                        ui.input_selectize(
                            "var",
                            "Policy Rate",
                            choices=[
                                "All region",
                                "Selected region 1",
                                "Selected region 2",
                            ],
                        ),
                        output_widget("hist1"),
                        ui.card_footer("""Notes: The policy rate for the United States refers to the effective Fed Funds rate. Data for China pertains to the one-year 
                                       loan prime rate sourced from the Bank for International Settlements (BIS) Data Portal. The policy rate for the Euro Area is the 
                                       main refinancing fixed rate of the European Central Bank
                                       """),
                        col_widths={"sm": (6, 6, 12, 12)},
                        row_heights=['auto', 1],                     
                        ),                        
                        # output_widget("hist1"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Exchange Rate Changes"),
                        output_widget("hist2"),
                        ui.card_footer("""Notes: Year-to-date values are computed as the monthly difference between the first and last data points within a year. 
                                       Positive changes refer to an appreciation of the local currency versus the U.S. dollar, and negative changes refer to depreciation. 
                                       """),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("5-Year Sovereign Credit Default Swap"),
                        ui.layout_columns(
                            ui.input_date_range(
                            "date_range3",
                            "Select Date Range - CDS:",
                            start=all_var[5]["Date"].min(),
                            end=all_var[5]["Date"].max(),
                        ),
                            output_widget("hist3"),
                            ui.card_footer("""
                                           Note: 5-Year USD Credit Default Swap par mid-rate in basis points.
                                       """),
                            col_widths={"sm": (12, 12)},
                            row_heights=['auto', 1],),
                        full_screen=True,
                    ),
                    ui.card(
                        output_widget("hist4"),
                        full_screen=True,
                    ),
                    fill=False,
                    col_widths={"sm": (6, 6)},
                ),
            ),
        )
    ),
    title="Capital Flow Monitor Dashboard",
)


def server(input, output, session):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def parent_filtered_df(df, input_date_range):
        start_date, end_date = input_date_range
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        filt_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

        return filt_df

    filltered_vix = reactive.Calc(
        lambda: parent_filtered_df(all_var[0], input.date_range())
    )
    filltered_pr1 = reactive.Calc(
        lambda: parent_filtered_df(all_var[1], input.date_range2())
    )
    filltered_pr2 = reactive.Calc(
        lambda: parent_filtered_df(all_var[2], input.date_range2())
    )
    filltered_pr3 = reactive.Calc(
        lambda: parent_filtered_df(all_var[3], input.date_range2())
    )
    filltered_cds = reactive.Calc(
        lambda: parent_filtered_df(all_var[5], input.date_range3())
    )

    @render_plotly
    def hist():
        vix = filltered_vix()
        return px.line(vix, x="Date", y="CLOSE", title="VIX Liquidity")

    @render_plotly
    def hist1():
        policy_dict = {
            "All region": filltered_pr1(),
            "Selected region 1": filltered_pr2(),
            "Selected region 2": filltered_pr3(),
        }
        title_pl = {
            "All region": "Policy Rate - All Region",
            "Selected region 1": "Policy Rate - Selected Region 1",
            "Selected region 2": "Policy Rate - Selected Region 2",
            }
        title_pl2 = title_pl.get(input.var(), "Policy Rate")
        policy_rate = policy_dict.get(input.var(), filltered_pr1())
        return px.line(
            policy_rate,
            x="Date",
            y="Value",
            color="Region",
            markers=True,
            title=title_pl2,
        )

    @render_plotly
    def hist2():
        fx = all_var[4]
        fig = px.histogram(
            fx,
            x="Value",
            y="Region",
            color="Year",
            barmode="group",
            # orientation="h",
            title="Forex Exchange",
        )
        return fig

    @render_plotly
    def hist3():
        cds = filltered_cds()
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
            title="Liquidity",
        )
        return fig


app = App(app_ui, server)
