from dash import html, dcc, Dash, dash_table, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.dash_table.Format import Format, Scheme
import dash_bootstrap_components as dbc
import sqlite3


# def get_variants():
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM cargo_variants WHERE variant = "Фин.план"')
#     results = cursor.fetchall()
#     options = [{'label': row[2], 'value': row[0]} for row in results]
#     conn.close()
#     return options

def get_variants():
    return [
        {'label': 'Фин.план. (базовый)', 'value': 'fin_plan'},
        {'label': 'Фин.план. (измененный)', 'value': 'fin_plan_izm'}
    ]


def get_data():
    LIST_NAMES = ['Погрузка', 'Грузооборот', 'Средняя дальность']
    raw = pd.read_excel('data/initial/fin_plan.xlsx', sheet_name=None, header=0)
    df = raw.pop(LIST_NAMES[0])
    df['Показатель'] = LIST_NAMES[0]

    n = 0
    for sheet_name, df1 in raw.items():
        df1['Показатель'] = LIST_NAMES[n + 1]
        df = pd.concat([df, df1])
        n += 1
    return df


df = get_data()
# df = pd.read_csv('data/initial/fin_plan/fin_plan.csv',delimiter=';',decimal=",")
selector_value = ''
base_variant = 'fin_plan'
change = 'Грузооборот'


def finplan1_layout():
    return html.Div([
        commands,
        html.Div(id='test_div'),
        draw_datatable('pl_datatable', 'Грузооборот', 'млрд. ткм'),
        draw_datatable('p_datatable', 'Погрузка', 'млн. тонн'),
        draw_datatable('l_datatable', 'Средняя дальность', 'км')
    ], className='mx-2')


# обновляем грузооборот
@callback(
    Output('pl_datatable', 'data'),
    Input('p_datatable', 'data'), Input('update_selector', 'value'),
    State('p_datatable', 'data_previous'),
    prevent_initial_call=True
)
def update_pl(data, update_selector, data_previous):
    global df
    if update_selector == 'Грузооборот' and data != data_previous:
        for i in range(len(data)):
            if data[i] != data_previous[i]:
                for key in data[i]:
                    if data[i][key] != data_previous[i][key]:
                        cargo = data[i]['Наименование груза']
                        year = key
                        new_value = data[i][key]
                        pl_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Грузооборот')
                        l_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Средняя дальность')
                        p_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Погрузка')
                        lenght = df.loc[l_condition, 'Значение']
                        p = new_value
                        new_pl = new_value * int(lenght) / 1000
                        df.loc[p_condition, 'Значение'] = p
                        df.loc[pl_condition, 'Значение'] = new_pl

    p_df = make_pivot_table('Грузооборот')

    return p_df.to_dict('records')


# обновляем погрузку
@callback(
    Output('p_datatable', 'data'),
    Input('pl_datatable', 'data'), Input('update_selector', 'value'),
    State('pl_datatable', 'data_previous'),
    prevent_initial_call=True
)
def update_p(data, update_selector, data_previous):
    global df
    if update_selector == 'Погрузка' and data != data_previous:
        for i in range(len(data)):
            if data[i] != data_previous[i]:
                for key in data[i]:
                    if data[i][key] != data_previous[i][key]:
                        cargo = data[i]['Наименование груза']
                        year = key
                        new_value = data[i][key]
                        p_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Погрузка')
                        l_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Средняя дальность')
                        pl_condition = (df['Наименование груза'] == cargo) & (
                                df['Год'] == int(year)) & (df[
                                                               'Показатель'] == 'Грузооборот')
                        lenght = df.loc[l_condition, 'Значение']
                        pl = new_value
                        new_p = int(new_value) / int(lenght) * 1000
                        df.loc[pl_condition, 'Значение'] = pl
                        df.loc[p_condition, 'Значение'] = new_p

    p_df = make_pivot_table('Погрузка')

    return p_df.to_dict('records')


# editable
@callback(
    [Output('p_datatable', 'editable'),
     Output('pl_datatable', 'editable')],
    # Output('test_div','children'),
    Input('update_selector', 'value'))
def update_editable_cells(value):
    global change
    change = value

    if value == 'Погрузка':
        return True, True
    else:
        return True, False


def make_pivot_table(indicator):
    p_df = df.query('`Показатель` == @indicator')
    p_df = p_df.pivot_table(values='Значение', index='Наименование груза',
                            columns='Год', aggfunc=sum)
    p_df = p_df.reset_index().rename_axis(None, axis=1)
    return p_df


