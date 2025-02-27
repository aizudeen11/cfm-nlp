# shiny run --reload --launch-browser cfm-nlp/testy.py

from processed_data import dfs
from shiny import App, ui, render, reactive
from shinywidgets import render_plotly, output_widget
import plotly.express as px
import pandas as pd

all_df = dfs()


app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card(
            ui.card_header("Exchange Rate Changes"),
            ui.layout_columns(
                ui.input_checkbox_group(
                    "ex_rate",
                    "Exchange Rate Changes",
                    choices=list(
                        all_df[4]["Year"].unique()
                    ),  # Ensure it's a list, not a dict
                    selected=list(all_df[4]["Year"].unique()),
                    inline=True,
                ),
                ui.input_radio_buttons(
                    "ex_rate2",
                    "Select Order by Year",
                    choices=list(all_df[4]["Year"].unique()),
                    selected=sorted(all_df[4]["Year"].unique())[-1],
                    inline=True,
                ),
                output_widget("hist2"),
                col_widths={"sm": (6, 6, 12)},
                row_heights=["auto", 1],
            ),
            ui.card_footer(
                """Notes: Year-to-date values are computed as the monthly difference between the first and last data points within a year. 
                            Positive changes refer to an appreciation of the local currency versus the U.S. dollar, and negative changes refer to depreciation. 
                            """
            ),
            full_screen=True,
        ),
    )
)


def server(input, output, session):
    @render_plotly
    def hist2():
        fx = all_df[4]
        region_sort = list(
            fx[(fx["Year"] == input.ex_rate2())].sort_values(
                by="Value", ascending=False
            )["Region"]
        )
        fx["Region"] = pd.Categorical(
            fx["Region"], categories=region_sort, ordered=True
        )
        fx = fx.sort_values(by=["Region", "Year"], ascending=False)
        fx = fx[fx["Year"].isin(input.ex_rate())]
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
    # @reactive(input.date_range)
    # def vix_liquidity(date_range):
    #     df = all_df[0]
    #     df = df[(df["Date"] >= date_range[0]) & (df["Date"] <= date_range[1])]
    #     return df

    # @render_plotly(output.hist)
    # def render_vix_liquidity(df):
    #     return df.plotly.line(x="Date", y="VIX")


app = App(app_ui, server)
