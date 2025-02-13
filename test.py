from shiny import App, ui, render, reactive
from data import Data
import logging
import pandas as pd

# import shinyswatch
from shinywidgets import render_plotly, output_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go

# Example data frames
all_var = [
    pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=100),
        "CLOSE": range(100)
    }),
    pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=100),
        "CLOSE": range(100, 200)
    })
]

def server(input, output, session):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Factory function to create a reactive calculation for a given data frame
    def create_filtered_df(df):
        @reactive.calc
        def filtered_df():
            start_date, end_date = input.date_range()
            start_date = pd.Timestamp(start_date)
            end_date = pd.Timestamp(end_date)
            filt_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            return filt_df
        return filtered_df

    # Create reactive calculations for each data frame
    filtered_df_1 = create_filtered_df(all_var[0])
    filtered_df_2 = create_filtered_df(all_var[1])

    @render_plotly
    def hist_1():
        vix = filtered_df_1()
        return px.line(vix, x="Date", y="CLOSE", title="VIX Liquidity (Data Frame 1)")

    @render_plotly
    def hist_2():
        vix = filtered_df_2()
        return px.line(vix, x="Date", y="CLOSE", title="VIX Liquidity (Data Frame 2)")

# Example UI
ui = ui.page_fluid(
    ui.input_date_range("date_range", "Date Range", start="2023-01-01", end="2023-03-31"),
    output_widget("hist_1"),
    output_widget("hist_2")
)

app = App(ui, server)