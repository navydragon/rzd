import dash
from dash import html, dcc,callback, Input, Output, State
from pages.references.load_share import load_share
from pages.references.costs import costs
import dash_bootstrap_components as dbc

dash.register_page(__name__, name="Справочники", path='/references', order=4)


def layout():
    return html.Div([
        html.H2('Справочники', className="m-4"),
        dcc.Tabs(id="tabs-references", value='costs',
                 children=[
                     dcc.Tab(label='Темп роста себестоимости', value='costs'),
                     dcc.Tab(label='Коэффициент погрузки', value='loading_share'),
                     dcc.Tab(label='...', value='tab-3-example-graph'),
                 ]),
        html.Div(id='tabs-references-content')
    ])

@callback(Output('tabs-references-content', 'children'),
          Input('tabs-references', 'value'))
def render_content(tab):
    if tab == 'costs':
        return costs()
    elif tab == 'loading_share':
        return load_share()