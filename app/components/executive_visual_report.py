"""임원 보고용 인터랙티브 비주얼 리포트 컴포넌트"""

import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go
import pandas as pd
from typing import List, Any

from ..report_schema import ReportData


def create_executive_summary_card(report_data: ReportData) -> dbc.Card:
    """최종 결론 카드를 생성합니다."""
    if not report_data.comprehensive_report:
        return dbc.Card(
            dbc.CardBody("종합 평가 데이터가 없습니다."),
            className="mb-4 shadow-sm"
        )
    
    # 추천 등급별 스타일 맵
    status_map = {
        '강력 추천': {'color': 'success', 'icon': 'bi bi-rocket-takeoff'},
        '추천': {'color': 'primary', 'icon': 'bi bi-hand-thumbs-up'},
        '고려': {'color': 'warning', 'icon': 'bi bi-search'},
        '보류': {'color': 'secondary', 'icon': 'bi bi-pause-circle'},
        '비추천': {'color': 'danger', 'icon': 'bi bi-x-circle'}
    }
    
    recommendation = report_data.comprehensive_report.recommendation
    score = report_data.comprehensive_report.score
    summary = report_data.comprehensive_report.summary
    
    status_style = status_map.get(recommendation, {'color': 'light', 'icon': 'bi bi-question-circle'})
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className=f"{status_style['icon']} me-2"),
            html.Span(f"최종 추천: {recommendation}")
        ], className=f"bg-{status_style['color']} text-white h4 mb-0"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H1(f"{score:.0f}", className="display-3 text-center"),
                    html.P("종합 점수", className="text-center text-muted")
                ], width=12, md=3, className="d-flex flex-column justify-content-center border-end"),
                dbc.Col([
                    html.H5(f"{report_data.candidate_info.name} | {report_data.candidate_info.position}", 
                           className="mb-3"),
                    html.P(summary, className="text-muted", style={'textAlign': 'justify'})
                ], width=12, md=9, className="p-3")
            ], className="g-0")
        ])
    ], className="mb-4 shadow-sm")


def create_competency_chart(analysis_items: List[Any]) -> go.Figure:
    """역량 요약 바 차트를 생성합니다."""
    if not analysis_items:
        return go.Figure()
    
    # 카테고리별 평균 점수 계산
    df = pd.DataFrame([{
        'category': item.category,
        'score': item.score,
        'title': item.title
    } for item in analysis_items])
    
    # 5개 차원만 필터링
    dimension_names = {
        'CAPABILITY': '역량',
        'PERFORMANCE': '성과',
        'POTENTIAL': '잠재력',
        'PERSONALITY': '개인특성',
        'FIT': '적합성'
    }
    
    df = df[df['category'].isin(dimension_names.keys())]
    category_scores = df.groupby('category')['score'].mean().reset_index()
    category_scores = category_scores.sort_values('score', ascending=True)
    
    # 차원 이름 한글화
    category_scores['category_kr'] = category_scores['category'].map(dimension_names)
    
    # 5개 차원별 고유 색상 매핑
    dimension_colors = {
        'CAPABILITY': '#1f77b4',    # 파란색 - 역량
        'PERFORMANCE': '#ff7f0e',   # 주황색 - 성과
        'POTENTIAL': '#2ca02c',     # 녹색 - 잠재력
        'PERSONALITY': '#d62728',   # 빨간색 - 개인특성
        'FIT': '#9467bd'            # 보라색 - 적합성
    }
    
    # 각 차원별 색상 적용
    bar_colors = [dimension_colors.get(cat, '#cccccc') for cat in category_scores['category']]
    
    fig = go.Figure(go.Bar(
        x=category_scores['score'],
        y=category_scores['category_kr'],
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color='rgba(0,0,0,0.1)', width=0.5)
        ),
        text=category_scores['score'].apply(lambda x: f'{x:.1f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>점수: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='5대 차원별 평균 점수',
        xaxis_title="점수 (100점 만점)",
        yaxis_title="차원",
        xaxis=dict(range=[0, 110]),
        height=200,  # 350에서 200으로 줄임
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Pretendard, sans-serif")
    )
    
    return fig


