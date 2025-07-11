import dash_bootstrap_components as dbc
from dash import html

def MaterialSummaryTable(materials):
    header = [html.Th("자료명"), html.Th("요약"), html.Th("분석포인트"), html.Th("활용항목")]
    rows = [
        html.Tr([
            html.Td(m.get("자료명", "")),
            html.Td(m.get("요약", "")),
            html.Td(m.get("분석포인트", "")),
            html.Td(", ".join(str(x) for x in m.get("활용항목", [])))
        ]) for m in materials
    ]
    return dbc.Table([html.Thead(html.Tr(header)), html.Tbody(rows)], bordered=True, hover=True, responsive=True, className="mb-3")
