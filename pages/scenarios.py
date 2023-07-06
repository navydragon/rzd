import dash
from dash import html, dcc,callback, Input, Output, State
from pages.helpers import scenario_parameters as sp

import dash_bootstrap_components as dbc
import pandas as pd

import random
import string


def generate_random_string(length):
    """Генерирует случайную строку заданной длины"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=length))

dash.register_page(__name__, name="Сценарии", path='/scenarios', order=4)

SUFFIX = 'scenarios'

# считываем параметры сценариев
scenarios_df = pd.read_csv('data/scenarios.csv')

# регистрация callback
sp.switch_base_variant_callback(SUFFIX)
sp.invest_variant_callback(SUFFIX)
sp.turnover_variant_callback(SUFFIX)


def layout():
    card1 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Сценарий №1", className="card-title"),
                    html.P("Описание параметров сценария №1...",
                           className="card-text", ),
                    html.Ul([
                        html.Li('Горизонт расчета - 2026 г.'), html.Li('...'),
                    ]),
                    dbc.ButtonGroup([
                        dbc.Button("Рассчитать", color="primary"),
                        dbc.Button("Изменить", color="info"),
                        dbc.Button("Удалить", color="danger"),
                    ])
                ]
            ),
        ], className='my-2')
    card2 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Сценарий №2", className="card-title"),
                    html.P("Описание параметров сценария №2...",
                           className="card-text", ),
                    html.Ul([
                        html.Li('Горизонт расчета - 2026 г.'), html.Li('...'),
                    ]),
                    dbc.ButtonGroup([
                        dbc.Button("Рассчитать", color="primary"),
                        dbc.Button("Изменить", color="info"),
                        dbc.Button("Удалить", color="danger"),
                    ])
                ]
            ),
        ], className='my-2')

    card3 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Сценарий №3", className="card-title"),
                    html.P("Описание параметров сценария №3...",
                           className="card-text", ),
                    html.Ul([
                        html.Li('Горизонт расчета - 2026 г.'), html.Li('...'),
                    ]),
                    dbc.ButtonGroup([
                        dbc.Button("Рассчитать", color="primary"),
                        dbc.Button("Изменить", color="info"),
                        dbc.Button("Удалить", color="danger"),
                    ])
                ]
            ),
        ], className='my-2')

    modal = html.Div(
        [
            dbc.Button("+ Добавить сценарий",id="open",n_clicks=0, color="success"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Добавить новый сценарий")),
                    dbc.ModalBody([
                        html.Label('Название сценария', className="fw-bold"),
                        dbc.Input(type="text", placeholder="Введите название сценария", id='scenario_name', className="my-2"),
                        sp.draw_panel(SUFFIX)
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Добавить", color='success', id="create", className="ml-auto", n_clicks=0),
                        dbc.Button("Закрыть", id="close", className="ml-auto", n_clicks=0)
                    ]),
                ],
                id="modal",
                is_open=False,
                size="xl"
            ),
        ]
    )

    return html.Div([
        html.H2('Сценарии', className="m-4"),
        modal,
        html.Div([
            card1, card2, card3
        ])
    ], className='m-2')

@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open




@callback(
    [Output("close", "n_clicks")],
    [Input("create", "n_clicks")],
    State("close", "n_clicks"),
    State('scenario_name', 'value'),
    State('costs_base_variant' + SUFFIX, 'value'), # ЦПС/расходы
    State('costs_variant' + SUFFIX, 'value'), # переменные/полные
    State('approach_variant' + SUFFIX, 'value'), # дифференциация тарифов
    State('direction_variant' + SUFFIX, 'value'), # ЦПС вариант
    State('turnover_variant' + SUFFIX, 'value'),
    State('invest_variant' + SUFFIX, 'value'),
    State('year_variant' + SUFFIX, 'value'),
    State('invest_percent' + SUFFIX, 'value'),
    prevent_initial_call = True
)
def create_scenario (n1, n2,
    scenario_name,
    costs_base_variant,
    costs_variant,
    approach_variant,
    direction_variant,
    turnover_variant,
    invest_variant,
    year_variant,
    invest_percent,
):
    global scenarios_df
    print(n1)

    new_row = pd.Series({
        'id': generate_random_string(6),
        'name': scenario_name,
        'costs_base_variant': costs_base_variant,
        'costs_variant': costs_variant,
        'approach_variant': approach_variant,
        'direction_variant': direction_variant,
        'turnover_variant': turnover_variant,
        'invest_variant': invest_variant,
        'year_variant': year_variant,
        'invest_percent': invest_percent
    })
    scenarios_df = scenarios_df.append(new_row, ignore_index=True)
    scenarios_df.to_csv('data/scenarios.csv', index=False)
    return [n2+1]