import dash
from dash import html
import dash_bootstrap_components as dbc


# отрисовка верхнего меню
def navbar():
    return dbc.NavbarSimple(
        children=registered_pages(),
        brand="Меню",
        brand_href="#",
        color="primary",
        dark=True,
    )


def registered_pages():
    return [dbc.NavItem(dbc.NavLink(page["name"], href=page["path"],
                                    active="exact"))
            for page in dash.page_registry.values()
            ]
