from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import List
from ..report_schema import ComprehensiveReport, AnalysisItem
from collections import defaultdict

def create_full_report_summary(report: ComprehensiveReport, items: List[AnalysisItem]) -> html.Div:
    """
    종합 분석 및 레이더 차트 섹션을 생성합니다.
    """
    
    # 1. 레이더 차트 데이터 계산
    category_scores = defaultdict(list)
    for item in items:
        category_scores[item.category].append(item.score)
    
    avg_scores = {
        cat: round(sum(scores) / len(scores), 2) if scores else 0
        for cat, scores in category_scores.items()
    }
    
    # 카테고리 순서 정의 (원하는 순서대로)
    categories = ['EXPERTISE', 'CAREER', 'COMMUNICATION', 'PERSONALITY']
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[avg_scores.get(cat, 0) for cat in categories],
        theta=categories,
        fill='toself',
        name='역량'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5]),
            angularaxis=dict(tickfont=dict(size=14))
        ),
        showlegend=False,
        height=400,
        margin=dict(l=60, r=60, t=40, b=40)
    )

    # 2. 종합 평가 텍스트 컴포넌트 생성
    summary_text_component = html.Div([
        dbc.Badge(report.recommendation, color="primary", className="me-2"),
        html.H4("종합 평가", className="d-inline"),
        html.P(report.summary, className="mt-3"),
        html.Hr(),
        html.H5(f"종합 평점: {report.score} / 5.0", className="text-end")
    ])

    return html.Div(
        dbc.Row([
            dbc.Col(summary_text_component, md=6),
            dbc.Col(dcc.Graph(figure=fig), md=6),
        ]),
        className="report-summary-section p-4 mb-4",
    )
