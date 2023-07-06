import dash
from dash import dcc
from dash import html
from dash import dash_table, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import time
import random
import dash_bootstrap_components as dbc
from pages.helper import load_data, get_indexes_data
# dash.register_page(__name__, name="Dashboard", path='/', order=0)


# base_routes_df = load_data()





SUFFIX = '_home'
def layout():
    return html.H2('Dashboard', className="m-4")
    table1 = html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in
                     base_routes_df.columns],
            data=base_routes_df.to_dict('records'),
        )
    ])

    cargos = base_routes_df['Наименование груза ЦО-12'].unique()
    return html.Div([
        html.H2('Dashboard', className="m-4"),
        scenario_parameters(SUFFIX),
        html.H2('Показатели', className='m-4'),
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        ),
        html.Div([
            # html.Div([
                # html.Label("Показать направления"),
                # dbc.Switch(id="show_sides")], className='col-md-3'),
            html.Div([
                html.Label('Выберите грузы'),
                dcc.Dropdown(
                    cargos,
                    [],
                    multi=True,
                    id='cargo_select'
                ),
            ], className='col-md-9'),
        ], className='row mx-4'),
        html.Div([], id='main_div'),
    ])

START_YEAR = 2026
SO_PM = 'Помаршрутная СО, тыс. руб.'
SO_3Z = 'Вариант по 3м зонам СО, тыс. руб.'
SO_SS = 'Среднесетевая СО, тыс. руб.'
SO_KB = 'Комбинированная СО, тыс. руб.'
SO_PM_DIFF = 'Помаршрутная СО с дифференциацией, тыс. руб.'
SO_3Z_DIFF = 'Вариант по 3м зонам СО с дифференциацией, тыс. руб.'
SO_SS_DIFF = 'Среднесетевая СО с дифференциацией, тыс. руб.'
SO_KB_DIFF = 'Комбинированная СО с дифференциацией, тыс. руб.'
PER = 'Условно-переменные расходы, тыс. руб'
PER_DOL = 'Доля переменных расходов'
POST = 'Условно-постоянные расходы, тыс. руб'
POST_DOL = 'Доля постоянных расходов'
POL = 'Расходы полные, тыс. руб'
CAP = 'Инвест ремонт, тыс. руб'
POL_CAP = 'Расходы полные + инвест ремонт, тыс. руб'
PR_P = 'Провозная плата из накладных, тыс. руб'
EPL = 'Грузооборот брутто, тыс. ткм'
P = 'Перевезено груженых, тыс. тонн'
INVEST_REMONT = 'Капитальные вложения(инвест),тыс. руб.'
INVEST_NETWORK = 'Расходы на общесетевые инвестпроекты, тыс. руб.'
INVEST_DIRECTION = 'Расходы на инвестпроекты по направлениям, тыс. руб.'
NETWORK_PART = 'Доля от расходов на общесетевые проекты'
DIRECTION_PART = 'Доля от расходов на проекты по направлениям'
index_df = get_indexes_data()

