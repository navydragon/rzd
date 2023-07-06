import dash
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output
# from pages.initial.finplan1 import finplan1_layout
from pages.initial.finplan2 import finplan2_layout
from pages.initial.finplan05 import finplan05_layout
from pages.initial.invest import invest_layout
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Исходные данные", path='/initial', order=4)

app = Dash()


def layout():
    return html.Div([
        html.H2('Исходные данные', className="m-4"),
        dcc.Tabs(id="tabs-example-graph", value='finplan_05',
                 children=[
                     dcc.Tab(label='Фин. план (версия май)', value='finplan_05'),
                     dcc.Tab(label='Фин. план (версия апрель)', value='finplan'),
                     dcc.Tab(label='Инвест. проекты', value='invest')
                 ]),
        html.Div(id='tabs-content-example-graph')
    ])


@callback(Output('tabs-content-example-graph', 'children'),
          Input('tabs-example-graph', 'value'))
def render_content(tab):
    if tab == 'finplan':
        return html.Div([finplan2_layout()])
    elif tab == 'invest':
        return html.Div([invest_layout()])
    if tab == 'finplan_05':
        return html.Div([finplan05_layout()])

