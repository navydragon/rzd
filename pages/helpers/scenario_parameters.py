import pandas as pd
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from pages.constants import Constants as CON




# функция возвращающая параметры сценария
def draw_panel(suffix):
    return html.Div([
        html.Div([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Параметры сценария"),
                dbc.CardBody(
                    [
                        dbc.Row([
                            dbc.Col([
                                html.Label('Базовая основа для тарифа:', className="fw-bold"),
                                dcc.Dropdown(
                                    id='costs_base_variant' + suffix,
                                    options=CON.COSTS_BASE_VARIANTS,
                                    clearable=False,
                                    value='option1'
                                ),
                                html.Div([
                                    html.Label('Вариант агрегации расходных ставок:', className="fw-bold mt-2"),
                                    dcc.Dropdown(
                                        id='direction_variant' + suffix,
                                        options= CON.DIRECTION_VARIANTS,
                                        clearable=False,
                                        value='option4'
                                    ),
                                    html.Label('Дифференциация тарифов между видами грузов:', className="fw-bold mt-2"),
                                    dcc.Dropdown(
                                        id='approach_variant' + suffix,
                                        options=CON.APPROACH_VARIANTS,
                                        clearable=False,
                                        value='option1'
                                    ),

                                ], style={"display": "none"}, id='cps_parameters' + suffix),
                                html.Div([
                                    html.Label('Вид расходов:', className="fw-bold"),
                                    dcc.Dropdown(
                                        id='costs_variant' + suffix,
                                        options=CON.COSTS_VARIANTS,
                                        clearable=False,
                                        value='option1'
                                    ),
                                ], style={"display": "none"}, className='mt-2', id='costs_parameters' + suffix)
                            ], className='col-md-6'),
                            dbc.Col([
                                html.Label('Инвестиционная составляющая:', className="mt-2 fw-bold"),
                                dcc.Dropdown(
                                    id='invest_variant' + suffix,
                                    options=CON.INVEST_VARIANTS,
                                    multi=True
                                ),
                                html.Div([
                                    html.Label('% инвестиционной программы',
                                               className="fw-bold mt-2"),
                                    dcc.Slider(
                                        id='invest_percent' + suffix,
                                        min=0,
                                        max=100,
                                        step=5,
                                        value=50,
                                        marks={}
                                    ),
                                ], id='invest_percent_div' + suffix),
                                html.Label('Тарифный период:',
                                           className="fw-bold mt-2"),
                                dcc.Dropdown(
                                    id='year_variant' + suffix,
                                    options=CON.YEAR_VARIANTS,
                                    clearable=False,
                                    value='2026'
                                ),
                                html.Div([
                                    html.Label('Изменение грузооборота:',
                                               className="fw-bold mt-2"),
                                    dcc.Dropdown(
                                        id='turnover_variant' + suffix,
                                        options=CON.TURNOVER_VARIANTS,
                                        clearable=False,
                                        value='option1'
                                    ),
                                ], style={"display": "none"}, id='turnover_parameters' + suffix)

                            ], className='col-md-6'),
                        ]),
                    ]
                ),
            ], color="light")),
        ], className="m-4", ),
    ])


def switch_base_variant_callback(suffix):
    @callback(
        [Output("cps_parameters" + suffix, "style"), Output("costs_parameters" + suffix, "style")],
        Input("costs_base_variant" + suffix, "value"),
    )
    def switch_base_variant(costs_base_variant):
        if costs_base_variant == 'option1':
            return {"display": "block"}, {"display": "none"}
        return {"display": "none"}, {"display": "block"}


def invest_variant_callback(suffix):
    @callback(
        Output("invest_percent_div" + suffix, "style"),
        [Input('invest_variant' + suffix, 'value')]
    )
    def switch_invest_percent(variants):
        if not isinstance(variants, list):
            variants = [variants]
        if 'option2' in variants:
            return {"display": "block"}
        return {"display": "none"}


def turnover_variant_callback(suffix):
    @callback(
        Output("turnover_parameters" + suffix, "style"),
        Input("year_variant" + suffix, "value"),
    )
    def switch_turnover_variant(year_variant):
        if year_variant != "2026":
            return {"display": "block"}
        return {"display": "none"}
