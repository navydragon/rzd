from dash import html, dash_table
import pandas as pd


def load_share():
    excel_file = 'data/references/load_share.xlsx'
    df = pd.read_excel(excel_file, sheet_name='всего').round(3)
    df2 = pd.read_excel(excel_file, sheet_name='внутр').round(3)
    df3 = pd.read_excel(excel_file, sheet_name='экспорт').round(3)
    res = html.Div([
        html.H3('Всего'),
        make_datatable_from_df(df),
        html.H3('Внутренние перевозки'),
        make_datatable_from_df(df2),
        html.H3('Экспорт'),
        make_datatable_from_df(df3)
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