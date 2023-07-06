import dash
from dash import html
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}


def sidebar():
    return html.Div(
        [
            html.H2("Меню", className="display-4"),
            html.Hr(),
            html.P(
                "Моделирование тарифов",
                className="lead"
            ),
            dbc.Nav(
                [
                    dbc.NavLink(page["name"], href=page["path"], active="exact")
                    for page in dash.page_registry.values()
                ],
                vertical=True,
                pills=True,
            ),
        ],
        style=SIDEBAR_STYLE,
    )
