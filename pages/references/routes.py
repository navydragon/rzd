import dash
from dash import html, dcc, Dash, dash_table, callback
from dash.dependencies import Input, Output
import pandas as pd
import dash_bootstrap_components as dbc

df = pd.read_excel('data/refences/routes.xlsx')


def routes():
    # df = pd.read_excel('data/cargo_base.xlsx')
    res = html.Div([
        html.H3('Маршруты станция-станция', className="p-4"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            style_table={'height': '350px', 'overflowY': 'auto',
                         'width': '99%'},
            page_size=50,
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['ds', 'Вид перевозки']
            ],

        ),
        html.Div([
            html.Button("Скачать Excel", id="btn_routes_xlsx"),
            dcc.Download(id="download-routes-xlsx")]),
    ])
    return res


@callback(
    Output("download-routes-xlsx", "data"),
    Input("btn_routes_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df.to_excel, "download.xlsx",
                               sheet_name="Sheet_name_1")
