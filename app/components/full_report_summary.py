from dash import html, dcc
import dash_bootstrap_components as dbc  # type: ignore
import plotly.graph_objects as go
from app.report_schema import ComprehensiveReport


def create_comprehensive_score_donut(score: float) -> dcc.Graph:
    """종합 점수 도넛 차트를 생성합니다."""
    # 점수에 따른 색상 결정
    if score >= 80:
        color = '#28a745'  # 초록색
    elif score >= 60:
        color = '#ffc107'  # 노란색  
    else:
        color = '#dc3545'  # 빨간색
    
    fig = go.Figure(data=[go.Pie(
        labels=['점수', ''],
        values=[score, 100-score],
        hole=0.6,
        marker=dict(colors=[color, '#e9ecef']),
        textinfo='none',
        hoverinfo='none',
        showlegend=False
    )])
    
    fig.add_annotation(
        text=f"{score:.0f}",
        x=0.5, y=0.5,
        font_size=36,
        showarrow=False
    )
    
    fig.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_full_report_summary(report: ComprehensiveReport) -> html.Div:
    """
    '종합 평가 및 핵심 요약' 섹션을 생성합니다.
    (Executive Summary 텍스트 + 종합 평가 점수 도넛 차트)
    """

    # Executive Summary 텍스트 부분
    summary_content = html.Div([
        html.H4("Executive Summary", className="summary-title"),
        html.P(report.summary, className="summary-paragraph"),
    ])

    # 종합 평가 점수 차트
    donut_chart = create_comprehensive_score_donut(report.score)

    return html.Div(
        [
            html.H2("I. 종합 평가 및 핵심 요약", className="report-main-section-title"),
            dbc.Row(
                [
                    dbc.Col(summary_content, md=7),
                    dbc.Col(donut_chart, md=5),
                ],
                align="center",
                className="g-0",
            ),
        ],
        className="report-section-container",
    )
