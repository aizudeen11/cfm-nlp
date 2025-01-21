# shiny run --reload --launch-browser cfm-nlp/main.py

from shiny import App, ui, render, reactive

# import shinyswatch
from shinywidgets import render_plotly
import plotly.express as px
from palmerpenguins import load_penguins

app_ui = ui.page_fixed(
    ui.navset_tab(
        ui.nav_panel(
            "A",
            ui.page_sidebar(
                ui.sidebar(
                    ui.input_selectize(
                        "var",
                        "Select variable",
                        choices=["bill_length_mm", "body_mass_g"],
                    ),
                ui.output_plot('hist')
                )
            ),
        )
    )
)


def server(input, output, session):
    @render_plotly
    def hist():
        df = load_penguins()
        return px.histogram(df, x=input.var())


app = App(app_ui, server)
