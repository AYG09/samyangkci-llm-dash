import plotly.graph_objs as go
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import List
from ..report_schema import ComprehensiveReport, AnalysisItem

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

def create_executive_summary_charts(report: ComprehensiveReport, items: List[AnalysisItem]) -> dbc.Card:
    """
    경영진 보고서용 종합 점수 및 핵심 역량 차트를 생성합니다.
    """
    
    # 1. 종합 점수 Indicator 차트 생성
    score_indicator = go.Figure(go.Indicator(
        mode="gauge+number",
        value=report.score,
        title={'text': "종합 평점"},
        gauge={'axis': {'range': [0, 5]}}
    ))
    score_indicator.update_layout(height=250, margin=dict(l=30, r=30, t=50, b=30))

    # 2. 핵심 역량 막대 차트 데이터 준비 (상위 4개)
    top_items = sorted(items, key=lambda x: x.score, reverse=True)[:4]
    
    competency_fig = go.Figure(go.Bar(
        y=[item.title for item in top_items],
        x=[item.score for item in top_items],
        orientation='h'
    ))
    competency_fig.update_layout(
        title="핵심 역량 Top 4",
        xaxis_title="점수",
        height=300,
        margin=dict(l=150, r=30, t=50, b=50)
    )

    return dbc.Card(
        dbc.CardBody([
            dcc.Graph(figure=score_indicator),
            html.Hr(),
            dcc.Graph(figure=competency_fig),
        ]),
        className="executive-charts-card",
    )
