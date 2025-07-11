"""임원 보고용 인터랙티브 비주얼 리포트 컴포넌트"""

import dash_bootstrap_components as dbc
from dash import html, dcc
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
    
    category_scores = df.groupby('category')['score'].mean().reset_index()
    category_scores = category_scores.sort_values('score', ascending=True)
    
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
    
    fig = go.Figure(go.Bar(
        x=category_scores['score'],
        y=category_scores['category_kr'],
        orientation='h',
        marker=dict(
            color=category_scores['score'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=100,
        ),
        text=category_scores['score'].apply(lambda x: f'{x:.1f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>점수: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='6대 역량 그룹별 평균 점수',
        xaxis_title="점수 (100점 만점)",
        yaxis_title="역량 그룹",
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
    
    # 카테고리 이름 한글화
    category_names = {
        'CAREER': '경력/전문성',
        'COMPETENCY': '핵심역량',
        'SIMULATION': '직무테스트',
        'MOTIVATION': '동기/성격',
        'POTENTIAL': '성장잠재력',
        'FIT': '조직적합성'
    }
    
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


def create_key_risks_card(executive_insights: List[Any], hr_points: List[Any]) -> dbc.Card:
    """주요 리스크 카드를 생성합니다."""
    # 리스크 관련 항목 추출
    risk_items = []
    
    # Executive insights에서 리스크 관련 항목 찾기
    for item in executive_insights:
        if any(keyword in item.title for keyword in ['리스크', '위험', '경영적', '우려']):
            risk_items.append({
                'title': item.title,
                'analysis': item.analysis,
                'type': 'executive'
            })
    
    # HR points에서 리스크 관련 항목 찾기
    for item in hr_points:
        if any(keyword in item.title for keyword in ['리스크', '위험', '법적', '윤리적']):
            risk_items.append({
                'title': item.title,
                'analysis': item.analysis,
                'type': 'hr'
            })
    
    # 리스크가 없는 경우 일반적인 우려사항 표시
    if not risk_items and executive_insights:
        risk_items = [
            {
                'title': item.title,
                'analysis': item.analysis,
                'type': 'general'
            } for item in executive_insights[:3]  # 상위 3개 항목
        ]
    
    risk_list_items = []
    for item in risk_items:
        icon_class = {
            'executive': 'bi bi-exclamation-triangle text-warning',
            'hr': 'bi bi-shield-exclamation text-danger',
            'general': 'bi bi-info-circle text-primary'
        }.get(item['type'], 'bi bi-info-circle text-primary')
        
        risk_list_items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className=f"{icon_class} me-2"),
                    html.Strong(item['title'])
                ], className="mb-2"),
                html.P(item['analysis'], className="mb-0 text-muted small")
            ])
        )
    
    if not risk_list_items:
        risk_list_items = [
            dbc.ListGroupItem(
                "특별한 위험 요인이 식별되지 않았습니다.",
                color="success"
            )
        ]
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-shield-exclamation me-2"),
            "주요 위험 요인 (Key Risk Factors)"
        ]),
        dbc.ListGroup(risk_list_items, flush=True)
    ], className="h-100")


def create_insights_accordion_content(executive_insights: List[Any], hr_points: List[Any]) -> dbc.ListGroup:
    """핵심 의사결정 포인트 아코디언 내용을 생성합니다."""
    items = []
    
    # Executive insights 추가
    for item in executive_insights:
        items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-lightbulb text-warning me-2"),
                    html.Strong(item.title)
                ], className="mb-2"),
                html.P(item.analysis, className="mb-1 text-muted"),
                html.Small(f"근거: {item.evidence}", className="text-secondary")
            ])
        )
    
    # HR points 추가
    for item in hr_points:
        items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-people text-info me-2"),
                    html.Strong(item.title)
                ], className="mb-2"),
                html.P(item.analysis, className="mb-1 text-muted"),
                html.Small(f"근거: {item.evidence}", className="text-secondary")
            ])
        )
    
    return dbc.ListGroup(items, flush=True)


def create_material_analysis_accordion_content(material_analysis: List[Any]) -> dbc.ListGroup:
    """자료별 분석 요약 아코디언 내용을 생성합니다."""
    items = []
    
    for item in material_analysis:
        items.append(
            dbc.ListGroupItem([
                html.Div([
                    html.I(className="bi bi-file-earmark-text me-2"),
                    html.Strong(item.material_name)
                ], className="mb-2"),
                html.Blockquote(
                    item.summary,
                    className="mb-2 text-muted small border-start border-3 ps-3"
                ),
                html.P([
                    html.Strong("분석 포인트: "),
                    item.analysis_points
                ], className="small mb-0")
            ])
        )
    
    return dbc.ListGroup(items, flush=True)


def render_executive_visual_report(report_data: ReportData) -> html.Div:
    """임원용 비주얼 리포트를 렌더링합니다."""
    return html.Div([
        # 헤더
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2([
                        html.I(className="bi bi-graph-up-arrow me-2"),
                        "Executive Visual Report"
                    ], className="text-white mb-1"),
                    html.P("AI 기반 후보자 종합 분석 보고서", className="text-white-50 mb-0")
                ], className="p-4")
            ], width=12, style={'backgroundColor': '#1A237E'})
        ], className="mb-4"),
        
        # 최종 결론 카드
        dbc.Row([
            dbc.Col([
                create_executive_summary_card(report_data)
            ], width=12)
        ]),
        
        # 역량 요약 및 주요 리스크
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="bi bi-bar-chart me-2"),
                        html.H5("역량 프로필 및 주요 리스크 요약", className="m-0 d-inline")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(
                                    id="exec-visual-competency-chart",
                                    figure=create_competency_chart(report_data.analysis_items),
                                    config={'displayModeBar': False}
                                )
                            ], width=12, md=7),
                            dbc.Col([
                                create_key_risks_card(
                                    report_data.executive_insights,
                                    report_data.hr_points
                                )
                            ], width=12, md=5)
                        ]),
                        # 세부 역량별 점수 테이블 추가
                        html.Hr(className="my-4"),
                        html.H6("세부 역량별 점수", className="mb-3"),
                        create_competency_detail_table(report_data.analysis_items)
                    ])
                ], className="mb-4 shadow-sm")
            ], width=12)
        ]),
        
        # 상세 분석 아코디언
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="bi bi-zoom-in me-2"),
                        "상세 분석 (Drill-down)"
                    ], className="mb-3"),
                    dbc.Accordion([
                        dbc.AccordionItem([
                            create_insights_accordion_content(
                                report_data.executive_insights,
                                report_data.hr_points
                            )
                        ], title="💡 핵심 의사결정 포인트 (Executive & HR Insights)"),
                        dbc.AccordionItem([
                            create_material_analysis_accordion_content(
                                report_data.material_analysis
                            )
                        ], title="📄 검토 자료별 분석 요약 (Material Analysis)")
                    ], start_collapsed=True, always_open=False)
                ])
            ], width=12)
        ])
    ], className="executive-visual-report", id="exec-visual-report-container") 