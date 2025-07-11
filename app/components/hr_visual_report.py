"""HR 담당자용 인터랙티브 비주얼 리포트 컴포넌트"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from typing import List, Any, Dict

from ..report_schema import ReportData


# 카테고리별 색상 맵
CATEGORY_COLOR_MAP = {
    'CAREER': '#1f77b4',
    'COMPETENCY': '#ff7f0e',
    'SIMULATION': '#2ca02c',
    'MOTIVATION': '#d62728',
    'POTENTIAL': '#9467bd',
    'FIT': '#8c564b'
}

# 추천 등급별 스타일 맵
RECOMMENDATION_STYLE_MAP = {
    '강력 추천': {'color': 'success', 'icon': 'bi bi-hand-thumbs-up'},
    '추천': {'color': 'primary', 'icon': 'bi bi-check-circle'},
    '고려': {'color': 'warning', 'icon': 'bi bi-search'},
    '보류': {'color': 'secondary', 'icon': 'bi bi-pause-circle'},
    '비추천': {'color': 'danger', 'icon': 'bi bi-hand-thumbs-down'}
}


def create_candidate_info_card(report_data: ReportData) -> dbc.Card:
    """후보자 기본 정보 카드를 생성합니다."""
    info = report_data.candidate_info
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-person-badge me-2"),
            html.H4(f"{info.name} ({info.position})", className="m-0 d-inline")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.I(className="bi bi-building me-2 text-primary"),
                        html.Strong("지원 조직: "),
                        info.organization
                    ], className="mb-2"),
                    html.P([
                        html.I(className="bi bi-calendar-event me-2 text-success"),
                        html.Strong("면접 일자: "),
                        info.interview_date
                    ], className="mb-2")
                ], width=12, md=6),
                dbc.Col([
                    html.P([
                        html.I(className="bi bi-briefcase me-2 text-info"),
                        html.Strong("경력 요약: "),
                        info.career_summary
                    ], className="mb-2"),
                    html.P([
                        html.I(className="bi bi-currency-dollar me-2 text-warning"),
                        html.Strong("연봉 정보: "),
                        info.salary_info
                    ], className="mb-2")
                ], width=12, md=6)
            ])
        ])
    ], className="mb-4")


def create_recommendation_gauge(report_data: ReportData) -> dbc.Card:
    """추천 등급 게이지 카드를 생성합니다."""
    if not report_data.comprehensive_report:
        return dbc.Card(
            dbc.CardBody("종합 평가 데이터가 없습니다."),
            className="h-100"
        )
    
    recommendation = report_data.comprehensive_report.recommendation
    score = report_data.comprehensive_report.score
    
    style = RECOMMENDATION_STYLE_MAP.get(
        recommendation, 
        {'color': 'light', 'icon': 'bi bi-question-circle'}
    )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className=f"{style['icon']} me-2"),
            html.Span(f"채용추천", className="fw-bold")
        ], className=f"bg-{style['color']} text-white text-center py-2"),
        dbc.CardBody([
            html.Div([
                html.H4(recommendation, className=f"text-{style['color']} mb-2 fw-bold"),
                html.Hr(className="my-2"),
                html.H2(f"{score:.1f}", className=f"text-{style['color']} mb-1"),
                html.P("/ 100점", className="text-muted mb-0")
            ], className="text-center")
        ])
    ], className="h-100")


def create_competency_radar_chart(analysis_items: List[Any]) -> go.Figure:
    """6개 역량 그룹별 레이더 차트를 생성합니다."""
    if not analysis_items:
        return go.Figure()
    
    # 데이터 준비 - 카테고리별 평균 점수 계산
    df = pd.DataFrame([{
        'category': item.category,
        'score': item.score
    } for item in analysis_items])
    
    category_scores = df.groupby('category')['score'].mean().reset_index()
    
    # 카테고리 이름 한글화
    category_names = {
        'CAREER': '경력/전문성',
        'COMPETENCY': '핵심역량',
        'SIMULATION': '직무테스트',
        'MOTIVATION': '동기/성격',
        'POTENTIAL': '성장잠재력',
        'FIT': '조직적합성'
    }
    
    category_scores['category_kr'] = category_scores['category'].map(
        lambda x: category_names.get(x, x)
    )
    
    # 레이더 차트 생성
    fig = go.Figure()
    
    # 카테고리별 색상 적용
    category_colors = [CATEGORY_COLOR_MAP.get(cat, '#cccccc') for cat in category_scores['category']]
    
    fig.add_trace(go.Scatterpolar(
        r=category_scores['score'],
        theta=category_scores['category_kr'],
        fill='toself',
        name='역량 점수',
        line=dict(color='rgba(0, 85, 164, 0.8)', width=2),
        fillcolor='rgba(0, 85, 164, 0.1)',
        marker=dict(
            size=12, 
            color=category_colors,
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{theta}</b><br>점수: %{r:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showline=False,
                showticklabels=True,
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20', '40', '60', '80', '100'],
                ticks='',
                gridcolor='rgba(0,0,0,0.1)',
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                direction="clockwise",
                tickfont=dict(size=12, color='#333'),
                rotation=90
            )
        ),
        showlegend=False,
        title='6대 역량 그룹별 분석',
        height=450,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Pretendard, sans-serif")
    )
    
    return fig


def create_insights_accordion(executive_insights: List[Any], hr_points: List[Any]) -> dbc.Accordion:
    """Executive & HR Insights 아코디언을 생성합니다."""
    accordion_items = []
    
    # Executive insights 추가
    for i, item in enumerate(executive_insights):
        accordion_items.append(
            dbc.AccordionItem([
                html.Div([
                    html.P(item.analysis, className="mb-3"),
                    html.Hr(),
                    html.Small([
                        html.I(className="bi bi-clipboard-data me-2"),
                        html.Strong("근거: "),
                        item.evidence
                    ], className="text-muted")
                ])
            ], title=f"💡 {item.title}")
        )
    
    # HR points 추가
    for i, item in enumerate(hr_points):
        accordion_items.append(
            dbc.AccordionItem([
                html.Div([
                    html.P(item.analysis, className="mb-3"),
                    html.Hr(),
                    html.Small([
                        html.I(className="bi bi-clipboard-data me-2"),
                        html.Strong("근거: "),
                        item.evidence
                    ], className="text-muted")
                ])
            ], title=f"⚙️ {item.title}")
        )
    
    return dbc.Accordion(
        accordion_items,
        start_collapsed=True,
        always_open=False
    )


def create_material_analysis_accordion(material_analysis: List[Any]) -> dbc.Accordion:
    """자료별 분석 아코디언을 생성합니다."""
    accordion_items = []
    
    for item in material_analysis:
        accordion_items.append(
            dbc.AccordionItem([
                html.Div([
                    html.H6([
                        html.I(className="bi bi-file-text me-2"),
                        "핵심 내용 요약"
                    ], className="mt-2 mb-3"),
                    html.P(item.summary, className="mb-3"),
                    html.H6([
                        html.I(className="bi bi-lightbulb me-2"),
                        "주요 분석 포인트"
                    ], className="mb-3"),
                    html.P(item.analysis_points, className="mb-0")
                ])
            ], title=f"📄 {item.material_name}")
        )
    
    return dbc.Accordion(
        accordion_items,
        start_collapsed=True,
        always_open=True,
        flush=True
    )


def create_category_legend() -> dbc.Card:
    """카테고리 범례 카드를 생성합니다."""
    category_names = {
        'CAREER': '경력/전문성',
        'COMPETENCY': '핵심역량',
        'SIMULATION': '직무테스트',
        'MOTIVATION': '동기/성격',
        'POTENTIAL': '성장잠재력',
        'FIT': '조직적합성'
    }
    
    legend_items = []
    for category, color in CATEGORY_COLOR_MAP.items():
        legend_items.append(
            html.Div([
                html.Div(
                    style={
                        'width': '20px',
                        'height': '20px',
                        'backgroundColor': color,
                        'borderRadius': '3px',
                        'display': 'inline-block',
                        'marginRight': '8px'
                    }
                ),
                html.Span(category_names.get(category, category))
            ], className="d-flex align-items-center mb-2")
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-palette me-2"),
            html.H6("역량 카테고리", className="m-0 d-inline")
        ]),
        dbc.CardBody(legend_items)
    ])


def render_hr_visual_report(report_data: ReportData) -> html.Div:
    """HR 담당자용 비주얼 리포트를 렌더링합니다."""
    return html.Div([
        # 헤더
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-people me-2"),
                        "HR Visual Report"
                    ], className="text-white mb-1"),
                    html.P("HR 전문가를 위한 상세 역량 분석 보고서", className="text-white-50 mb-0")
                ], className="p-4")
            ], width=12, style={'backgroundColor': '#0055A4'})
        ], className="mb-4"),
        
        # 후보자 기본 정보
        dbc.Row([
            dbc.Col([
                create_candidate_info_card(report_data)
            ], width=12)
        ]),
        
        # 메인 대시보드 영역
        dbc.Row([
            # 좌측 패널: 핵심 정보 및 분석
            dbc.Col([
                # 종합 평가
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-clipboard-check me-2"),
                        html.H5("종합 평가 (Comprehensive Report)", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                create_recommendation_gauge(report_data)
                            ], width=12, md=4),
                            dbc.Col([
                                html.P(
                                    report_data.comprehensive_report.summary if report_data.comprehensive_report else "종합 평가 데이터가 없습니다.",
                                    style={'textAlign': 'justify', 'lineHeight': '1.6'}
                                )
                            ], width=12, md=8)
                        ])
                    ])
                ], className="mb-4"),
                
                # 주요 분석 포인트
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-lightbulb me-2"),
                        html.H5("주요 분석 포인트 (Executive & HR Insights)", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        create_insights_accordion(
                            report_data.executive_insights,
                            report_data.hr_points
                        )
                    ])
                ])
            ], width=12, lg=5, className="mb-4"),
            
            # 우측 패널: 시각화
            dbc.Col([
                # 레이더 차트
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-diagram-3 me-2"),
                        html.H5("6대 역량 그룹별 분석", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(
                            id="hr-visual-competency-radar",
                            figure=create_competency_radar_chart(report_data.analysis_items),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4"),
                
                # 카테고리 범례
                create_category_legend()
            ], width=12, lg=7)
        ]),
        
        # 자료 분석 아코디언
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-file-earmark-text me-2"),
                        html.H5("검토 자료별 분석 요약 (Material Analysis)", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        create_material_analysis_accordion(report_data.material_analysis)
                    ])
                ])
            ], width=12, className="mt-4")
        ])
    ], className="hr-visual-report", id="hr-visual-report-container") 