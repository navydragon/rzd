import dash
from dash import dcc
from dash import html
from dash import dash_table, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import time
import random
import dash_bootstrap_components as dbc

# dash.register_page(__name__, name="Холдинги", path='/holdings', order=1)

# parameters = html.Div([
#     html.Div([
#         dbc.Col(dbc.Card([
#             dbc.CardHeader("Параметры сценария"),
#             dbc.CardBody(
#                 [
#                     dbc.Row([
#                         dbc.Col([
#                             html.Label('Дифференциация по направлениям:',
#                                        style={"font-weight": "bold"}),
#                             dcc.Dropdown(
#                                 id='direction_variant',
#                                 options=[
#                                     {'label': 'Среднесетевой вариант',
#                                      'value': 'option1'},
#                                     {'label': 'Вариант по 3 зонам',
#                                      'value': 'option2'},
#                                     {'label': 'Комбинированный вариант',
#                                      'value': 'option3'}
#                                 ],
#                                 value='option2'
#                             ),
#                         ], className='col-md-6')
#                     ])
#                 ]
#             ),
#         ], color="light")),
#     ], className="m-4", ),
# ])
#
#
# def get_data():
#     df = pd.read_csv('data/holdings_routes.csv',delimiter=";",decimal=",",thousands=" ")
#
#     df = df.dropna(subset=['Наименование дороги выхода', 'Холдинг отправителя'])
#     df = df.reset_index(drop=True)
#     directions = pd.read_excel('data/references/road_direction.xlsx')
#     df = pd.merge(df, directions, left_on='Наименование дороги выхода',
#                   right_on='Дорога', how='inner')
#
#     return df
#
#
# def cost_index_multiply(index_df, year):
#   parameter = 'Темп роста себестоимости (грузовые перевозки)'
#   total_index = index_df.query('Параметр == @parameter and Год <= @year')['Значение'].prod()
#   return total_index
#
#
# def calculate_data(df,index_df):
#   d_yper = 'Доля условно-переменных расходов, %'
#   d_ypos = 'Доля условно-постоянных расходов, %'
#   yper = 'Условно-переменные расходы, руб'
#   ypos = 'Условно-постоянные расходы, руб'
#   so_1 = 'Стоимостная основа, вариант по 3-м зонам, тыс. руб'
#   so_1_new = 'Стоимостная основа, вариант по 3-м зонам 2026, тыс. руб'
#   so_2 = 'Стоимостная основа, среднесетевой вариант, тыс. руб'
#   so_2_new = 'Стоимостная основа, среднесетевой вариант 2026, тыс. руб'
#   so_3 = 'Стоимостная основа, комбинированный вариант, тыс. руб'
#   so_3_new = 'Стоимостная основа, комбинированный вариант 2026, тыс. руб'
#   df[d_yper] = df[yper] * 100 / (df[yper] + df[ypos])
#   df[d_ypos] = df[ypos] * 100 / (df[yper] + df[ypos])
#   so_index = cost_index_multiply(index_df, 2026)
#   df[so_1_new] = df[so_1] * so_index
#   df[so_2_new] = df[so_2] * so_index
#   df[so_3_new] = df[so_3] * so_index
#   return df
#
#
# index_df = pd.read_excel('data/indexes.xlsx', sheet_name='Лист1')
# df = get_data()
# df = calculate_data(df, index_df)
#
# table1 = html.Div([
#     dash_table.DataTable(
#         id='table',
#         columns=[{"name": i, "id": i} for i in
#                  df.columns],
#         data=df.to_dict('records'),
#     )
# ])
#
# table2 = html.Div([
#     dash_table.DataTable(
#         id='table',
#         columns=[{"name": i, "id": i} for i in
#                  ['column1', 'column2', 'column3']],
#         data=[{'column1': 'value1', 'column2': 'value2',
#                'column3': 'value3'},
#               {'column1': 'value4', 'column2': 'value5',
#                'column3': 'value6'},
#               {'column1': 'value7', 'column2': 'value8',
#                'column3': 'value9'}]
#     )
# ])
# main_div = html.Div([
#     dbc.Row([
#         dbc.Col([
#             html.Div([dcc.Graph(id='graph')]),
#         ], className='col-md-6'),
#         dbc.Col([
#             html.Div([dcc.Graph(id='graph2')]),
#         ], className='col-md-6')
#     ]),
#     dbc.Row([
#         dbc.Col([table1], className='col-md-6'),
#         # dbc.Col([table2], className='col-md-6')
#     ])
# ], className='m-4')
#
#
# def layout():
#     cargos = df['Наименование груза ЦО-12'].unique()
#     return html.Div([
#         html.H2('Dashboard по холдингам', className="m-4"),
#         parameters,
#         html.H2('Показатели перевозок', className='m-4'),
#         dcc.Loading(
#             id="loading-1",
#             type="default",
#             children=html.Div(id="loading-output-1")
#         ),
#         html.Div([
#             html.Div([
#                 html.Label("Показать направления"),
#                 dbc.Switch(id="show_sides")], className='col-md-3'),
#             html.Div([
#                 html.Label('Выберите грузы'),
#                 dcc.Dropdown(
#                     cargos,
#                     ['Уголь каменный', 'Кокс каменноугольный',
#                      'Нефть и нефтепродукты', 'Руды металлические'],
#                     multi=True,
#                     id='cargo_select'
#                 ),
#             ], className='col-md-9'),
#         ], className='row mx-4'),
#         html.Div([], id='holdings_main_div'),
#     ])
#
#
# def get_attr_names():
#     return {
#         'pl0': 'Грузооборот брутто млн. ткм',
#         'pl1': 'Грузооборот новый, млн. ткм',
#         'pp0': 'Провозная плата из накладных, тыс. руб',
#         'so0': 'Стоимостная основа, помаршрутный вариант, тыс. руб',
#         'so11': 'Стоимостная основа, вариант по 3-м зонам, тыс. руб',
#         'so12': 'Стоимостная основа, среднесетевой вариант, тыс. руб',
#         'so13': 'Стоимостная основа, комбинированный вариант, тыс. руб',
#         'pp1': 'Провозная плата новая, тыс. руб',
#         'p0': 'Погрузка, тыс. тонн',
#         'p1': 'Погрузка новая, тыс. тонн',
#         'delta_d': 'Δ доходной ставки, %',
#         'delta_p': 'Δ объема погрузки, %',
#         'delta_pr': 'Δ прибыли, тыс. руб',
#     }
#
#
# def get_print_class(value):
#     if value > 0:
#         item_class = 'text-success fw-bold text-end';
#         item_print = '+' + str(value) + ''
#     elif value < 0:
#         item_class = 'text-danger fw-bold text-end';
#         item_print = str(value) + ''
#     else:
#         item_class = 'text-dark fw-bold text-end';
#         item_print = '-'
#     return item_print, item_class
#
# @callback(
#     Output('holdings_main_div', 'children'),
#     Input('direction_variant', 'value'),
#     Input('show_sides', 'value'),
#     Input('cargo_select', 'value')
# )
# def update_dashboard(variant, show_sides, cargos):
#     params = {
#         "direction_variant": variant,
#         "show_sides": show_sides,
#         "cargos": cargos,
#     }
#
#     if len(params['cargos']) > 0:
#         df_filtered = df[df['Наименование груза ЦО-12'].isin(params['cargos'])]
#     else:
#         df_filtered = df
#
#     so_1_new = 'Стоимостная основа, среднесетевой вариант 2026, тыс. руб'
#     so_2_new = 'Стоимостная основа, вариант по 3-м зонам 2026, тыс. руб'
#     so_3_new = 'Стоимостная основа, комбинированный вариант 2026, тыс. руб'
#
#     if params['direction_variant'] == 'option1':
#         so1 = so_1_new
#     elif params['direction_variant'] == 'option2':
#         so1 = so_2_new
#     elif params['direction_variant'] == 'option3':
#         so1 = so_3_new
#
#     df_grouped0 = df_filtered.groupby(['Холдинг отправителя']).agg({
#         'Погрузка, тыс. тонн': 'sum',
#         'Количество вагоноотправок': 'sum',
#         'Погрузка, ваг': 'sum',
#         'Грузооборот брутто млн. ткм': 'sum',
#         'Провозная плата из накладных, тыс. руб': 'sum',
#         'Стоимостная основа, помаршрутный вариант, тыс. руб' : 'sum',
#         'Стоимостная основа, среднесетевой вариант, тыс. руб': 'sum',
#         'Стоимостная основа, вариант по 3-м зонам, тыс. руб': 'sum',
#         'Стоимостная основа, комбинированный вариант, тыс. руб': 'sum',
#         'Условно-переменные расходы, руб': 'sum',
#         'Условно-постоянные расходы, руб': 'sum',
#     })
#
#     df_grouped0 = calculate_data(df_grouped0, params)
#     df_grouped0 = df_grouped0.sort_values(by='Грузооборот брутто млн. ткм')
#     if params['show_sides']:
#         df_grouped = df_filtered.groupby(
#             ['Холдинг отправителя', 'Направление']).agg({
#             'Погрузка, тыс. тонн': 'sum',
#             'Количество вагоноотправок': 'sum',
#             'Погрузка, ваг': 'sum',
#             'Грузооборот брутто млн. ткм': 'sum',
#             'Провозная плата из накладных, тыс. руб': 'sum',
#             'Стоимостная основа, помаршрутный вариант, тыс. руб' : 'sum',
#             'Стоимостная основа, среднесетевой вариант, тыс. руб': 'sum',
#             'Стоимостная основа, вариант по 3-м зонам, тыс. руб': 'sum',
#             'Стоимостная основа, комбинированный вариант, тыс. руб': 'sum',
#             'Условно-переменные расходы, руб': 'sum',
#             'Условно-постоянные расходы, руб': 'sum',
#         })
#         df_grouped = calculate_data(df_grouped, params)
#
#
#     table_1_body = html.Tbody([])
#     for index, row in df_grouped0.iterrows():
#         delta_so_for_variant = (row[so1] - row['Стоимостная основа, помаршрутный вариант, тыс. руб']) / row['Стоимостная основа, помаршрутный вариант, тыс. руб']
#         delta_so = {'value': round(delta_so_for_variant * 100, 2)}
#         delta_so['print'], delta_so['class'] = get_print_class(delta_so['value'])
#
#         table_1_body.children.append(
#             html.Tr([
#                 html.Td(index, className='fw-bold'),
#                 html.Td(delta_so['print'], className=delta_so['class']),
#             ], className='bg-light' if params['show_sides'] else ''
#             ),
#         )
#         if params['show_sides']:
#             sides = df_grouped[df_grouped.index.isin([index], level=0)]
#             for s_index, s_row in sides.iterrows():
#                 delta_so_for_variant = (s_row[so1] - row['Стоимостная основа, помаршрутный вариант, тыс. руб']) / s_row['Стоимостная основа, помаршрутный вариант, тыс. руб']
#                 delta_so = {'value': round(delta_so_for_variant * 100, 2)}
#                 delta_so['print'], delta_so['class'] = get_print_class(delta_so['value'])
#
#                 table_1_body.children.append(
#                     html.Tr([
#                         html.Td(s_index[1]),
#                         html.Td(delta_so['print'], className=delta_so['class']),
#                     ]),
#                 )
#     table1 = dbc.Table(
#         # header
#         [html.Thead(html.Tr(
#             [html.Th("Наименование компании", className='text-center'),
#              html.Th("Δ стоимостной основы к 2026, %", className='text-center'),
#              ])),
#             # body
#             table_1_body
#         ], className='m-4')
#
#     # график
#     fig = px.treemap(df_filtered, path=[px.Constant("Направления"), 'Направление', 'Холдинг отправителя', 'Наименование груза ЦО-12'],
#                      values='Погрузка, тыс. тонн')
#     fig.update_traces(root_color="lightgrey")
#     fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
#
#     return html.Div([
#         html.Div([
#             html.H5('Показатели перевозок', className='m-4'),
#             table1], className='col mx-5'),
#         html.Div([
#             html.H5('Объем погрузки по направлениям и холдингам', className='mx-4 mt-4'),
#             dcc.Graph(figure=fig)
#         ], className='col')
#     ], className='row')