def create_competency_detail_table(analysis_items: List[Any]) -> dbc.Table:
    """세부 역량별 점수 테이블을 생성합니다."""
    if not analysis_items:
        return dbc.Table()
    
    # 카테고리별로 그룹화
    df = pd.DataFrame([{
        'category': item.category,
        'title': item.title,
        'score': item.score,
        'analysis': item.analysis
    } for item in analysis_items])
    
    # 5개 차원만 필터링
    dimension_names = {
        'CAPABILITY': '역량',
        'PERFORMANCE': '성과',
        'POTENTIAL': '잠재력',
        'PERSONALITY': '개인특성',
        'FIT': '적합성'
    }
    
    # 5개 차원만 필터링
    df = df[df['category'].isin(dimension_names.keys())]
    
    # 카테고리 이름 한글화
    category_names = dimension_names
    
    df['category_kr'] = df['category'].map(
        lambda x: category_names.get(x, x)
    )
    
    # 카테고리별 평균 점수 계산해서 정렬
    category_order = df.groupby('category_kr')['score'].mean().sort_values(ascending=False).index
    
    # 테이블 행 생성
    table_rows = []
    for category in category_order:
        category_items = df[df['category_kr'] == category].sort_values('score', ascending=False)
        
        # 카테고리 헤더
        table_rows.append(
            html.Tr([
                html.Td(category, className="fw-bold text-primary", colSpan=2),
                html.Td(f"{category_items['score'].mean():.1f}", className="fw-bold text-primary text-end")
            ], className="table-primary")
        )
        
        # 세부 항목들
        for _, item in category_items.iterrows():
            score_color = "text-success" if item['score'] >= 80 else "text-warning" if item['score'] >= 60 else "text-danger"
            table_rows.append(
                html.Tr([
                    html.Td("", style={'width': '20px'}),  # 들여쓰기
                    html.Td(item['title'], className="small"),
                    html.Td(f"{item['score']:.1f}", className=f"text-end {score_color}")
                ])
            )
    
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("", style={'width': '20px'}),
                html.Th("역량 항목", style={'width': '70%'}),
                html.Th("점수", style={'width': '30%'}, className="text-end")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, hover=True, size="sm", className="mb-0")


def create_strengths_card(decision_points: Any) -> dbc.Card:
    """주요 강점 카드를 생성합니다."""
    if not hasattr(decision_points, 'strengths') or not decision_points.strengths:
        return dbc.Card(
            dbc.CardBody("분석된 강점이 없습니다."),
            className="mb-4"
        )
    
    strength_items = []
    for item in decision_points.strengths:
        strength_items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-graph-up-arrow me-2 text-primary"),
                    html.Strong(getattr(item, 'title', '강점'))
                ], className="mb-2"),
                html.P(getattr(item, 'analysis', ''), className="mb-0 text-muted small")
            ])
        )
        
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-trophy me-2"),
            "Key Strengths"
        ]),
        dbc.ListGroup(strength_items, flush=True)
    ], className="mb-4")


def create_key_risks_card(decision_points: Any) -> dbc.Card:
    """주요 리스크 카드를 생성합니다."""
    if not hasattr(decision_points, 'risks') or not decision_points.risks:
        return dbc.Card(
            dbc.CardBody([
                html.I(className="bi bi-check-circle-fill me-2 text-success"),
                "특별한 위험 요인이 식별되지 않았습니다."
            ]),
            className="mb-4"
        )

    risk_items = []
    for item in decision_points.risks:
        risk_items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-exclamation-triangle me-2 text-danger"),
                    html.Strong(getattr(item, 'title', '리스크'))
                ], className="mb-2"),
                html.P(getattr(item, 'analysis', ''), className="mb-0 text-muted small")
            ])
        )
        
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-shield-exclamation me-2"),
            "Key Risk Factors"
        ]),
        dbc.ListGroup(risk_items, flush=True)
    ], className="mb-4")


def create_material_analysis_accordion_content(material_analysis: List[Any]) -> dbc.ListGroup:
    """자료별 분석 요약 ListGroup을 생성합니다."""
    if not material_analysis:
        return dbc.ListGroup(
            dbc.ListGroupItem("분석된 자료가 없습니다.")
        )
    
    accordion_items = []
    for item in material_analysis:
        accordion_items.append(
            dbc.ListGroupItem([
                html.H6(item.material_name, className="mb-2 text-primary"),
                html.P([
                    html.Strong("요약: "),
                    item.summary
                ], className="mb-1 small"),
                html.P([
                    html.Strong("주요 포인트: "),
                    item.analysis_points
                ], className="mb-0 small text-muted")
            ])
        )
    
    return dbc.ListGroup(accordion_items, flush=True)


def render_executive_visual_report(report_data: ReportData) -> html.Div:
    """임원 보고용 비주얼 리포트를 렌더링합니다."""
    return html.Div([
        # 헤더
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H3("Executive Visual Report", className="text-white"),
                    html.P("핵심 요약 및 의사결정 지원을 위한 보고서", className="text-white-50")
                ], className="p-4 rounded", style={'backgroundColor': '#003366'}),
                width=12
            )
        ], className="mb-4"),

        # 최종 결론
        create_executive_summary_card(report_data),

        # 강점 및 리스크
        dbc.Row([
            dbc.Col(
                create_strengths_card(report_data.decision_points), 
                width=12, 
                lg=6
            ),
            dbc.Col(
                create_key_risks_card(report_data.decision_points), 
                width=12, 
                lg=6
            )
        ]),

        # 상세 분석
        dbc.Card([
            dbc.CardHeader("상세 분석 (Drill-down)"),
            dbc.CardBody([
                dbc.Accordion([
                    dbc.AccordionItem(
                        create_competency_detail_table(report_data.analysis_items),
                        title="1. 5대 차원별 상세 점수"
                    ),
                    dbc.AccordionItem(
                        create_material_analysis_accordion_content(report_data.material_analysis),
                        title="2. 검토 자료별 분석 요약"
                    )
                ], start_collapsed=True, always_open=True)
            ])
        ], className="mb-4")
        
    ], className="executive-visual-report-container p-3") 