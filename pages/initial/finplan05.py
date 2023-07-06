from dash import html, dcc, Dash, dash_table, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc

POSTFIX = '_may'

def get_variants():
    return [
        {'label': 'Фин.план. (базовый)', 'value': 'fin_plan'},
        {'label': 'Фин.план. (измененный)', 'value': 'fin_plan_izm'}
    ]


def get_data():
    # df = pd.read_csv('data/initial/fin_plan_types.csv').astype('str')
    df = pd.read_csv('data/initial/fin_plan_05.csv', delimiter=';',decimal=',',encoding='windows-1251').astype('str')

    df[PL] = pd.to_numeric(df[PL])

    return df


def finplan05_layout():
    global df
    df = get_data()
    return html.Div([
        html.H3('Грузооборот по финансовому плану'),
        selectors(),
        html.Div([], id='datatable_div'+POSTFIX, className='m-2'),
    ], className='m-2')


# названия столбцов
P = 'Погрузка, млн. т'
P_BASE = 'Погрузка базовая, млн. т'
PL = 'Грузооборот, млрд. ткм'
PL_BASE = 'Грузооборот базовый, млрд. ткм'
PL_INDEX = 'Индекс грузооборота'
IPER = 'Индекс перевезено'
CARGO = 'Наименование груза ЦО-12'


def draw_table_pl(df_part):
    # print (df_part)
    columns_to_display = [CARGO, 'Год', 'Вид сообщения', 'Направление', PL,PL_INDEX]
    table = dash_table.DataTable(
        id='datatable_pl'+POSTFIX,
        data=df_part.to_dict('records'),
        columns=[
            {'name': col, 'id': col, 'editable': (col == PL)}
            for col in columns_to_display
        ],
        sort_action='native',
        page_size=11,
        style_cell_conditional=[
            {'if': {'column_id': CARGO}, 'textAlign': 'left'},
            {'if': {'column_id': 'Год'}, 'textAlign': 'left'},
            {'if': {'column_id': 'Вид сообщения'}, 'textAlign': 'left'},
        ],
        style_data_conditional=[
            {'if': {'column_editable': False}, 'backgroundColor': 'lightgray'},
        ],
        style_header={'fontWeight': 'bold'},
        editable=True,
    )
    return table


@callback(
    Output('datatable_pl'+POSTFIX, 'data'),
    Input('datatable_pl'+POSTFIX, 'data'),
    State('datatable_pl'+POSTFIX, 'data_previous'),
    State('datatable_pl'+POSTFIX, 'start_cell'),
    State('datatable_pl'+POSTFIX, 'page_current'),
    State('datatable_pl'+POSTFIX, 'page_size'),
    prevent_initial_call=True
)
def calculate_and_save_pl(data, data_previous,start_cell,page_current,page_size):
    global df
    if page_current is None : page_current = 0
    changed_index = int(start_cell['row']) + int(page_current) * int(page_size) - 1
    updated_row = data[changed_index]
    # print (updated_row)
    row_index = updated_row['row_index']
    updated_df = pd.DataFrame.from_records(data)
    cols_to_numeric = [PL, 'Грузооборот 2019']
    updated_df[cols_to_numeric] = updated_df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')

    # формула расчета индекса
    updated_df.loc[changed_index, PL_INDEX] = updated_df.loc[changed_index, PL] / updated_df.loc[changed_index, 'Грузооборот 2019']
    # заполняем исходный df
    df.loc[df['row_index'] == row_index, [PL,PL_INDEX]] = [updated_df.loc[changed_index, PL],updated_df.loc[changed_index, PL_INDEX]]
    df.to_csv('data/initial/fin_plan_types.csv', index=False)
    return updated_df.to_dict('records')



@callback(
    Output('datatable_div'+POSTFIX, 'children'),
    Input('message_dropdown'+POSTFIX, 'value'),
    Input('direction_dropdown'+POSTFIX, 'value'),
    Input('cargo_dropdown'+POSTFIX, 'value'),
    Input('year_dropdown'+POSTFIX, 'value'),
)
def filter(message,direction, cargo, year):
    df_part = df
    if direction is not None: df_part = df_part.query('`Направление` == @direction')
    if message is not None: df_part = df_part.query('`Вид сообщения` == @message')
    if cargo is not None: df_part = df_part.query('`Наименование груза ЦО-12` == @cargo')
    if year is not None: df_part = df_part.query('`Год` == @year')

    return draw_table_pl(df_part)


def selectors():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col([
                        html.Label('Вид сообщения'),
                        dcc.Dropdown(
                            id='message_dropdown'+POSTFIX,
                            options = [
                                {'label': str(message), 'value': message}
                                for message in df['Вид сообщения'].unique()
                            ],
                            value= None,
                            placeholder='Фильтр по виду вообщения',
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.Label('Направление'),
                        dcc.Dropdown(
                            id='direction_dropdown' + POSTFIX,
                            options=[
                                {'label': str(message), 'value': message}
                                for message in df['Направление'].unique()
                            ],
                            placeholder='Фильтр по направлению',
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.Label('Груз'),
                        dcc.Dropdown(
                            id='cargo_dropdown'+POSTFIX,
                            options=[
                                {'label': str(cargo), 'value': cargo}
                                for cargo in df[CARGO].unique()
                            ],
                            value=None,
                            placeholder='Фильтр по грузу',
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.Label('Год'),
                        dcc.Dropdown(
                            id='year_dropdown'+POSTFIX,
                            options=[
                                {'label': str(year), 'value': year}
                                for year in df['Год'].unique()
                            ],
                            value=None,
                            placeholder='Фильтр по году',
                        )],
                        width=3
                    ),
                ],
                justify='center',
                align='center',
            ),
        ],
        fluid=True
    )
