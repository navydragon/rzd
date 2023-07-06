from dash import Dash, html, dcc, callback, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd


def scenario():
    scenarios_df = pd.read_excel('data/scenarios.xlsx')
    return html.Div([
        html.H2('Результаты сценария', className="m-4"),
        html.Label('Выберите сценарий'),
        dcc.Dropdown(
            options=[
                {'label': i[1], 'value': i[0]}
                for _, i in scenarios_df.iterrows()
            ],
            id='scenario_select'
        ),
        html.Div(id='results_div')
    ])


@callback(Output('results_div', 'children'),
          Input('scenario_select', 'value'),
          )
def render_content(scenario_id):
    if scenario_id is None: return ''
    df = pd.read_excel('data/results.xlsx')
    filtered_df = df[df['Сценарий'] == scenario_id]

    data = dash_table.DataTable(
        data=filtered_df.to_dict('records'),
        id='work_data',
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        style_table={'height': '300px', 'overflowY': 'auto'},
    )

    op_df = filtered_df[['Вид груза', 'Объем погрузки']]
    op_data = dash_table.DataTable(
        data=op_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in op_df.columns],
        style_table={'height': '450px', 'overflowY': 'auto', 'width':'99%'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Вид груза'},
                'textAlign': 'left'
            }
        ]
    )
    op_pie = px.pie(op_df, values='Объем погрузки', names='Вид груза')

    op_delta_df = filtered_df[['Вид груза', 'Изменение объема']]
    op_delta_data = dash_table.DataTable(
        data=op_delta_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in op_delta_df.columns],
        style_table={'height': '450px', 'overflowY': 'auto', 'width': '99%'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Вид груза'},
                'textAlign': 'left'
            }
        ]
    )
    op_delta_pie =px.bar(op_delta_df, y='Изменение объема', x='Вид груза')

    return [
        # data,
        html.H3('Объем погрузки', className="m-4"),
        html.Div([
            html.Div([op_data], className='col-md-4'),
            html.Div([dcc.Graph(figure=op_pie)], className='col-md-8')
        ], className='row'),
        html.H3('Изменение объемов погрузки', className="m-4"),
        html.Div([
            html.Div([op_delta_data], className='col-md-4'),
            html.Div([dcc.Graph(figure=op_delta_pie)], className='col-md-8')
        ], className='row'),
        html.H3('Грузооборот', className="m-4"),
    ]


def scenario_comparsion():
    df = pd.read_excel('data/results.xlsx')
    scenarios_df = pd.read_excel('data/scenarios.xlsx')
    cargos = df['Вид груза'].unique()
    df = df.merge(scenarios_df, left_on='Сценарий', right_on='scenario_id')
    df_gr = df.groupby(['name'])['Объем погрузки'].sum()
    op_delta_pie = px.bar(df_gr, labels={"value":"Объем погрузки","name":"Сценарий","variable":"Параметр"})
    return html.Div([
        html.H2('Сравнение сценариев', className="m-4"),
        html.H3('Объем погрузки', className="m-4"),
        html.Label('Выберите грузы'),
        dcc.Dropdown(
            cargos,
            ['Уголь'],
            multi=True,
            id='cargo_select'
        ),
        html.Div([], className='col-md-8'),
        html.Div(id='div-11')
        # html.Pre(df_gr.columns)
    ])

@callback(
    Output('div-11', 'children'),
    Input('cargo_select', 'value')
)
def update_cargo_graph(value):
    df = pd.read_excel('data/results.xlsx')
    scenarios_df = pd.read_excel('data/scenarios.xlsx')
    df = df.merge(scenarios_df, left_on='Сценарий', right_on='scenario_id')
    df = df[df['Вид груза'].isin(value)]
    df_gr = df.groupby(['name','Вид груза'],as_index=False)['Объем погрузки'].sum()
    op_delta_pie = px.bar(df_gr, x="name", y="Объем погрузки", text_auto=True,
                          color="Вид груза",
                          labels={"value": "Объем погрузки", "name": "Сценарий",
                                  "variable": "Параметр"})
    return dcc.Graph(figure=op_delta_pie)