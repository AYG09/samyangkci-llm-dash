import plotly.graph_objs as go
from dash import dcc

def executive_summary_gauge(score: float, max_score: float = 5.0):
    return dcc.Graph(
        figure=go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "종합 평가 점수", 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, max_score]},
                'bar': {'color': "#005BAC"},
                'steps': [
                    {'range': [0, max_score*0.6], 'color': "#e0e4ea"},
                    {'range': [max_score*0.6, max_score*0.8], 'color': "#b2bec3"},
                    {'range': [max_score*0.8, max_score], 'color': "#81ecec"}
                ],
            },
            number={'suffix': ' / 5.0'}
        )),
        config={"displayModeBar": False},
        style={"height": "220px"}
    )

def executive_risk_bar(risk_score: float, max_score: float = 5.0):
    return dcc.Graph(
        figure=go.Figure(go.Bar(
            x=["경영 리스크"],
            y=[risk_score],
            marker_color="#d63031",
            text=[f"{risk_score} / {max_score}"],
            textposition="auto"
        )).update_layout(
            yaxis=dict(range=[0, max_score]),
            margin=dict(l=30, r=30, t=30, b=30),
            height=180
        ),
        config={"displayModeBar": False}
    )
