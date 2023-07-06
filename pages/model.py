import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .side_bar import sidebar

# dash.register_page(__name__, name="Модель", path='/model', order=3)

def layout():
    return html.H2('Модель', className="m-4")