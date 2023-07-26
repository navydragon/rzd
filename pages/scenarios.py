import dash
from dash import html, dcc,callback, Input, Output, State, ALL
from pages.helpers import scenario_parameters as sp
from pages.constants import Constants as CON
import dash_bootstrap_components as dbc
import pandas as pd

import random
import string
import json
import ast

def generate_random_string(length):
    """Генерирует случайную строку заданной длины"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=length))

dash.register_page(__name__, name="Сценарии", path='/scenarios', order=4)

def get_state_objects(suffix):
    return [
        State('scenario_name', 'value'),
        State('costs_base_variant' + suffix, 'value'),
        State('costs_variant' + suffix, 'value'),
        State('approach_variant' + suffix, 'value'),
        State('direction_variant' + suffix, 'value'),
        State('turnover_variant' + suffix, 'value'),
        State('invest_variant' + suffix, 'value'),
        State('year_variant' + suffix, 'value'),
        State('invest_percent' + suffix, 'value'),
        State('card-container', 'children'),
    ]

SUFFIX = 'scenarios'
state_objects = get_state_objects(SUFFIX)


# считываем параметры сценариев
scenarios_df = pd.read_csv('data/scenarios.csv').reset_index(drop=True)


# регистрация callback
sp.switch_base_variant_callback(SUFFIX)
sp.invest_variant_callback(SUFFIX)
sp.turnover_variant_callback(SUFFIX)


def layout():
    global scenarios_df
    cards = []
    for index, row in scenarios_df.iterrows():
        card = draw_card(row)
        cards.append(card)

    modal = html.Div(
        [
            dbc.Button("+ Добавить сценарий",id="open_button",n_clicks=0, color="success"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Добавить новый сценарий")),
                    dbc.ModalBody([
                        html.Label('Название сценария', className="fw-bold"),
                        dbc.Input(type="text", placeholder="Введите название сценария", id='scenario_name', className="my-2"),
                        sp.draw_panel(SUFFIX)
                    ]),
                    dbc.ModalFooter([
                        dbc.Button("Добавить", color='success', id="create-button", className="ml-auto", n_clicks=0),
                        dbc.Button("Закрыть", id="close_button", className="ml-auto", n_clicks=0)
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
        html.Div(cards, id='card-container')
    ], className='m-2')


@callback(
    Output("modal", "is_open"),
    Input("open_button", "n_clicks"), Input("close_button", "n_clicks"),
    prevent_initial_call = True
)
def open_modal(open_button, close_button):
    # Получение индекса нажатой кнопки с помощью dash.callback_context
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'open_button':
        return True
    return False


# добавить сценарий
# @callback(
#     [
#         Output("close_button", "n_clicks"),
#      ],
#     [Input("create-button", "n_clicks")],
#     State("close", "n_clicks"),
#     *state_objects,
#     prevent_initial_call = True
# )
# def create_scenario (n1, n2,
#     *state_values
# ):
#
#     return [n2+1]


@callback(
    [Output('card-container', 'children'),
    Output("close_button", "n_clicks")],
    Input("create-button", "n_clicks"),
    Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
    State('card-container', 'children'),
    State('close_button', 'n_clicks'),
    *state_objects,
    prevent_initial_call = True
)
def handle_cards(create_button_clicks, delete_button_clicks, card_children,close_button_clicks, *state_values,):
    # Получение индекса нажатой кнопки с помощью dash.callback_context
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    global scenarios_df

    if triggered_id == 'create-button':
        new_row = pd.Series({
            'id': generate_random_string(6),
            'name': state_values[0],
            'costs_base_variant': state_values[1],
            'costs_variant': state_values[2],
            'approach_variant': state_values[3],
            'direction_variant': state_values[4],
            'turnover_variant': state_values[5],
            'invest_variant': state_values[6],
            'year_variant': state_values[7],
            'invest_percent': state_values[8]
        })
        scenarios_df = scenarios_df.append(new_row, ignore_index=True)
        scenarios_df.to_csv('data/scenarios.csv', index=False)
        updated_children = card_children + [draw_card(new_row)]
        return updated_children, close_button_clicks+1

    # удаляем
    clicked_index = json.loads(triggered_id).get('index')
    # Удаление соответствующей карточки из списка
    updated_children = [child for child in card_children if child['props']['id'] != clicked_index]
    # удаление из df
    condition = scenarios_df['id'] == clicked_index
    scenarios_df = scenarios_df.drop(scenarios_df[condition].index)
    scenarios_df.to_csv('data/scenarios.csv', index=False)
    return updated_children, [0]


def draw_card (row):
    return dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4(f"Сценарий «{row['name']}»", className="card-title"),
                        html.P("Параметры сценария:.", className="card-text", ),
                        html.Ul(scenario_definition(row)),

                        dbc.ButtonGroup([
                            dbc.Button("Рассчитать", color="primary"),
                           # dbc.Button("Изменить", color="info"),
                            dbc.Button("Удалить", id={'type': 'delete-button', 'index': row['id']}, n_clicks=0, color="danger"),
                        ])
                    ]
                ),
            ], id=row.id, className='my-2')


def scenario_definition(row):
    res = []
    res.append(html.Li([
            html.Strong('Базовая основа для тарифа: '),
            html.Span(search_in_dicts_list(CON.COSTS_BASE_VARIANTS, row["costs_base_variant"]))
    ]))
    if row["costs_base_variant"] == 'option1':
        res.append(html.Li([
            html.Strong('Вариант агрегации расходных ставок: '),
            html.Span(search_in_dicts_list(CON.DIRECTION_VARIANTS, row["direction_variant"]))
        ]))
        res.append(html.Li([
            html.Strong('Дифференциация тарифов между видами грузов: '),
            html.Span(search_in_dicts_list(CON.APPROACH_VARIANTS, row["approach_variant"]))
        ]))

    if row["costs_base_variant"] == 'option2':
        res.append(html.Li([
            html.Strong('Вид расходов: '),
            html.Span(search_in_dicts_list(CON.COSTS_VARIANTS, row["costs_variant"]))
        ]))
    if len(str(row['invest_variant'])) > 3:
        inv = ''
        if type(row['invest_variant']) is not list:
            options = row['invest_variant'].strip("[]").strip()
            print(options)
            options = ast.literal_eval(options)
        else:
            options = row['invest_variant']
        if 'option1' in options:
            inv += 'Затраты на ремонт инфраструктуры; '
        if 'option2' in options:
            inv += f'Инвестиционная программа({row["invest_percent"]}%);'
    else:
        inv = 'нет'

    res.append(html.Li([
        html.Strong('Инвестиционная составляющая: '),
        html.Span(inv)
    ]))
    res.append(html.Li([
        html.Strong('Тарифный период: '),
        html.Span(row['year_variant'])
    ]))
    return res

def search_in_dicts_list (data, search_value):
    found_label = None
    for item in data:
        if str(item['value']) == str(search_value):
            return item['label']
    return None