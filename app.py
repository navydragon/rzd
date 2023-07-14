from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import dash
# from pages.side_bar import sidebar # функция, импортирующая боковое меню
from pages.nav_bar import navbar # функция, импортирующая верхнее меню
# from pages.helper import load_data
import os

import webbrowser

# df = load_data()

# Установка переменной окружения PYTHONIOENCODING
os.environ['PYTHONIOENCODING'] = 'utf-8'


app = dash.Dash(__name__, use_pages=True,external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1('1'),
    dash.page_container
])

app.layout = html.Div([
    navbar(),
    html.Div(dash.page_container)
])

# app.layout = dbc.Row(
#         [dbc.Col(sidebar(), width=2), dbc.Col(dash.page_container, width=10)]
#     )
debug = True

if debug == False:
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == '__main__':
    app.run_server(debug=debug)

