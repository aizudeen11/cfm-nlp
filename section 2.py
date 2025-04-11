# shiny run --reload --launch-browser cfm-nlp/main.py
# shiny run --reload --launch-browser main.py
# SHIFT + END to go to end of line
from shiny import App, ui, render, reactive
import pandas as pd
from processed_data import dfs, dfs1

# import shinyswatch
from shinywidgets import render_plotly, output_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

all_df = dfs()

def section2():
    ui.nav_panel(
            "Section 2",
            ui.page_sidebar(
                ui.sidebar(
                    ui.card(
                        ui.p("This is a sidebar"),
                    ),
                    title="Filter controls",
                    open='closed'
                    ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("VIX Liquidity"),
                        ui.layout_columns(
                            ui.input_date_range(
                                "date_range",
                                "Select Date Range:",
                                start=all_df[0]["Date"].min(),
                                end=all_df[0]["Date"].max(),
                            ),
                            output_widget("hist"),
                            col_widths={"sm": (12, 12)},
                            row_heights=["auto", 1],
                        ),
                        ui.card_footer(
                                """
                                Notes: The VIX index is a measure of market expectations of near-term volatility conveyed by S&P 500 stock index option prices.
                                """
                            ),
                        full_screen=True,
                        ),
                    )
                )
            )