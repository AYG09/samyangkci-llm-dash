"""HR 담당자용 인터랙티브 비주얼 리포트 컴포넌트"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
from typing import List, Any

from ..report_schema import ReportData

# 5개 차원 기반 색상 맵 (레이더 차트와 일치)
CATEGORY_COLOR_MAP = {
    'CAPABILITY': '#1f77b4',    # 파란색 - 역량
    'PERFORMANCE': '#ff7f0e',   # 주황색 - 성과
    'POTENTIAL': '#2ca02c',     # 녹색 - 잠재력
    'PERSONALITY': '#d62728',   # 빨간색 - 개인특성
    'FIT': '#9467bd'            # 보라색 - 적합성
}

# 5개 차원 한국어 매핑
DIMENSION_NAMES = {
    'CAPABILITY': '역량',
    'PERFORMANCE': '성과',
    'POTENTIAL': '잠재력',
    'PERSONALITY': '개인특성',
    'FIT': '적합성'
}

# 추천 등급별 스타일 맵
RECOMMENDATION_STYLE_MAP = {
    '강력 추천': {'color': 'success', 'icon': 'bi bi-hand-thumbs-up'},
    '추천': {'color': 'primary', 'icon': 'bi bi-check-circle'},
    '고려': {'color': 'warning', 'icon': 'bi bi-search'},
    '보류': {'color': 'secondary', 'icon': 'bi bi-pause-circle'},
    '비추천': {'color': 'danger', 'icon': 'bi bi-hand-thumbs-down'}
}


def _create_empty_radar_chart() -> go.Figure:
    """빈 레이더 차트를 생성합니다."""
    fig = go.Figure()
    fig.update_layout(
        annotations=[
            dict(
                text="분석 데이터가 부족합니다",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color="gray")
            )
        ],
        height=450,
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig


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
                        html.I(
                            className="bi bi-currency-dollar me-2 text-warning"
                        ),
                        html.Strong("연봉 정보: "),
                        info.salary_info
                    ], className="mb-2")
                ], width=12, md=6)
            ])
        ])
    ], className="mb-4")


def create_recommendation_gauge(report_data: ReportData) -> dbc.Card:
    """추천 등급 게이지 카드를 생성합니다."""
    try:
        if (not hasattr(report_data, 'comprehensive_report') or 
                not report_data.comprehensive_report):
            return dbc.Card(
                dbc.CardBody("종합 평가 데이터가 없습니다."),
                className="h-100"
            )
        
        recommendation = getattr(
            report_data.comprehensive_report, 'recommendation', '평가 없음'
        )
        score = getattr(report_data.comprehensive_report, 'score', 0)
    except Exception as e:
        print(f"추천 게이지 데이터 처리 중 오류: {e}")
        return dbc.Card(
            dbc.CardBody("추천 데이터를 처리할 수 없습니다."),
            className="h-100"
        )
    
    style = RECOMMENDATION_STYLE_MAP.get(
        recommendation, 
        {'color': 'light', 'icon': 'bi bi-question-circle'}
    )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className=f"{style['icon']} me-2"),
            html.Span("채용추천", className="fw-bold")
        ], className=f"bg-{style['color']} text-white text-center py-2"),
        dbc.CardBody([
            html.Div([
                html.H4(
                    recommendation, className=f"text-{style['color']} mb-2 fw-bold"
                ),
                html.Hr(className="my-2"),
                html.H2(f"{score:.1f}", className=f"text-{style['color']} mb-1"),
                html.P("/ 100점", className="text-muted mb-0")
            ], className="text-center")
        ])
    ], className="h-100")


def create_competency_radar_chart(analysis_items: List[Any]) -> go.Figure:
    """5개 차원별 레이더 차트를 생성합니다."""
    if not analysis_items:
        return _create_empty_radar_chart()
    
    try:
        # 데이터 준비 - 카테고리별 평균 점수 계산
        df = pd.DataFrame([
            {
                'category': getattr(item, 'category', 'CAPABILITY'),
                'score': getattr(item, 'score', 0)
            } 
            for item in analysis_items 
            if hasattr(item, 'category') and hasattr(item, 'score')
        ])
        
        if df.empty:
            return _create_empty_radar_chart()
        
        category_scores = df.groupby('category')['score'].mean().reset_index()
        
        # 5개 차원만 필터링
        category_scores = category_scores[
            category_scores['category'].isin(DIMENSION_NAMES.keys())
        ]
        
        # 누락된 차원에 대해 기본값 추가
        missing_dimensions = set(DIMENSION_NAMES.keys()) - set(
            category_scores['category']
        )
        for dim in missing_dimensions:
            new_row = pd.DataFrame([{'category': dim, 'score': 0}])
            category_scores = pd.concat(
                [category_scores, new_row], ignore_index=True
            )
        
        # 차원 이름 한글화
        category_scores['category_kr'] = category_scores['category'].map(
            DIMENSION_NAMES
        )
        
        # 레이더 차트 생성
        fig = go.Figure()
        
        # 카테고리별 색상 적용
        category_colors = [
            CATEGORY_COLOR_MAP.get(cat, '#cccccc') 
            for cat in category_scores['category']
        ]
        
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
            title='5대 차원별 분석',
            height=450,
            margin=dict(l=80, r=80, t=80, b=80),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Pretendard, sans-serif")
        )
        
        return fig
        
    except Exception as e:
        print(f"레이더 차트 생성 중 오류: {e}")
        return _create_empty_radar_chart()


def create_decision_points_section(decision_points: Any) -> html.Div:
    """핵심 의사결정 포인트를 (강점/리스크) 생성합니다."""
    
    # 강점 리스트 생성
    strengths_items = []
    if hasattr(decision_points, 'strengths') and decision_points.strengths:
        for item in decision_points.strengths:
            strengths_items.append(
                html.Li([
                    html.Strong(f"✔️ {getattr(item, 'title', '강점')}: "),
                    html.Span(getattr(item, 'analysis', ''))
                ], className="mb-2")
            )
    
    # 리스크 리스트 생성
    risks_items = []
    if hasattr(decision_points, 'risks') and decision_points.risks:
        for item in decision_points.risks:
            risks_items.append(
                html.Li([
                    html.Strong(f"⚠️ {getattr(item, 'title', '리스크')}: "),
                    html.Span(getattr(item, 'analysis', ''))
                ], className="mb-2")
            )

    if not strengths_items and not risks_items:
        return html.Div(
            html.P("핵심 의사결정 포인트 데이터가 없습니다.", className="text-muted text-center"),
            className="p-3"
        )
        
    return html.Div([
        # 강점 섹션
        html.Div([
            html.H6([
                html.I(className="bi bi-graph-up-arrow me-2 text-primary"),
                "Strengths (강점 및 기회 요인)"
            ], className="mb-3"),
            html.Ul(strengths_items if strengths_items else [html.Li("분석된 강점이 없습니다.", className="text-muted")], className="list-unstyled")
        ]),
        
        html.Hr(className="my-4"),
        
        # 리스크 섹션
        html.Div([
            html.H6([
                html.I(className="bi bi-exclamation-triangle me-2 text-danger"),
                "Risks (리스크 및 우려 사항)"
            ], className="mb-3"),
            html.Ul(risks_items if risks_items else [html.Li("분석된 리스크가 없습니다.", className="text-muted")], className="list-unstyled")
        ]),
    ])


def create_material_analysis_accordion(
    material_analysis: List[Any]
) -> dbc.Accordion:
    """자료별 분석 아코디언을 생성합니다."""
    accordion_items = []
    
    if material_analysis:
        for i, item in enumerate(material_analysis):
            try:
                material_name = getattr(item, 'material_name', f'자료 {i+1}')
                summary = getattr(item, 'summary', '요약 정보가 없습니다.')
                analysis_points = getattr(
                    item, 'analysis_points', '분석 포인트가 없습니다.'
                )
                
                accordion_items.append(
                    dbc.AccordionItem([
                        html.Div([
                            html.H6([
                                html.I(className="bi bi-file-text me-2"),
                                "핵심 내용 요약"
                            ], className="mt-2 mb-3"),
                            html.P(summary, className="mb-3"),
                            html.H6([
                                html.I(className="bi bi-lightbulb me-2"),
                                "주요 분석 포인트"
                            ], className="mb-3"),
                            html.P(analysis_points, className="mb-0")
                        ])
                    ], title=f"📄 {material_name}")
                )
            except Exception as e:
                print(f"자료 분석 처리 중 오류: {e}")
                continue
    
    # 자료가 없는 경우 기본 메시지 추가
    if not accordion_items:
        accordion_items.append(
            dbc.AccordionItem([
                html.Div([
                    html.P("분석할 자료가 없습니다.", className="text-muted text-center")
                ])
            ], title="📄 자료 없음")
        )
    
    return dbc.Accordion(
        accordion_items,
        start_collapsed=True,
        always_open=True,
        flush=True
    )


def create_category_legend() -> dbc.Card:
    """5개 차원 카테고리 범례를 생성합니다."""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-palette me-2"),
            html.H6("5대 차원 분류", className="m-0 d-inline")
        ]),
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.Div(
                        style={
                            'width': '16px',
                            'height': '16px',
                            'backgroundColor': color,
                            'borderRadius': '3px',
                            'border': '1px solid rgba(0,0,0,0.1)',
                            'display': 'inline-block',
                            'marginRight': '8px'
                        }
                    ),
                    html.Span(
                        name, 
                        style={'fontSize': '0.9rem', 'fontWeight': '500'}
                    )
                ], className="legend-item")
                for category, (color, name) in zip(
                    DIMENSION_NAMES.keys(),
                    [(CATEGORY_COLOR_MAP[cat], DIMENSION_NAMES[cat]) 
                     for cat in DIMENSION_NAMES.keys()]
                )
            ])
        ])
    ], className="category-legend")


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
        
        # 메인 분석 영역
        dbc.Row([
            # 좌측 패널: 추천 결과 및 인사이트
            dbc.Col([
                # 추천 결과 게이지
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-speedometer2 me-2"),
                        html.H5("최종 추천 결과", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        create_recommendation_gauge(report_data)
                    ])
                ], className="mb-4"),
                
                # 핵심 인사이트
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-bullseye me-2"),
                        html.H5("핵심 의사결정 포인트", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        create_decision_points_section(
                            report_data.decision_points
                        )
                    ])
                ])
            ], width=12, lg=5),
            
            # 우측 패널: 시각화
            dbc.Col([
                # 레이더 차트
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-diagram-3 me-2"),
                        html.H5("5대 차원별 분석", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        dcc.Graph(
                            id="hr-visual-competency-radar",
                            figure=create_competency_radar_chart(
                                report_data.analysis_items
                            ),
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
                        html.H5(
                            "검토 자료별 분석 요약 (Material Analysis)", 
                            className="m-0 d-inline"
                        )
                    ]),
                    dbc.CardBody([
                        create_material_analysis_accordion(
                            report_data.material_analysis
                        )
                    ])
                ])
            ], width=12, className="mt-4")
        ])
    ], className="hr-visual-report", id="hr-visual-report-container") 