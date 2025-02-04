# shiny run --reload --launch-browser cfm-nlp/main.py

from shiny import App, ui, render, reactive
from data import Data

# import shinyswatch
from shinywidgets import render_plotly, output_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go

app_ui = ui.page_fixed(
    ui.navset_tab(
        ui.nav_panel(
            "Section 1",
            ui.page_sidebar(
                ui.sidebar(
                    ui.input_selectize(
                        "var",
                        "Policy Rate",
                        choices=["All region", "Selected region 1", "Selected region 2"]
                    )
                ),
            output_widget('hist'),
            output_widget('hist1'),
            output_widget('hist2'),
            ),
        )
    )
)


def server(input, output, session):
    @timed_lru_cache(seconds=None, maxsize=None)
    def dataF():
        df = Data()
        vix_data = df.vix_history()
        policy_rate1, policy_rate2, policy_rate3 = df.policy_rate()
        fx = df.forex_exchange()
        return vix_data, policy_rate1, policy_rate2, policy_rate3, fx
    @render_plotly
    def hist():        
        vix_data, policy_rate1, policy_rate2, policy_rate3, fx = dataF()
        return px.line(vix_data, x='Date', y='CLOSE', title='VIX Liquidity')
    @render_plotly
    def hist1():        
        vix_data, policy_rate1, policy_rate2, policy_rate3, fx = dataF()
        if input.var() == 'All region':
            policy_rate = policy_rate1
        elif input.var() == 'Selected region 1':
            policy_rate = policy_rate2 
        elif input.var() == 'Selected region 2':
            policy_rate = policy_rate3
        return px.line(policy_rate, x="Date", y="Value", color="Region", markers=True, title="Policy Rate")
    @render_plotly
    def hist2():
        vix_data, policy_rate1, policy_rate2, policy_rate3, fx = dataF()
        fig = px.histogram(fx, x="Value", y="Region",
            color='index', barmode='group',
            orientation="h",
            height=400)
        return fig.show()

app = App(app_ui, server)
