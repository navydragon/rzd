import dash

from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
from pages.helper import load_data, get_invest_data
import dash_bootstrap_components as dbc
from pages.constants import Constants as CON
import plotly.express as px
import plotly.graph_objs as go
from pages.helper import (
    get_indexes_data,
    percentage_change,
)



import pages.helpers.scenario_parameters as sp
import pages.helpers.calculations as calc
from pages.constants import Constants


dash.register_page(__name__, name="Аналитика", path='/', order=3)






SUFFIX = '_parameters'

# константы
START_YEAR = 2026
CON = Constants(START_YEAR)

# регистрация callback
sp.switch_base_variant_callback(SUFFIX)
sp.invest_variant_callback(SUFFIX)
sp.turnover_variant_callback(SUFFIX)

# подключаем маршруты
base_routes_df = load_data()
# подключаем индексы
index_df = get_indexes_data()

# фильтры


CARGOS = sorted(base_routes_df[CON.CARGO].unique())
MESSAGES = sorted(base_routes_df[CON.MESSAGE].unique())
SIDES = sorted(base_routes_df[CON.SIDE].unique())
HOLDINGS = base_routes_df[CON.HOLDING].unique()


def layout():
    return html.Div([
        html.H2('Аналитика', className="m-4"),
        sp.draw_panel(SUFFIX),
        selectors(),
        # html.H3('Стоимостная основа', className='m-4'),
        dcc.Loading(
            id="loading",
            type="default",
            children=[html.Div([], id='cost_basis_div', className='mx-4')]
        ),
        dbc.Button(
            "+",
            id="collapse_special_button",
            className="mb-3 mx-2",
            color="light",
            n_clicks=0,
        )
        # html.H4('Проверка', className='m-4'),
        # html.H5('Первые 5 строк таблицы', className='m-4'),
        # html.Div([], id='check_div', className='mx-4'),

    ])