@callback(
    Output('main_div', 'children'),
    Input('costs_base_variant'+SUFFIX,'value'), # ЦПС/расходы
    Input('costs_variant'+SUFFIX, 'value'), # переменные/полные
    Input('approach_variant'+SUFFIX, 'value'), # дифференциация тарифов
    Input('direction_variant'+SUFFIX, 'value'), # ЦПС вариант
    Input('turnover_variant'+SUFFIX, 'value'),
    Input('invest_variant'+SUFFIX, 'value'),
    Input('year_variant'+SUFFIX, 'value'),
    Input('cargo_select', 'value')
)
def update_dashboard(
        costs_base_variant,
        costs_variant,
        approach_variant,
        direction_variant,
        turnover_variant,
        invest_variant,
        year_variant,
        cargo_select):
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
    }
    # рассчитываем параметры
    agg_params = {
        P: 'sum',
        EPL: 'sum',
        PR_P: 'sum',
        SO_PM: 'sum',
        SO_SS: 'sum',
        SO_3Z: 'sum',
        SO_KB: 'sum',
        PER: 'sum',
        POST: 'sum',
        POL: 'sum',
        'so_start': 'sum',
        'delta_start': 'sum',
        'Код группы по ЦО-12': 'min'
    }
    for year in params['year_variant']:
        agg_params['so_'+year] = 'sum'
        agg_params['pp_' + year] = 'sum'
        agg_params['delta_' + year] = 'sum'
    group1_variant = 'Наименование груза ЦО-12'
    sorting_param = 'Код группы по ЦО-12' if group1_variant=='Наименование груза ЦО-12' else EPL
    sorting_asc = True if group1_variant=='Наименование груза ЦО-12' else False

    df = calculate_data(base_routes_df, index_df, params)

    # фильтруем данные
    if not isinstance(cargo_select, list):
        cargo_select = [cargo_select]
    if len(cargo_select) > 0:
        df = df[df['Наименование груза ЦО-12'].isin(cargo_select)]
    # группируем данные
    df_grouped1 = df.groupby([group1_variant]).agg(agg_params)

    df_grouped1 = df_grouped1.sort_values(by=sorting_param, ascending=sorting_asc)

    so = df_grouped1['so_start'].sum() / 1000000
    pp = df_grouped1[PR_P].sum() / 1000000
    ee = df_grouped1['delta_start'].sum() / 1000000
    table1 =html.Div([
        dbc.Row ([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Стоимостная основа"),
                dbc.CardBody(
                    [
                        html.Label(round(so), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Провозная плата"),
                dbc.CardBody(
                    [
                        html.Label(round(pp), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Экономический эффект"),
                dbc.CardBody(
                    [
                        html.Label(round(ee), className="fw-bold"),
                        html.Span(' млрд. руб.')
                    ]
                ),
            ], color="light"), width=4),
        ])

        ], className="m-4", )


    return table1


def calculate_data(df, index_df, params):
    so_column = get_so_column (params)
    # costs_column = get_costs_column (params['costs_variant'])
    #df['so_2019'] = df[[so_column, costs_column]].max(axis=1)
    df['so_start'] = df[so_column]

    if 'option1' in params['invest_variant']:
        df['so_start'] = df['so_start'] + df[INVEST_REMONT]


    # инвест проекты
    invest_df = pd.read_excel('data/initial/invest.xlsx')
    invest_grouped = invest_df.query('`Участие в расчете` == "Да"').groupby('Направление')['Сумма расходов на проекты, тыс руб'].sum()

    # инвестиции общесетевые
    if 'option2' in params['invest_variant']:
        network_value = invest_grouped['Сеть']
        df[INVEST_NETWORK] = df[NETWORK_PART] * network_value
        df['so_start'] = df['so_start'] + df[INVEST_NETWORK]

    #инвестиции по направлениям
    if 'option3' in params['invest_variant']:
        df[INVEST_DIRECTION] = df[DIRECTION_PART] * df['Направление'].map(invest_grouped)
        df['so_start'] = df['so_start'] + df[INVEST_DIRECTION]

    df['delta_start'] = df[PR_P] - df['so_start']


    if params['turnover_variant'] == 'option2':
        fp_df = pd.read_csv('data/initial/fin_plan_types.csv')
        fp_df = fp_df.query('`Вид сообщения` == "общий уровень"')
    if params['turnover_variant'] == 'option3':
        fp_df = pd.read_csv('data/initial/fin_plan_05.csv', delimiter=';',decimal=',',encoding='windows-1251')

    for year in params["year_variant"]:
        year_int = int(year)
        if params['turnover_variant'] == 'option1':
            turn_index = 1
        elif params['turnover_variant'] == 'option2':
            df2 = fp_df.query('Год == @year_int')
            df = df.merge(
                df2[['Груз', 'Индекс грузооборота']],
                left_on=['Наименование груза ЦО-12'],
                right_on=['Груз'],
                how='inner'
            )
            turn_index = df['Индекс грузооборота']
            df = df.rename(columns={'Индекс грузооборота': 'Индекс грузооборота_' + year})
        elif params['turnover_variant'] == 'option3':
            df2 = fp_df.query('Год == @year_int')
            df = df.merge(
                df2[['Наименование груза ЦО-12','Направление', 'Вид сообщения', 'Индекс грузооборота']],
                left_on=['Наименование груза ЦО-12','Направление', 'Вид сообщения'],
                right_on=['Наименование груза ЦО-12','Направление', 'Вид сообщения'],
                how='inner'
            )
            turn_index = df['Индекс грузооборота']
            df = df.rename(columns={'Индекс грузооборота': 'Индекс грузооборота_' + year})



        # индекс изменения себестоимости
        so_index = cost_index_multiply(index_df, int(year),START_YEAR)
        # индекс изменения тарифов
        tf_index = tarif_index_multiply(index_df, int(year),START_YEAR)
        # грузооборот_новый
        df['epl_'+year] = df[EPL] * turn_index
        # провозная плата
        df['pp_' + year] = df[PR_P] * tf_index * turn_index
        # расходы полные без изменения грузооборота
        df['costs_wo_epl_'+year] = (df[POST] * so_index) + (df[PER] * so_index)
        # расходы полные с изменением грузооборота
        df['costs_w_epl_' + year] = (df[POST] * so_index) + (df[PER] * so_index * turn_index)
        # индекс изменения полных расходов
        df['ipr'] = df['costs_w_epl_' + year] / df['costs_wo_epl_'+year]
        # стоимостная основа
        df['so_'+year] = df['so_start'] * df['ipr'] * so_index

        df['delta_'+year] = df['pp_'+year] - df['so_'+year]
    return df
def update_dashboard(pl_izm, pl_coal, direction_variant, show_sides, cargos):
    pl_izm = pd.to_numeric(pl_izm, errors='coerce')
    params = {
        "pl_izm": pl_izm,
        "pl_coal": pl_coal,
        "direction_variant": direction_variant,
        "show_sides": show_sides,
        "cargos": cargos,
    }
    if len(params['cargos']) > 0:
        df_filtered = df[df['Наименование груза ЦО-12'].isin(params['cargos'])]
    else:
        df_filtered = df

    attrs = get_attr_names()
    delta_d, delta_p, delta_pr = attrs['delta_d'], attrs['delta_p'], attrs[
        'delta_pr']

    df_grouped0 = df_filtered.groupby(['Наименование груза ЦО-12']).agg({
        'Погрузка, тыс. тонн': 'sum',
        'Грузооборот брутто млн. ткм': 'sum',
        'Провозная плата из накладных, тыс. руб': 'sum',
        'Стоимостная основа, помаршрутный вариант, тыс. руб': 'sum',
        'Стоимостная основа, среднесетевой вариант, тыс. руб': 'sum',
        'Стоимостная основа, вариант по 3-м зонам, тыс. руб': 'sum',
        'Стоимостная основа, комбинированный вариант, тыс. руб': 'sum',
        'order': 'max'
    })

    df_grouped0 = calculate_df(df_grouped0, params)
    df_grouped0 = df_grouped0.sort_values(by='order')

    if params['show_sides']:
        df_grouped = df_filtered.groupby(
            ['Наименование груза ЦО-12', 'Направление']).agg({
            'Погрузка, тыс. тонн': 'sum',
            'Грузооборот брутто млн. ткм': 'sum',
            'Провозная плата из накладных, тыс. руб': 'sum',
            'Стоимостная основа, помаршрутный вариант, тыс. руб': 'sum',
            'Стоимостная основа, среднесетевой вариант, тыс. руб': 'sum',
            'Стоимостная основа, вариант по 3-м зонам, тыс. руб': 'sum',
            'Стоимостная основа, комбинированный вариант, тыс. руб': 'sum',
            'order': 'max',
        })
        df_grouped = calculate_df(df_grouped, params)
        # df_grouped = df_grouped.reset_index(level=0)
    table_1_body = html.Tbody([])

    for index, row in df_grouped0.iterrows():
        dd = {'value': round(row[delta_d] * 100, 2)}
        dd['print'], dd['class'] = get_print_class(dd['value'])

        dp = {'value': round(row[delta_p] * 100, 2)}
        dp['print'], dp['class'] = get_print_class(dp['value'])

        dpr = {'value': round(row[delta_pr] / 1000, 2)}
        dpr['print'], dpr['class'] = get_print_class(dpr['value'])

        table_1_body.children.append(
            html.Tr([
                html.Td(index, className='fw-bold'),
                html.Td(dd['print'], className=dd['class']),
                html.Td(dp['print'], className=dp['class']),
                html.Td(dpr['print'], className=dpr['class']),
            ], className='bg-light' if params['show_sides'] else ''
            ),
        )
        if params['show_sides']:
            sides = df_grouped[df_grouped.index.isin([index], level=0)]
            for s_index, s_row in sides.iterrows():
                dd = {'value': round(s_row[delta_d] * 100, 2)}
                dd['print'], dd['class'] = get_print_class(dd['value'])

                dp = {'value': round(s_row[delta_p] * 100, 2)}
                dp['print'], dp['class'] = get_print_class(dp['value'])

                dpr = {'value': round(s_row[delta_pr] / 1000, 2)}
                dpr['print'], dpr['class'] = get_print_class(dpr['value'])

                table_1_body.children.append(
                    html.Tr([
                        html.Td(s_index[1]),
                        html.Td(dd['print'], className=dd['class']),
                        html.Td(dp['print'], className=dp['class']),
                        html.Td(dpr['print'], className=dpr['class']),
                        html.Td()
                    ]),
                )
    table1 = dbc.Table(
        # header
        [html.Thead(html.Tr(
            [html.Th("Наименование груза", className='text-center'),
             html.Th("Δ доходной ставки, %", className='text-center'),
             html.Th("Δ объема погрузки, %", className='text-center'),
             html.Th("Δ прибыли, млн. руб", className='text-center')])),
            # body
            table_1_body
        ], className='m-4')

    # Создаем DataFrame для данных
    rzd_pr = df_grouped0[delta_pr].sum() / 1000000
    rzd_pr = random.randint(-10, 25)
    gos_pr = random.randint(-10, 25)
    biz_pr = random.randint(-10, 25)
    dfg = pd.DataFrame({'Категория': ['РЖД', 'Государство', 'Бизнес'],
                        'Прибыль': [rzd_pr, gos_pr, biz_pr]})

    # Создаем фигуру
    fig = go.Figure()

    # Добавляем столбчатую диаграмму для отрицательных значений
    fig.add_trace(go.Bar(x=dfg[dfg['Прибыль'] < 0]['Прибыль'],
                         y=dfg[dfg['Прибыль'] < 0]['Категория'],
                         orientation='h',
                         text=dfg[dfg['Прибыль'] < 0]['Прибыль'],
                         textfont=dict(size=16),
                         textposition='auto',
                         marker=dict(color='red')))

    # Добавляем столбчатую диаграмму для положительных значений
    fig.add_trace(go.Bar(x=dfg[dfg['Прибыль'] >= 0]['Прибыль'],
                         y=dfg[dfg['Прибыль'] >= 0]['Категория'],
                         text=[f'{val:+}' if val > 0 else str(val) for val in
                               dfg[dfg['Прибыль'] >= 0]['Прибыль']],
                         textfont=dict(size=16),
                         textposition='auto',
                         orientation='h',
                         marker=dict(color='blue')))

    # Устанавливаем параметры макета
    fig.update_layout(
        xaxis_title='Прибыль',
        yaxis_title='Категория',
        barmode='overlay',
        margin={'t': 50}
    )
    # Скрываем легенду
    fig.update_traces(showlegend=False)

    return html.Div([
        html.Div([
            html.H5('Показатели перевозок', className='m-4'),
            table1], className='col mx-5'),
        # html.Div([],className='col-2'),
        html.Div([
            html.H5('Макроэффекты, млн. руб.', className='mx-4 mt-4'),
            dcc.Graph(figure=fig)
        ], className='col')
    ], className='row')



def get_attr_names():
    return {
        'pl0': 'Грузооборот брутто млн. ткм',
        'pl1': 'Грузооборот новый, млн. ткм',
        'pp0': 'Провозная плата из накладных, тыс. руб',
        'so0': 'Стоимостная основа, помаршрутный вариант, тыс. руб',
        'so11': 'Стоимостная основа, вариант по 3-м зонам, тыс. руб',
        'so12': 'Стоимостная основа, среднесетевой вариант, тыс. руб',
        'so13': 'Стоимостная основа, комбинированный вариант, тыс. руб',
        'pp1': 'Провозная плата новая, тыс. руб',
        'p0': 'Погрузка, тыс. тонн',
        'p1': 'Погрузка новая, тыс. тонн',
        'delta_d': 'Δ доходной ставки, %',
        'delta_p': 'Δ объема погрузки, %',
        'delta_pr': 'Δ прибыли, тыс. руб',
    }


def calculate_df(df, params):
    attrs = get_attr_names()
    pl0, pl1, pp0, so0, so11, so12, so13, pp1, p0, p1, delta_d, delta_p, delta_pr = attrs.values()

    # считаем R
    df['R'] = df[pp0] / df[so0] - 1

    if params['direction_variant'] == 'option1':
        so1 = so11
    elif params['direction_variant'] == 'option2':
        so1 = so12
    elif params['direction_variant'] == 'option3':
        so1 = so13
    # else: so1 = so11

    # считаем pp1
    df[pp1] = df[so1] * (1 + df['R'])

    # считаем pl1
    #df[pl1] = df[pl0] * (1 + params['pl_izm'] / 100)
    df[pl1] = df.apply(calculate_pl1, args=(params['pl_izm'],params['pl_coal']),axis=1)
    # считаем Δd
    dr1 = df[pp1] / df[pl1]
    dr0 = df[pp0] / df[pl0]
    df[delta_d] = (dr1 - dr0) / dr0

    # считаем l0
    l0 = df[pl0].sum() / df[p0].sum()
    # считаем p1
    df[p1] = df[pl1] / l0
    # считаем Δp
    df[delta_p] = (df[p1] - df[p0]) / df[p0]

    # считаем прибыль
    df[delta_pr] = (df[pp1] - df[so1]) - (df[pp0] - df[so0])
    return df

def get_so_column(params):
    if params['costs_base_variant'] == 'option1': #ЦПС
        if params['approach_variant'] == 'option1': #плоские
            if params['direction_variant'] == 'option1': #пл_сс
                return SO_SS
            elif params['direction_variant'] == 'option2':  # пл_3з
                return SO_3Z
            elif params['direction_variant'] == 'option3':  # пл_комб
                return SO_KB
            else: # пл_пом
                return SO_PM
        else: # с дифф
            if params['direction_variant'] == 'option1': #дифф_сс
                return SO_SS_DIFF
            elif params['direction_variant'] == 'option2':  # дифф_3з
                return SO_3Z_DIFF
            elif params['direction_variant'] == 'option3':  # дифф_комб
                return SO_KB_DIFF
            else: # дифф_пом
                return SO_PM_DIFF
    else: #расходы
        if params['costs_variant'] == 'option1':
            return PER
        return POL

def get_print_class(value):
    if value > 0:
        item_class = 'text-success fw-bold text-end';
        item_print = '+' + str(value) + ''
    elif value < 0:
        item_class = 'text-danger fw-bold text-end';
        item_print = str(value) + ''
    else:
        item_class = 'text-dark fw-bold text-end';
        item_print = '-'
    return item_print, item_class


def calculate_pl1(row, pl_izm, pl_coal):
    if row['order'] == 1: # уголь
        return row['Грузооборот брутто млн. ткм'] * (1 + pl_coal / 100)
    else:
        return row['Грузооборот брутто млн. ткм'] * (1 + pl_izm / 100)


@callback(
    [Output("cps_parameters"+SUFFIX, "style"),Output("costs_parameters"+SUFFIX, "style")],
    Input("costs_base_variant"+SUFFIX, "value"),
)
def switch_base_variant(costs_base_variant):
    if costs_base_variant == 'option1':
        return {"display": "block"}, {"display": "none"}
    return {"display": "none"}, {"display": "block"}
