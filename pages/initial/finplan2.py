from dash import html, dcc, Dash, dash_table, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc


def get_variants():
    return [
        {'label': 'Фин.план. (базовый)', 'value': 'fin_plan'},
        {'label': 'Фин.план. (измененный)', 'value': 'fin_plan_izm'}
    ]


def get_data():
    df = pd.read_csv('data/initial/fin_plan_types.csv').astype('str')
    # df = pd.read_csv('data/initial/fin_plan_types.csv', delimiter=';',decimal=',').astype('str')
    df = df.query('`Год` != "2019"')
    # индекс перевезено
    df.drop('Индекс перевезено', axis=1, inplace=True, errors='ignore')
    excel_file = 'data/references/load_share.xlsx'
    ls_df = pd.read_excel(excel_file, sheet_name='table')
    ls_df['Год'] = ls_df['Год'].astype(str)
    df = df.merge(
        ls_df,
        left_on=['Груз', 'Год', 'Вид сообщения','Направление'],
        right_on=['Груз', 'Год', 'Вид сообщения','Направление'],
        how='left'
    )
    df[PL] = pd.to_numeric(df[PL])
    df[P] = pd.to_numeric(df[P], errors='coerce')
    return df


def finplan2_layout():
    global df
    df = get_data()
    return html.Div([
        html.H3('Погрузка и грузооборот по финансовому плану'),
        selectors(),
        html.Div([], id='datatable_div', className='m-2'),
    ], className='m-2')


# названия столбцов
P = 'Погрузка, млн. т'
P_BASE = 'Погрузка базовая, млн. т'
PL = 'Грузооборот, млрд. ткм'
PL_BASE = 'Грузооборот базовый, млрд. ткм'
PL_INDEX = 'Индекс грузооборота'
IPER = 'Индекс перевезено'
HAS_P = ['общий уровень','внутрироссийское','экспорт']


def draw_table_p(df_part):
    # print (df_part)
    columns_to_display = ['Груз', 'Год', 'Вид сообщения', P, PL]
    table = dash_table.DataTable(
        id='datatable_p',
        data=df_part.to_dict('records'),
        columns=[
            {'name': col, 'id': col, 'editable': (col == P)}
            for col in columns_to_display
        ],
        sort_action='native',
        page_size=11,
        style_cell_conditional=[
            {'if': {'column_id': 'Груз'}, 'textAlign': 'left'},
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


def draw_table_pl(df_part):
    # print (df_part)
    columns_to_display = ['Груз', 'Год', 'Вид сообщения', P, PL]
    table = dash_table.DataTable(
        id='datatable_pl',
        data=df_part.to_dict('records'),
        columns=[
            {'name': col, 'id': col, 'editable': (col == PL)}
            for col in columns_to_display
        ],
        sort_action='native',
        page_size=11,
        style_cell_conditional=[
            {'if': {'column_id': 'Груз'}, 'textAlign': 'left'},
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
    Output('datatable_p', 'data'),
    Input('datatable_p', 'data'),
    State('datatable_p', 'data_previous'),
    State('datatable_p', 'start_cell'),
    State('datatable_p', 'page_current'),
    State('datatable_p', 'page_size'),
    prevent_initial_call=True
)
def calculate_and_save_p(data, data_previous,start_cell,page_current,page_size):
    global df
    if page_current is None : page_current = 0
    changed_index = int(start_cell['row']) + int(page_current) * int(page_size) - 1
    updated_row = data[changed_index]
    print (updated_row)
    row_index = updated_row['row_index']
    updated_df = pd.DataFrame.from_records(data)
    cols_to_numeric = [PL, P, PL_BASE, P_BASE,'Грузооборот 2019']
    updated_df[cols_to_numeric] = updated_df[cols_to_numeric].apply(pd.to_numeric, errors='coerce')

    # формула расчета PL
    pl_0 = updated_df.loc[changed_index, PL_BASE]
    p_1 = updated_df.loc[changed_index, P]
    p_0 = updated_df.loc[changed_index, P_BASE]
    ind = updated_df.loc[changed_index, 'Индекс перевезено']
    updated_df.loc[changed_index, PL] = pl_0 * (1 + (p_1 - p_0) / p_0 * ind)
    # формула расчета индекса
    updated_df.loc[changed_index, PL_INDEX] = updated_df.loc[changed_index, PL] / updated_df.loc[changed_index, 'Грузооборот 2019']
    # заполняем исходный df
    df.loc[df['row_index'] == row_index, [P,PL,PL_INDEX]] = [updated_df.loc[changed_index, P],updated_df.loc[changed_index, PL],updated_df.loc[changed_index, PL_INDEX]]
    df.to_csv('data/initial/fin_plan_types.csv', index=False)
    return updated_df.to_dict('records')


@callback(
    Output('datatable_pl', 'data'),
    Input('datatable_pl', 'data'),
    State('datatable_pl', 'data_previous'),
    State('datatable_pl', 'start_cell'),
    State('datatable_pl', 'page_current'),
    State('datatable_pl', 'page_size'),
    prevent_initial_call=True
)
def calculate_and_save_pl(data, data_previous,start_cell,page_current,page_size):
    global df
    if page_current is None : page_current = 0
    changed_index = int(start_cell['row']) + int(page_current) * int(page_size) - 1
    updated_row = data[changed_index]
    print (updated_row)
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
    Output('datatable_div', 'children'),
    Input('message_dropdown', 'value'),
    Input('cargo_dropdown', 'value'),
    Input('year_dropdown', 'value'),
)
def filter(message, cargo, year):
    df_part = df.query('`Вид сообщения` == @message')
    if cargo is not None: df_part = df_part.query('`Груз` == @cargo')
    if year is not None: df_part = df_part.query('`Год` == @year')

    if message in HAS_P:
        return draw_table_p(df_part)
    return draw_table_pl(df_part)


def selectors():
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col([
                        html.Label('Вид сообщения'),
                        dcc.Dropdown(
                            id='message_dropdown',
                            options = [
                                {'label': str(message), 'value': message}
                                for message in df['Вид сообщения'].unique()
                            ],
                            value='общий уровень',
                            placeholder='Фильтр по виду вообщения',
                        )],
                        width=4
                    ),
                    dbc.Col([
                        html.Label('Груз'),
                        dcc.Dropdown(
                            id='cargo_dropdown',
                            options=[
                                {'label': str(cargo), 'value': cargo}
                                for cargo in df['Груз'].unique()
                            ],
                            value=None,
                            placeholder='Фильтр по грузу',
                        )],
                        width=4
                    ),
                    dbc.Col([
                        html.Label('Год'),
                        dcc.Dropdown(
                            id='year_dropdown',
                            options=[
                                {'label': str(year), 'value': year}
                                for year in df['Год'].unique()
                            ],
                            value=None,
                            placeholder='Фильтр по году',
                        )],
                        width=4
                    ),
                ],
                justify='center',
                align='center',
            ),
        ],
        fluid=True
    )
