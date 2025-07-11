from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from typing import List
from ..report_schema import AnalysisItem

# 카테고리 이름 한글 매핑
CATEGORY_MAP = {
    "CAREER": "경력",
    "COMPETENCY": "역량",
    "SIMULATION": "수행",
    "MOTIVATION": "동기",
    "POTENTIAL": "잠재력",
    "FIT": "조직적합성",
    "CHARACTER": "인성",
    "METHODOLOGY": "방법론"
}

def create_radar_chart(analysis_items: List[AnalysisItem]) -> html.Div:
    """
    세부 분석 항목들을 기반으로 역량 레이더 차트를 생성합니다.
    """
    if not analysis_items:
        return html.Div()

    # '종합 평가' 항목 제외
    items_for_chart = [
        item for item in analysis_items if "종합 평가" not in item.title
    ]
    if not items_for_chart:
        return html.Div()

    df = pd.DataFrame([item.model_dump() for item in items_for_chart])
    
    # 카테고리별 평균 점수 계산
    category_scores = df.groupby('category')['score'].mean().reset_index()

    # 한글 카테고리명 추가
    category_scores['category_kr'] = category_scores['category'].map(CATEGORY_MAP)
    
    # 차트 생성
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=category_scores['score'],
        theta=category_scores['category_kr'],
        fill='toself',
        name='역량 점수',
        hovertemplate='<b>%{theta}</b><br>점수: %{r:.1f}<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=False,
                showticklabels=False,
                ticks=''
            ),
            angularaxis=dict(
                tickfont=dict(size=14, family="Pretendard, sans-serif"),
                color="#333"
            )
        ),
        showlegend=False,
        height=450,
        margin=dict(l=80, r=80, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return html.Div(
        dbc.Card(
            dbc.CardBody([
                html.H4("역량 종합 분석 (레이더 차트)", className="card-title text-center mb-4"),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ])
        ),
        className="radar-chart-container mt-4 mb-4"
    ) 