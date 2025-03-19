# shiny run --reload --launch-browser cfm-nlp/main.py
# shiny run --reload --launch-browser main.py
# SHIFT + END to go to end of line
from shiny import App, ui, render, reactive
# from data import Data
import logging
import pandas as pd
from processed_data import dfs#, dataF

# import shinyswatch
from shinywidgets import render_plotly, output_widget
import plotly.express as px
from cache_pandas import timed_lru_cache
import plotly.graph_objects as go


# all_df = dataF() -- dev use this
all_df = dfs() # publish use this

@timed_lru_cache(seconds=None, maxsize=None)
def ex_rate_diff():
    ex_rate_df = all_df[4]
    years = sorted(list(ex_rate_df["Year"].unique()))[-2:]
    ex_rate_df = ex_rate_df[ex_rate_df["Year"].isin(years)]
    ex_rate_df['diff'] = ex_rate_df.groupby('Region')['Value'].diff(-1)
    ex_rate_df.dropna(inplace=True)
    ex_rate_df = ex_rate_df.iloc[::-1]
    ex_rate_df['diff'] = ex_rate_df['diff'].round(2)
    return ex_rate_df, years

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
                                start=all_df[0]["Date"].min(),
                                end=all_df[0]["Date"].max(),
                            ),
                            output_widget("hist"),
                            col_widths={"sm": (12, 12)},
                            row_heights=["auto", 1],
                        ),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Policy Rate"),
                        ui.layout_columns(
                            ui.input_date_range(
                                "date_range2",
                                "Select Date Range - Policy Rate:",
                                start=all_df[1]["Date"].min(),
                                end=all_df[1]["Date"].max(),
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
                            ui.card_footer(
                                """Notes: The policy rate for the United States refers to the effective Fed Funds rate. Data for China pertains to the one-year 
                                       loan prime rate sourced from the Bank for International Settlements (BIS) Data Portal. The policy rate for the Euro Area is the 
                                       main refinancing fixed rate of the European Central Bank
                                       """
                            ),
                            col_widths={"sm": (6, 6, 12, 12)},
                            row_heights=["auto", 1],
                        ),
                        # output_widget("hist1"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Exchange Rate Changes"),
                        ui.layout_columns(
                            ui.input_checkbox_group(
                                "ex_rate",
                                "Exchange Rate Changes",
                                choices=list(
                                    all_df[4]["Year"].unique()
                                ),  # Ensure it's a list, not a dict
                                selected=list(all_df[4]["Year"].unique())[:2],
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
                            ui.tags.div(ui.output_ui("styled_table")),
                            col_widths={"sm": (6, 6, 8, 4)},
                            row_heights=["auto", 1],
                        ),
                        ui.card_footer(
                            """Notes: Year-to-date values are computed as the monthly difference between the first and last data points within a year. 
                                       Positive changes refer to an appreciation of the local currency versus the U.S. dollar, and negative changes refer to depreciation. 
                                       """
                        ),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("5-Year Sovereign Credit Default Swap"),
                        ui.layout_columns(
                            ui.input_date_range(
                                "date_range3",
                                "Select Date Range - CDS:",
                                start=all_df[5]["Date"].min(),
                                end=all_df[5]["Date"].max(),
                            ),
                            output_widget("hist3"),
                            ui.card_footer(
                                """
                                           Note: 5-Year USD Credit Default Swap par mid-rate in basis points.
                                       """
                            ),
                            col_widths={"sm": (12, 12)},
                            row_heights=["auto", 1],
                        ),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("GDP Growth"),
                        ui.layout_columns(
                            ui.input_checkbox_group(
                                "gdp_quarterly",
                                "GDP Quarterly",  # {x:x for x in all_var[7]['Quarter'].unique()}, selected=all_var[7]['Quarter'].unique(),
                                choices=list(
                                    all_df[7]["Quarter"].unique()
                                ),  # Ensure it's a list, not a dict
                                selected=list(all_df[7]["Quarter"].unique()),
                                inline=True,
                            ),
                            output_widget("hist5"),
                            col_widths={"sm": (12, 12)},
                            row_heights=["auto", 1],
                        ),
                        ui.card_footer(
                            """
                                       Notes: Regional growth rates are weighted averages of individual growth rates, using GDP in PPP as weights. Asia Economies include 
                                       China, India, Mongolia, ASEAN-5 (Indonesia, Malaysia, Philippines, Thailand, and Vietnam), and Asia Advanced Economies (Hong Kong, 
                                       China; Korea; Singapore; and Chinese Taipei)."""
                        ),
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
    @output
    @render.ui
    def styled_table():
        ex_rate_diff_df, years = ex_rate_diff()
        table_html = f"""
        <table class='table table-bordered table-striped'>
            <thead>
                <tr>
                    <th>Region</th>
                    <th>Diff: ({years[1]} - {years[0]})</th>
                </tr>
            </thead>
            <tbody>
        """

        for _, row in ex_rate_diff_df.iterrows():
            row_class = "table-success" if row["diff"] > 0 else "table-danger"
            table_html += f"<tr class='{row_class}'><td>{row['Region']}</td><td>{row['diff']}</td></tr>"

        table_html += "</tbody></table>"
        return ui.HTML(table_html)

    def parent_filtered_df(df, input_date_range):
        start_date, end_date = input_date_range
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        filt_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

        return filt_df

    filltered_vix = reactive.Calc(
        lambda: parent_filtered_df(all_df[0], input.date_range())
    )
    filltered_pr1 = reactive.Calc(
        lambda: parent_filtered_df(all_df[1], input.date_range2())
    )
    filltered_pr2 = reactive.Calc(
        lambda: parent_filtered_df(all_df[2], input.date_range2())
    )
    filltered_pr3 = reactive.Calc(
        lambda: parent_filtered_df(all_df[3], input.date_range2())
    )
    filltered_cds = reactive.Calc(
        lambda: parent_filtered_df(all_df[5], input.date_range3())
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

    @render_plotly
    def hist3():
        cds = filltered_cds()
        return px.line(
            cds, x="Date", y="Value", color="Region", markers=True, title="CDS"
        )

    @render_plotly
    def hist4():
        liquidity = all_df[6]
        fig = px.histogram(
            liquidity,
            x="TIME_PERIOD",
            y="OBS_VALUE",
            # color='index', barmode='group',
            # orientation="h",
            title="Liquidity",
        )
        return fig

    @render_plotly
    def hist5():
        gdp_growth = all_df[7]
        gdp_growth = gdp_growth[gdp_growth["Quarter"].isin(input.gdp_quarterly())]
        fig = px.histogram(
            gdp_growth,
            x="Quarter",
            y="Value",
            color="Region",
            barmode="group",
            # orientation="h",
            title="GDP Growth by Region",
        )
        return fig
    
    @render_plotly
    def hist6():
        fsi = all_df[8]
        fsi = fsi[fsi["Quarter"].isin(input.gdp_quarterly())]
        fig = px.line(
            fsi,
            x="Quarter",
            y="Value",
            color="Region",
            markers=True,
            # orientation="h",
            title="GDP Growth by Region",
        )
        return fig


app = App(app_ui, server)
