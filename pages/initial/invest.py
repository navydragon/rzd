from dash import html, dcc, Dash, dash_table, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc


DIRECTIONS = ['Все','Сеть', 'Восток', 'Северо-Запад','Юг']
SUM_COL = 'Сумма расходов на проекты, млрд руб'

def get_data():
    df = pd.read_excel('data/initial/invest.xlsx')
    df['Index'] = df.index
    # df[SUM_COL] = df[SUM_COL].round(0)
    return df


def invest_layout():
    global df
    df = get_data()
    return html.Div([
        html.H3('Инвестиционные проекты'),
        html.Div([],id='output_div'),
        html.Div([draw_table(df)], id='invest_datatable_div', className='m-2'),
    ], className='m-2')




def draw_table(df_part):
    columns_to_display = ['Направление', 'Наименование проектов', SUM_COL, 'Участие в расчете']
    table = dash_table.DataTable(
        id='datatable_invest',
        data=df_part.to_dict('records'),
        columns=[
            {'id': 'Index', 'name': 'Index'},
            {'id': 'Направление', 'name': 'Направление'},
            {'id': 'Наименование проектов', 'name': 'Наименование проектов'},
            {'id': SUM_COL, 'name': SUM_COL, 'type':'numeric'},
            {'id': 'Участие в расчете', 'name': 'Участие в расчете'},
        ],
        dropdown={
            'Участие в расчете': {
                'options': [{'label': 'Да', 'value': 'Да'}, {'label': 'Нет', 'value': 'Нет'}]
            }
        },
        sort_action='native',
        page_size=20,
        row_selectable='multi',
        selected_rows=df_part[df_part['Участие в расчете'] == 'Да'].index,
        style_cell_conditional=[
            {'if': {'column_id': 'Направление'}, 'textAlign': 'left'},
            {'if': {'column_id': 'Наименование проектов'}, 'textAlign': 'left'},
            {'if': {'column_id': 'Index'}, 'display': 'none'},
            {'if': {'column_id': 'Участие в расчете'}, 'display': 'none'},
        ],
        style_data_conditional=[
            {'if': {'column_editable': False}, 'backgroundColor': 'lightgray'},
        ],
        style_header={'fontWeight': 'bold'},
        editable=True,

    )
    return table


@callback(
    Output('output_div', 'children'),
    Input('datatable_invest', 'selected_rows'),
    State('datatable_invest', 'data'),
    prevent_initial_call=True
)
def update_selected_rows(selected_rows,data):
    global df
    for index, elem in enumerate(data):
        if index in selected_rows:
            df.loc[elem['Index'], 'Участие в расчете'] = 'Да'
        else:
            df.loc[elem['Index'], 'Участие в расчете'] = 'Нет'

    df.to_excel('data/initial/invest.xlsx', index=False)
    pass

@callback(
    Output('datatable_invest', 'data'),
    Input('datatable_invest', 'data'),
    State('datatable_invest', 'data_previous'),
    State('datatable_invest', 'start_cell'),
    State('datatable_invest', 'page_current'),
    State('datatable_invest', 'page_size'),
    prevent_initial_call=True
)
def save_row(data, data_previous,start_cell,page_current,page_size):
    global df
    if page_current is None : page_current = 0
    changed_index = int(start_cell['row']) + int(page_current) * int(page_size) - 1
    updated_row = data[changed_index]
    row_index = updated_row['Index']
    df = pd.DataFrame.from_records(data)
    df.to_excel('data/initial/invest.xlsx', index=False)
    return data

# @callback(
#     Output('datatable_p', 'data'),
#     Input('datatable_p', 'data'),
#     State('datatable_p', 'data_previous'),
#     State('datatable_p', 'start_cell'),
#     State('datatable_p', 'page_current'),
#     State('datatable_p', 'page_size'),
#     prevent_initial_call=True
# )
# def calculate_and_save(data, data_previous, start_cell, page_current,
#                        page_size):
#     global df
#     if page_current is None: page_current = 0
#     changed_index = int(start_cell['row']) + int(page_current) * int(
#         page_size) - 1
#     updated_row = data[changed_index]
#     print(updated_row)
#     row_index = updated_row['row_index']
#     updated_df = pd.DataFrame.from_records(data)
#     cols_to_numeric = [PL, P, PL_BASE, P_BASE, 'Грузооборот 2019']
#     updated_df[cols_to_numeric] = updated_df[cols_to_numeric].apply(
#         pd.to_numeric, errors='coerce')
#
#     # формула расчета PL
#     pl_0 = updated_df.loc[changed_index, PL_BASE]
#     p_1 = updated_df.loc[changed_index, P]
#     p_0 = updated_df.loc[changed_index, P_BASE]
#     ind = updated_df.loc[changed_index, 'Индекс перевезено']
#     updated_df.loc[changed_index, PL] = pl_0 * (1 + (p_1 - p_0) / p_0 * ind)
#     # формула расчета индекса
#     updated_df.loc[changed_index, PL_INDEX] = updated_df.loc[
#                                                   changed_index, PL] / \
#                                               updated_df.loc[
#                                                   changed_index, 'Грузооборот 2019']
#     # заполняем исходный df
#     df.loc[df['row_index'] == row_index, [P, PL, PL_INDEX]] = [
#         updated_df.loc[changed_index, P], updated_df.loc[changed_index, PL],
#         updated_df.loc[changed_index, PL_INDEX]]
#     df.to_csv('data/initial/fin_plan_types.csv', index=False)
#     return updated_df.to_dict('records')


@callback(
    Output('invest_datatable_div', 'children'),
    Input('direction_dropdown', 'value'),
)
def filter(direction):

    if direction is not None and direction != 'Все':
        df_part = df.query('`Направление` == @direction')
    else:
        df_part = df

    return draw_table(df_part)


def selectors():
    return dbc.Container(
    [
        html.Div(
        [
            html.Label('Вид сообщения'),
            dcc.Dropdown(
                id='direction_dropdown',
                options=[
                    {'label': str(direction), 'value': direction}
                    for direction in DIRECTIONS
                ],
                value='Все',
                placeholder='Фильтр по направлению',
            )
        ],className='col-md-3'),
    ],className='mx-2')