def draw_datatable(table_id, indicator, measure):
    p_df = make_pivot_table(indicator)
    p_columns = [
        {"name": str(i), "id": str(i), "type": "numeric",
         "format": Format(precision=2, scheme=Scheme.fixed)} for i in
        p_df.columns[1:]]
    p_columns = [{"name": "Наименование груза",
                  "id": "Наименование груза"}] + p_columns
    return html.Div([
        html.H3(indicator + ', ' + measure, className='mt-3'),
        dash_table.DataTable(
            id=str(table_id),
            columns=p_columns,
            data=p_df.to_dict('records'),
            editable=indicator != change,
            style_cell={'textAlign': 'left'},
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Наименование груза', },
                    'textAlign': 'left'
                },
            ],
        )
    ])

save_toast = html.Div(
    [
        dbc.Toast(
            "Сохранено!",
            id="save_toast",
            header="Сохранение варианта",
            is_open=False,
            dismissable=True,
            duration=4000,
            icon="success",
            style={"position": "fixed", "top": 0, "right": 10, "width": 350},
        ),
    ]
)

variants_row = html.Div([
    # html.Div([
    #     html.H6(children='Вариант данных:'),
    #     dcc.Dropdown(get_variants(), base_variant,
    #                  id='variants_selector'),
    # ], className='col-4'),
    html.Div([
        html.H6(children='Сохранение изменений'),
        # dbc.Button("Сохранить как новый", id="save_new_open", n_clicks=0, className='btn btn-info'),
        dbc.Button("Сохранить", id="save_current_btn", n_clicks=0, color='primary'),
        save_toast
    ], className='col-4'),
    # dbc.Modal(
    #     [
    #         dbc.ModalHeader(dbc.ModalTitle("Сохранить как новый вариант")),
    #         dbc.ModalBody([
    #             dbc.Input(id="file_name_input",
    #                       placeholder="Введите название варианта...",
    #                       type="text"),
    #             html.Div([], id='modal_output')
    #         ]),
    #         dbc.ModalFooter([
    #             dbc.Button(
    #                 "Сохранить вариант", id="save_new_save", n_clicks=0),
    #             dbc.Button(
    #                 "Закрыть", id="close", className="ms-auto", n_clicks=0
    #             )]
    #         ),
    #     ],
    #     id="save_new_modal",
    #     is_open=False,
    # ),
], className='row mt-4', id='row1_div')
commands = html.Div([
    variants_row,
    html.Div([
        html.H6(children='Обновлять:'),
        dcc.Dropdown(['Грузооборот', 'Погрузка'], 'Грузооборот',
                     id='update_selector'),
    ], className='col-4'),
], className='row mt-4', id='row1_div')




@callback(
    Output("save_new_modal", "is_open"),
    Input("save_new_open", "n_clicks"),
    Input("close", "n_clicks"),
    Input("save_new_save", "n_clicks"),
    State("save_new_modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open


# @callback(
#     Output("variants_selector", "options"),
#     Output('variants_selector', 'value'),
#     Input("save_new_save", "n_clicks"),
#     State("file_name_input", "value"),
#     State("variants_selector", "options"),
#     prevent_initial_call=True
# )
# def save_new_variant(n1, name, variants):
#     global base_variant
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("SELECT MAX(id) FROM cargo_variants")
#     max_id = int(c.fetchone()[0])
#     new_id = max_id + 1
#     new_path = 'data/initial/fin_plan/' + str(new_id) + '.xlsx'
#     c.execute(
#         "INSERT INTO cargo_variants (variant, name, path, description) VALUES ('Фин.план', ?, ?, '...')",
#         (name, new_path)
#     )
#     conn.commit()
#     c.execute("SELECT last_insert_rowid()")
#     last_id = c.fetchone()[0]
#     # сохраняем df
#     df.to_excel(new_path, sheet_name='Фин_план_' + str(last_id), index=False)
#     conn.close()
#
#     base_variant = int(last_id)
#     variants.append({'label': name, 'value': last_id})
#     return variants, last_id

# @callback(
#     Output('p_datatable', 'data'),
#     Input("variants_selector","value"),
#     prevent_initial_call=True
# )
# def choose_variant(variant):
#     global df
#     df = pd.read_excel('data/initial/fin_plan/fin_plan_izm.xlsx')
#     p_df = make_pivot_table('Погрузка')
#
#     return p_df.to_dict('records')



@callback(
    Output("save_toast", "is_open"),
    Input("save_current_btn", "n_clicks"),
    prevent_initial_call=True
)
def save_current(n):
    global df
    df.to_excel('data/initial/fin_plan/fin_plan_izm.xlsx', index=False)
    #df.to_csv('data/initial/fin_plan/fin_plan_izm.csv',encoding='utf-8', decimal=",", index=False)
    return True
