import dash
from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output
from pages.results.results_test import scenario, scenario_comparsion

# dash.register_page(__name__, name="Результаты", path='/results', order=5)


def layout():
    return html.Div([
        html.H2('Результаты', className="m-4"),
        dcc.Tabs(id="tabs-results", value='scenario',
                 children=[
                     dcc.Tab(label='По сценариям', value='scenario'),
                     dcc.Tab(label='Сравнение сценариев',
                             value='scenario_comparsion'),
                 ]),
        html.Div(id='tabs-results-content')
    ])


@callback(Output('tabs-results-content', 'children'),
          Input('tabs-results', 'value'))
def render_content(tab):
    if tab == 'scenario':
        return scenario()
    elif tab == 'scenario_comparsion':
        return scenario_comparsion()