@callback(
    Output('cost_basis_div', 'children'),
    Input('costs_base_variant' + SUFFIX, 'value'), # ЦПС/расходы
    Input('costs_variant' + SUFFIX, 'value'), # переменные/полные
    Input('approach_variant' + SUFFIX, 'value'), # дифференциация тарифов
    Input('direction_variant' + SUFFIX, 'value'), # ЦПС вариант
    Input('turnover_variant' + SUFFIX, 'value'),
    Input('invest_variant' + SUFFIX, 'value'),
    Input('year_variant' + SUFFIX, 'value'),
    Input('invest_percent' + SUFFIX, 'value'),
    Input('group1_variant', 'value'),
    Input('group2_variant', 'value'),
    Input('cargo_filter', 'value'),
    Input('message_filter', 'value'),
    Input('side_filter', 'value'),
    Input('holding_filter', 'value'),
)
def update_dashboard(
        costs_base_variant,
        costs_variant,
        approach_variant,
        direction_variant,
        turnover_variant,
        invest_variant,
        year_variant,
        invest_percent,
        group1_variant,group2_variant,
        cargo_filter, message_filter, side_filter, holding_filter):
    # selected_label = next((option['label'] for option in turnover_variant if option['value'] == group1_variant), None)
    year_variants = year_variant
    if not isinstance(year_variants, list):
        year_variants = [year_variants]

    invest_variants = invest_variant
    if not isinstance(invest_variants, list):
        invest_variants = [invest_variants]
    params = {
        "costs_base_variant": costs_base_variant,
        "costs_variant": costs_variant,
        "approach_variant": approach_variant,
        "direction_variant": direction_variant,
        "turnover_variant": turnover_variant,
        "invest_variant": invest_variants,
        "label": 'Признак',
        "year_variant": year_variants,
        "invest_percent": invest_percent,
        "group1_variant": group1_variant,
        "group2_variant": group2_variant,
    }

    # Расчет на уровне маршрутов
    df = calc.calculate_data(base_routes_df, index_df, params)

    # Фильтрация данных
    # Фильтры
    filters = {
        'Наименование груза ЦО-12': cargo_filter,
        'Вид сообщения': message_filter,
        'Направление': side_filter,
        'Холдинг отправителя': holding_filter
    }

    for column, value in filters.items():
        if value is not None:
            df = df.loc[df[column] == value]



    # группируем данные
    df_grouped = calc.group_data(df,params)


    table1 = make_table_so(df_grouped, params)
    table2 = make_table2(df_grouped, params)
    table3 = make_table_tarif(df_grouped, params)
    graph_tarif = draw_graph_tarif(df_grouped, params)
    if params['year_variant'][0] == '2026':
        dty = df_grouped[CON.PR_P].sum() / 1000000
        nty = df_grouped['so_start'].sum() / 1000000
        delta = nty - dty
    else:
        dty = df_grouped['pp_'+params['year_variant'][0]].sum() / 1000000
        nty = df_grouped['so_'+params['year_variant'][0]].sum() / 1000000
        delta = nty - dty

    total_values = html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Действующие тарифные условия"),
                dbc.CardBody(
                    [
                        html.Label(round(dty), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Новые тарифные условия"),
                dbc.CardBody(
                    [
                        html.Label(round(nty), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Экономический эффект"),
                dbc.CardBody(
                    [
                        html.Label(round(delta), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
        ])

    ], className="m-4", )

    df_fig = df.groupby(['Вид сообщения','Направление','Наименование груза ЦО-12']).agg(CON.AGG_PARAMS)
    df_fig.reset_index(inplace=True)



    colors = ['#C2DFFF', '#FFD8B1', '#B1FFC2', '#FFB1C2', '#E8B1FF', '#B1FFDF',
              '#FFDFA3', '#A3FFDF', '#DFDFA3', '#A3DFFF', '#DFA3FF']
    head1 = html.H4('Стоимостная основа по видам грузов', className='mt-4')
    fig = px.pie(df_fig, values=CON.PR_P, names='Наименование груза ЦО-12',
                 title='Действующие тарифные условия', color_discrete_sequence=px.colors.sequential.BuGn[::-1])
    fig.data[0].hovertemplate = '%{label}<br>Значение: %{value} тыс. руб.'
    graph2 = dcc.Graph(figure=fig)
    fig = px.pie(df_fig, values=CON.PR_P, names='Наименование груза ЦО-12', title='Действующие тарифные условия (в другом цвете)', color_discrete_sequence=px.colors.sequential.Teal)
    fig.data[0].hovertemplate = '%{label}<br>Значение: %{value} тыс. руб.'
    graph3 = dcc.Graph(figure=fig)

    fig = px.pie(df_fig, values='so_start', names='Наименование груза ЦО-12',title='Новые тарифные условия', color_discrete_sequence=px.colors.sequential.RdBu[::-1])
    fig.data[0].hovertemplate = '%{label}<br>Значение: %{value} тыс. руб.'
    graph4 = dcc.Graph(figure=fig)

    df_fig2 = df_fig.groupby(['Наименование груза ЦО-12', 'Направление']).agg(CON.AGG_PARAMS)
    df_fig2 = df_fig2.reset_index().sort_values('so_start', ascending=False)
    df_fig2['so_start'] = df_fig2['so_start'] / 1000000 # приводим тыс. к млрд.
    df_fig2['percentage'] = \
    df_fig2['percentage'] = df_fig2.groupby('Наименование груза ЦО-12')['so_start'].transform(lambda x: x / x.sum() * 100)
    #fig = px.bar(df_fig2, x="Наименование груза ЦО-12", y='so_start'], title="Wide-Form Input", color_discrete_sequence=px.colors.sequential.RdBu[::-1])
    fig = px.bar(df_fig2, x="Наименование груза ЦО-12", y="so_start", color="Направление", title='Стоиостная основа по видам грузов и направлениям',color_discrete_sequence=px.colors.sequential.RdBu[::-1], text=df_fig2['percentage'])
    fig.update_yaxes(title_text="Стоимостная основа, млрд. руб.", tickformat=".0f")
    fig.update_traces(hovertemplate="Наименование груза ЦО-12: %{x}<br>Направление: %{customdata}<br>Стоимостная основа: %{y}", customdata=df_fig2['Направление'])
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='auto')
    graph5 = dcc.Graph(figure=fig)
    so_by_cargos = dbc.Row([
        head1,
        dbc.Col([graph2], width=6),
        dbc.Col([graph3],width=6),
        dbc.Col([graph4], width=6),
        dbc.Col([graph5], width=6)
    ])
    # fig.update_layout(yaxis=dict(title='Значение'))
    return  html.Div(
        [total_values, table1, so_by_cargos, table3,graph_tarif, table2]
    )




def selectors():
    return html.Div([
        dbc.Button(
            "Группировки и фильтры",
            id="collapse_filters_button",
            className="mb-3 mx-2",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Card([
                dbc.CardBody([dbc.Row([
                    dbc.Col([
                        html.Label('Группировка верхнего уровня:',
                                   className="fw-bold"),
                        dcc.Dropdown(
                            id='group1_variant',
                            options=[
                                {'label': 'Наименование груза',
                                 'value': 'Наименование груза ЦО-12'},
                                {'label': 'Холдинг отправителя',
                                 'value': 'Холдинг отправителя'},
                                {'label': 'Направление',
                                 'value': 'Направление'},
                                {'label': 'Дорога выхода',
                                 'value': 'Наименование дороги выхода'},
                                {'label': 'Вид сообщения',
                                 'value': 'Вид сообщения'}
                            ],
                            value='Наименование груза ЦО-12',
                            clearable=False
                        ),
                        html.Label('Группировка внутри:',
                                   className="fw-bold mt-2"),
                        dcc.Dropdown(
                            id='group2_variant',
                            options=[
                                {'label': 'Наименование груза',
                                 'value': 'Наименование груза ЦО-12'},
                                {'label': 'Холдинг отправителя',
                                 'value': 'Холдинг отправителя'},
                                {'label': 'Направление',
                                 'value': 'Направление'},
                                {'label': 'Дорога выхода',
                                 'value': 'Наименование дороги выхода'},
                                {'label': 'Вид сообщения',
                                 'value': 'Вид сообщения'}
                            ],
                        ),
                    ], className='col-md-4'),
                    dbc.Col([
                        html.Label('Фильтр по грузу:', className="fw-bold"),
                        dcc.Dropdown(
                            id='cargo_filter',
                            options=[
                                {'label': cargo, 'value': cargo}
                                for cargo in CARGOS
                            ],
                        ),
                        html.Label('Фильтр по виду сообщения:',
                                   className="fw-bold mt-2"),
                        dcc.Dropdown(
                            id='message_filter',
                            options=[
                                {'label': message, 'value': message}
                                for message in MESSAGES
                            ],
                        ),
                    ], className='col-md-4'),
                    dbc.Col([
                        html.Label('Фильтр по направлению:',
                                   className="fw-bold"),
                        dcc.Dropdown(
                            id='side_filter',
                            options=[
                                {'label': side, 'value': side}
                                for side in SIDES
                            ],
                        ),
                        html.Label('Фильтр по холдингу:', className="mt-2 fw-bold",),
                        dcc.Dropdown(
                            id='holding_filter',
                            options=[
                                {'label': str(holding), 'value': str(holding)}
                                for holding in HOLDINGS
                            ],
                        )
                    ], className='col-md-4')
                ])])
            ]), id="collapse_filters",is_open=False,
        )
    ])


@callback(
    Output("collapse_filters", "is_open"),
    [Input("collapse_filters_button", "n_clicks")],
    [State("collapse_filters", "is_open")],
)
def toggle_collapse_filters(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("special_totals", "is_open"),
    [Input("collapse_special_button", "n_clicks")],
    [State("special_totals", "is_open")],
)
def toggle_collapse_special(n, is_open):
    if n:
        return not is_open
    return is_open


def make_table_so(df, params):
    table_1_body = html.Tbody([])
    if params['year_variant'][0] == '2026':
        new_t = 'so_start'
        old_t = CON.PR_P
        delta = 'delta_start'
    else:
        new_t = 'so_'+params['year_variant'][0]
        old_t = 'pp_'+params['year_variant'][0]
        delta = 'delta_'+params['year_variant'][0]
    for index, row in df.iterrows():
        if params['group2_variant'] is None or row[params['group2_variant']] == 'ИТОГО':
            label = row[params['group1_variant']]
            td_list = [html.Td(label, className='fw-bold')]
            highlight = True
        else:
            label = row[params['group2_variant']]
            td_list = [html.Td(label, className='')]
            highlight = False

        td_list = td_list + [html.Td(round(row[old_t] / 1000000, 2), className='fw-bold text-end' if highlight else 'text-end')]
        td_list = td_list + [html.Td(round(row[new_t] / 1000000, 2), className='fw-bold text-end' if highlight else 'text-end')]

        value, class_name = get_print_class(round(row[delta] / 1000000, 2))
        td_list = td_list + [html.Td(value,className=class_name)]

        table_1_body.children.append(
            html.Tr(td_list, className='bg-light' if highlight else ''),
        )


    first_row = [
        html.Th(params['label'], rowSpan='2', className='text-center align-middle'),
        html.Th("Действующие тарифные условия, млрд. руб.", className='text-center', style={'background-color': 'lightgray'}),
        html.Th("Новые тарифные условия, млрд. руб.", className='text-center',style={'background-color': 'lightgray'}),
        html.Th("Δ, млрд. руб.", className='text-center',  style={'background-color': 'lightgray'})
    ]

    second_row = [html.Th(params["year_variant"][0] + " г.", colSpan='1', className='text-center', style={'background-color': 'LightSkyBlue'})]
    second_row = second_row * 3

    table1 = dbc.Table(
        # header
        [html.Thead(
            [
                html.Tr(first_row),
                html.Tr(second_row),
            ],
        className='bg-light'),
            table_1_body
        ], className='table table-sm')

    return table1


def make_table2(df, params):
    if params['group2_variant'] is not None:
        col = params['group2_variant']
        df = df.loc[df[col] == 'ИТОГО']
    table_2_body = html.Tbody([])
    # итоги
    dty = round(df[CON.PR_P].sum() / 1000000, 2)  # действующие тарифные условия
    nty = round(df['so_column'].sum() / 1000000, 2)  # новые тарифные условия
    izm_1, izm_1_class = get_print_class(percentage_change(dty, nty))
    nty_inv = round(nty + df[CON.INVEST_DIRECTION].sum() / 1000000 + df[CON.INVEST_NETWORK].sum() / 1000000,2)
    izm_2, izm_2_class = get_print_class(percentage_change(dty, nty_inv))
    nty_inv_kap = round(nty_inv + df[CON.INVEST_REMONT].sum() / 1000000, 2)
    izm_3, izm_3_class = get_print_class(percentage_change(dty, nty_inv_kap))
    td_list = [html.Td('ВСЕГО', className='fw-bold')]
    td_list = td_list + [html.Td(dty, className='text-end')]
    td_list = td_list + [html.Td(nty, className='text-end')]
    td_list = td_list + [html.Td(izm_1, className=izm_1_class)]
    td_list = td_list + [html.Td(nty_inv, className='text-end')]
    td_list = td_list + [html.Td(izm_2, className=izm_2_class)]
    td_list = td_list + [html.Td(nty_inv_kap, className='text-end')]
    td_list = td_list + [html.Td(izm_3, className=izm_3_class)]
    table_2_body.children.append(html.Tr(td_list, className='bg-info'))

    for index, row in df.iterrows():
        dty = round(row[CON.PR_P] / 1000000, 2) # действующие тарифные условия
        nty = round(row['so_column'] / 1000000, 2) # новые тарифные условия
        izm_1,izm_1_class = get_print_class(percentage_change(dty, nty))
        nty_inv = round(nty + row[CON.INVEST_DIRECTION] / 1000000 + row[CON.INVEST_NETWORK] / 1000000, 2)
        izm_2, izm_2_class = get_print_class(percentage_change(dty, nty_inv))
        nty_inv_kap = round(nty_inv + row[CON.INVEST_REMONT] / 1000000, 2)
        izm_3, izm_3_class = get_print_class(percentage_change(dty, nty_inv_kap))
        td_list = [html.Td(row[params['group1_variant']], className='fw-bold')]
        td_list = td_list + [html.Td(dty,className='text-end')]
        td_list = td_list + [html.Td(nty,className='text-end')]
        td_list = td_list + [html.Td(izm_1, className=izm_1_class)]
        td_list = td_list + [html.Td(nty_inv, className='text-end')]
        td_list = td_list + [html.Td(izm_2, className=izm_2_class)]
        td_list = td_list + [html.Td(nty_inv_kap, className='text-end')]
        td_list = td_list + [html.Td(izm_3, className=izm_3_class)]
        table_2_body.children.append(html.Tr(td_list))


    table2 = dbc.Table(
        # header
        [html.Thead(
            [
                html.Tr([
                    html.Th(params['label'], className='text-center align-middle'),
                    html.Th('Действущие тарифные условия (ДТУ), млрд. руб.', className='text-center'),
                    html.Th('Новые тарифные условия (НТУ), млрд. руб.', className='text-center'),
                    html.Th('Δ к ДТУ, %', className='text-center'),
                    html.Th('НТУ+инвест. программа, млрд. руб.', className='text-center'),
                    html.Th('Δ к ДТУ, %', className='text-center'),
                    html.Th('НТУ+инвест. программа + кап.ремонт, млрд. руб.', className='text-center'),
                    html.Th('Δ к ДТУ, %', className='text-center'),
                ]),
            ],
            className='bg-light'),
            table_2_body
        ], className='table table-sm')

    invest_df = get_invest_data()
    invest_sum = round(invest_df.query('`Участие в расчете` == "Да"')['Сумма расходов на проекты, млрд руб'].sum() / 1000,2)
    kap_sum = round(df[CON.INVEST_REMONT].sum() / 1000000, 2)
    return dbc.Collapse([
        html.Hr(),
        html.H3('Итоги по 2026 г.'),
        html.P(html.Em('Таблица учитывает параметры сценария, фильтры и группировки')),
        html.P('Инвест. программа всего: '+ str(invest_sum) + ' трлн. руб.'),
        html.P('Кап. ремонт всего: '+ str(kap_sum) + ' млрд. руб.'),
        table2
    ],id='special_totals', is_open=False)


def make_table_tarif(df, params):
    table_3_body = html.Tbody([])
    if params['year_variant'][0] == '2026':
        new_t = 'so_start'
        old_t = CON.PR_P
        delta = 'delta_start'
    else:
        new_t = 'so_'+params['year_variant'][0]
        old_t = 'pp_'+params['year_variant'][0]
        delta = 'delta_'+params['year_variant'][0]

    for index, row in df.iterrows():
        if params['group2_variant'] is None or row[params['group2_variant']] == 'ИТОГО':
            label = row[params['group1_variant']]
            td_list = [html.Td(label, className='fw-bold')]
            highlight = True
        else:
            label = row[params['group2_variant']]
            td_list = [html.Td(label, className='')]
            highlight = False

        dty_v = round(row['Тариф на вагон_ДТУ'], 2)
        dty_t = round(row['Тариф на тонну_ДТУ'], 2)
        nty_v = round(row['Тариф на вагон_НТУ'], 2)
        nty_t = round(row['Тариф на тонну_НТУ'], 2)
        delta_v = nty_v - dty_v
        delta_t = nty_t - dty_t
        value_v, class_name_v = get_print_class(delta_v)
        value_t, class_name_t = get_print_class(delta_t)
        td_list = td_list + [
            html.Td(dty_v, className='fw-bold text-end' if highlight else 'text-end'),
            html.Td(dty_t, className='fw-bold text-end' if highlight else 'text-end'),
            html.Td(nty_v, className='fw-bold text-end' if highlight else 'text-end'),
            html.Td(nty_t,className='fw-bold text-end' if highlight else 'text-end'),
            html.Td(value_v, className=class_name_v),
            html.Td(value_t, className=class_name_t)
        ]


        table_3_body.children.append(
            html.Tr(td_list, className='bg-light' if highlight else ''),
        )

    first_row = [
        html.Th(params['label'], rowSpan='2', className='text-center align-middle'),
        html.Th("Действующие тарифные условия", colSpan=2, className='text-center', style={'background-color': 'lightgray'}),
        html.Th("Новые тарифные условия", colSpan=2, className='text-center',style={'background-color': 'lightgray'}),
        html.Th("Δ", className='text-center', colSpan=2,  style={'background-color': 'lightgray'})
    ]

    second_row = [
        html.Th("Тариф на вагон, тыс. руб.", colSpan='1', className='text-center', style={'background-color': 'LightSkyBlue'}),
        html.Th("Тариф на тонну, руб.", colSpan='1', className='text-center', style={'background-color': 'LightSkyBlue'})
    ]
    second_row = second_row * 3

    header3 = html.H4("Тарифы", className="mt-3")
    table3 = dbc.Table(
        # header
        [html.Thead(
            [
                html.Tr(first_row),
                html.Tr(second_row),
            ],
        className='bg-light'),
            table_3_body
        ], className='table table-sm')

    return html.Div([html.Hr(), header3, table3])

def draw_graph_tarif (df,params):
    if params['group2_variant'] is not None:
        col = params['group2_variant']
        df = df.loc[df[col] == 'ИТОГО']
    df = df.sort_values(['Тариф на вагон_ДТУ'],ascending=[False])
    df = df.fillna(0)
    fig = px.bar(df, x=params['group1_variant'],
                 y=["Тариф на вагон_ДТУ", "Тариф на вагон_НТУ"],
                 title='Тариф на вагон',
                 barmode="group",
                 color_discrete_sequence=px.colors.sequential.RdBu[::-1]
                 )
    fig.update_yaxes(title_text="Тариф на вагон, тыс. руб.", tickformat=".0f")
    fig.update_traces(texttemplate='%{y:.0f}', textposition='auto')
    graph1 = dcc.Graph(figure=fig)

    df = df.sort_values(['Тариф на тонну_ДТУ'], ascending=[False])
    fig = px.bar(df, x=params['group1_variant'],
                 y=["Тариф на тонну_ДТУ", "Тариф на тонну_НТУ"],
                 title='Тариф на тонну',
                 barmode="group",
                 color_discrete_sequence=px.colors.sequential.RdBu[::-1]
                 )
    fig.update_yaxes(title_text="Тариф на тонну, руб.", tickformat=".0f")
    fig.update_traces(texttemplate='%{y:.0f}', textposition='auto')
    graph2 = dcc.Graph(figure=fig)
    result = dbc.Row([
        dbc.Col([graph1], width=12),
        dbc.Col([graph2], width=12),
    ])
    return result

def get_print_class(value):
    if value > 0:
        item_class = 'text-success fw-bold text-end';
        item_print = '+' + str(round(value,2)) + ''
    elif value < 0:
        item_class = 'text-danger fw-bold text-end';
        item_print = str(round(value,2)) + ''
    else:
        item_class = 'text-dark fw-bold text-end';
        item_print = '-'
    return item_print, item_class



def get_costs_column(option):
    if option == 'option1':
        return CON.PER
    elif option == 'option2':
        return CON.POL
    elif option == 'option3':
        return CON.POL_CAP


