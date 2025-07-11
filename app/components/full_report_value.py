import dash_bootstrap_components as dbc
from dash import html

def KCIValueAlignment(items):
    value_items = [i for i in items if i.get('index') in [5, 14, 15]]
    return dbc.Card([
        dbc.CardHeader("삼양KCI 가치체계/문화기여"),
        dbc.CardBody([
            html.Ul([html.Li([
                html.B(i.get('title', '')), ": ",
                i.get('analysis', '')
            ]) for i in value_items])
        ])
    ], color="info", outline=True, className="mb-3")
