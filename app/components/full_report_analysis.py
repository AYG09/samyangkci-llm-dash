import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objs as go

def AnalysisItemCard(item):
    value_badge = None
    if item.get('index') in [5, 14, 15]:
        value_badge = dbc.Badge("KCI 가치체계", color="info", className="ms-2")
    return dbc.Card([
        dbc.CardHeader([
            f"{item.get('index', '')}. {item.get('title', '')}",
            value_badge if value_badge else ""
        ]),
        dbc.CardBody([
            html.P(f"점수: {item.get('score', 'N/A')} / 신뢰도: {item.get('reliability', 'N/A')}"),
            dcc.Markdown(item.get('analysis', '')),
            html.Small(f"자료근거: {item.get('evidence', '')}")
        ])
    ], className="mb-3")

def AnalysisRadarChart(items):
    labels = [item.get('title', '') for item in items]
    scores = [item.get('score', 0) for item in items]
    reliabilities = [item.get('reliability', 0) for item in items]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=scores, theta=labels, fill='toself', name='점수'))
    fig.add_trace(go.Scatterpolar(r=reliabilities, theta=labels, fill='toself', name='신뢰도'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True, height=400)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

def AnalysisBarChart(items):
    labels = [f"{item.get('index', '')}.{item.get('title', '')}" for item in items]
    scores = [item.get('score', 0) for item in items]
    fig = go.Figure([go.Bar(x=labels, y=scores, marker_color='indigo')])
    fig.update_layout(title="항목별 점수", yaxis=dict(range=[0, 5]), height=300)
    return dcc.Graph(figure=fig, config={'displayModeBar': False})
