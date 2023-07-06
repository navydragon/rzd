from dash import html, dash_table
import pandas as pd


def costs():
    excel_file = 'data/references/costs.xlsx'
    df = pd.read_excel(excel_file).round(3)
    res = html.Div([
        html.H3('Параметры'),
        make_datatable_from_df(df),
    ], className="p-2")
    return res


def make_datatable_from_df(df):
    return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": str(i), "id": str(i)} for i in df.columns],
            style_table={'height': '350px', 'overflowY': 'auto', 'width': '99%'},
            page_size=50,
            style_cell_conditional=[
                {'if': {'column_id': c}, 'textAlign': 'left'} for c in ['Вид груза']
            ],
        )