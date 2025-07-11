from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from typing import List, Dict, Any
from app.report_schema import ReportData

# 상세 종합보고서 컴포넌트들 임포트
from .full_report_header import create_full_report_header
from .full_report_summary import create_full_report_summary
from .full_report_by_material import create_full_report_by_material
from .radar_chart import create_radar_chart
from .full_report_detailed_analysis import create_detailed_analysis_section


def create_comprehensive_visual_report(report_data: ReportData) -> html.Div:
    """
    HR + 임원 통합 종합 인터랙티브 비주얼 리포트를 생성합니다.
    
    구조:
    1. 핵심 지표 카드 (At a Glance)
    2. Executive Summary 탭 (임원용 요약)
    3. HR Deep Dive 탭 (HR 전문 분석)
    """
    
    # 추천 등급별 스타일 맵
    status_map = {
        '강력 추천': {'color': 'success', 'icon': 'fa-solid fa-rocket'},
        '추천': {'color': 'primary', 'icon': 'fa-solid fa-thumbs-up'},
        '고려': {'color': 'warning', 'icon': 'fa-solid fa-magnifying-glass'},
        '보류': {'color': 'secondary', 'icon': 'fa-solid fa-pause-circle'},
        '비추천': {'color': 'danger', 'icon': 'fa-solid fa-ban'}
    }
    
    # 역량 카테고리별 색상 맵
    color_map = {
        'CAREER': '#1f77b4', 'COMPETENCY': '#ff7f0e', 'SIMULATION': '#2ca02c',
        'MOTIVATION': '#d62728', 'POTENTIAL': '#9467bd', 'FIT': '#8c564b'
    }
    
    # 1. 핵심 지표 카드 생성
    key_metrics_card = _create_key_metrics_card(report_data, status_map)
    
    # 2. Executive Summary 탭 콘텐츠 생성
    executive_tab_content = _create_executive_tab_content(report_data, color_map)
    
    # 3. HR Deep Dive 탭 콘텐츠 생성
    hr_tab_content = _create_hr_tab_content(report_data, color_map)
    
    return html.Div([
        # 헤더
        dbc.Row(
            dbc.Col(
                html.Div([
                    html.H2("종합 후보자 분석 대시보드", className="text-white mb-2"),
                    html.P("AI 기반 통합 인터랙티브 비주얼 리포트 (임원 & HR)", className="text-white-50 mb-0")
                ]),
                style={'backgroundColor': '#0055A4', 'padding': '2rem', 'borderRadius': '8px'}
            ),
            className="mb-4"
        ),
        
        # 핵심 지표 카드
        dbc.Row(
            dbc.Col(key_metrics_card, width=12, className="mb-4")
        ),
        
        # 메인 탭 영역
        dbc.Row(
            dbc.Col(
                dbc.Tabs(
                    id="comprehensive-report-tabs",
                    active_tab="tab-executive",
                    children=[
                        dbc.Tab(
                            label="📊 Executive Summary", 
                            tab_id="tab-executive", 
                            children=html.Div(executive_tab_content, className="py-4")
                        ),
                        dbc.Tab(
                            label="🔍 HR Deep Dive", 
                            tab_id="tab-hr", 
                            children=html.Div(hr_tab_content, className="py-4")
                        ),
                    ]
                ),
                width=12
            )
        )
    ], className="comprehensive-visual-report")


def _create_key_metrics_card(report_data: ReportData, status_map: Dict[str, Dict[str, str]]) -> dbc.Card:
    """핵심 지표 카드를 생성합니다 (At a Glance)"""
    
    # 기본 정보 추출
    candidate_info = report_data.candidate_info
    comprehensive_report = report_data.comprehensive_report
    
    rec_status = comprehensive_report.recommendation
    status_style = status_map.get(rec_status, {'color': 'light', 'icon': 'fa-solid fa-question'})
    
    # 점수에 따라 최대 강점 또는 핵심 위험 요인 식별
    highlight_title = ""
    highlight_text = ""
    highlight_color = ""
    
    if comprehensive_report.score >= 60:  # 기준 점수 (수정 가능)
        # 강점 찾기 - 점수가 높은 항목
        if report_data.analysis_items:
            df_items = pd.DataFrame([{
                'title': item.title,
                'score': item.score,
                'analysis': item.analysis
            } for item in report_data.analysis_items])
            
            if not df_items.empty:
                top_item = df_items.loc[df_items['score'].idxmax()]
                highlight_title = "✅ 최대 강점"
                highlight_text = f"{top_item['title']}: {top_item['analysis'][:100]}..."
                highlight_color = "success"
    else:
        # 위험 요인 찾기 - executive_insights에서 위험 관련 항목 또는 점수가 낮은 항목
        risk_items = [item for item in report_data.executive_insights if "리스크" in item.title or "위험" in item.title]
        
        if risk_items:
            highlight_title = f"🚨 핵심 위험: {risk_items[0].title}"
            highlight_text = risk_items[0].analysis[:100] + "..."
        elif report_data.analysis_items:
            # 점수가 가장 낮은 항목을 표시
            df_items = pd.DataFrame([{
                'title': item.title,
                'score': item.score,
                'analysis': item.analysis
            } for item in report_data.analysis_items])
            
            if not df_items.empty:
                bottom_item = df_items.loc[df_items['score'].idxmin()]
                highlight_title = f"🚨 핵심 위험: {bottom_item['title']}"
                highlight_text = bottom_item['analysis'][:100] + "..."
        
        highlight_color = "danger"
    
    return dbc.Card(
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.P("종합 점수", className="text-muted mb-1"),
                        html.H1(f"{comprehensive_report.score:.0f}", className=f"display-2 text-{status_style['color']} mb-0")
                    ]),
                    className="text-center border-end",
                    width=12, md=3
                ),
                dbc.Col(
                    html.Div([
                        html.P("최종 추천 등급", className="text-muted mb-1"),
                        html.H3(
                            html.Span([
                                html.I(className=f"{status_style['icon']} me-2"), 
                                rec_status
                            ]), 
                            className=f"text-{status_style['color']} mb-0"
                        )
                    ]),
                    className="text-center border-end",
                    width=12, md=4
                ),
                dbc.Col(
                    html.Div([
                        html.P(highlight_title, className="text-muted mb-1"),
                        html.P(highlight_text, className=f"text-{highlight_color} small mb-0")
                    ]),
                    className="text-center",
                    width=12, md=5
                ),
            ], align="center")
        ),
        className="shadow-sm"
    )


def _create_executive_tab_content(report_data: ReportData, color_map: Dict[str, str]) -> List[Any]:
    """Executive Summary 탭 콘텐츠를 생성합니다"""
    
    # 1. 세부 역량별 점수 표만 생성 (막대그래프 제거)
    if report_data.analysis_items:
        df = pd.DataFrame([{
            'category': item.category,
            'score': item.score,
            'title': item.title
        } for item in report_data.analysis_items])
        
        # 카테고리 이름 한글화
        category_names = {
            'CAREER': '경력/전문성',
            'COMPETENCY': '핵심역량',
            'SIMULATION': '직무테스트',
            'MOTIVATION': '동기/성격',
            'POTENTIAL': '성장잠재력',
            'FIT': '조직적합성'
        }
        
        # 세부 항목별 점수 표 생성
        detail_table_rows = []
        df['category_kr'] = df['category'].map(lambda x: category_names.get(x, x))
        
        # 카테고리별 평균 점수 계산해서 정렬
        category_order = df.groupby('category_kr')['score'].mean().sort_values(ascending=False).index
        
        for category in category_order:
            category_items = df[df['category_kr'] == category].sort_values('score', ascending=False)
            
            # 카테고리 헤더
            detail_table_rows.append(
                html.Tr([
                    html.Td(category, className="fw-bold text-primary", colSpan=2),
                    html.Td(f"{category_items['score'].mean():.1f}", className="fw-bold text-primary text-end")
                ], className="table-primary")
            )
            
            # 세부 항목들
            for _, item in category_items.iterrows():
                score_color = "text-success" if item['score'] >= 80 else "text-warning" if item['score'] >= 60 else "text-danger"
                detail_table_rows.append(
                    html.Tr([
                        html.Td("", style={'width': '20px'}),  # 들여쓰기
                        html.Td(item['title'], className="small"),
                        html.Td(f"{item['score']:.1f}", className=f"text-end {score_color}")
                    ])
                )
        
        # 표만 표시 (차트 제거)
        competency_content = html.Div([
            html.H5("6대 역량 그룹별 세부 점수", className="mb-3"),
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("", style={'width': '20px'}),
                        html.Th("역량 항목", style={'width': '70%'}),
                        html.Th("점수", style={'width': '30%'}, className="text-end")
                    ])
                ]),
                html.Tbody(detail_table_rows)
            ], striped=True, hover=True, size="sm", className="mb-0")
        ])
        
    else:
        competency_content = html.Div("분석 항목 데이터가 없습니다.", className="text-center text-muted")
    
    # 2. Executive & HR Insights 리스트
    insights_items = []
    
    if report_data.executive_insights:
        insights_items.append(dbc.ListGroupItem(html.H5("💡 Executive Insights", className="mb-0")))
        for item in report_data.executive_insights:
            insights_items.append(
                dbc.ListGroupItem([
                    html.Strong(f"{item.title}: "), 
                    html.Span(item.analysis)
                ])
            )
    
    if report_data.hr_points:
        insights_items.append(dbc.ListGroupItem(html.H5("⚙️ HR Points", className="mt-3 mb-0")))
        for item in report_data.hr_points:
            insights_items.append(
                dbc.ListGroupItem([
                    html.Strong(f"{item.title}: "), 
                    html.Span(item.analysis)
                ])
            )
    
    if not insights_items:
        insights_list = html.Div("인사이트 데이터가 없습니다.", className="text-center text-muted")
    else:
        insights_list = dbc.ListGroup(insights_items, flush=True)
    
    return [
        dbc.Row([
            dbc.Col(competency_content, width=12, lg=6),
            dbc.Col(insights_list, width=12, lg=6)
        ])
    ]


def _create_hr_tab_content(report_data: ReportData, color_map: Dict[str, str]) -> List[Any]:
    """HR Deep Dive 탭에 상세 종합보고서의 모든 내용을 표시합니다"""
    
    # 상세 종합보고서의 모든 섹션들 생성
    header_section = create_full_report_header(report_data.candidate_info)
    summary_section = create_full_report_summary(report_data.comprehensive_report)
    by_material_section = create_full_report_by_material(report_data.material_analysis)
    radar_chart_section = create_radar_chart(report_data.analysis_items)
    detailed_analysis_section = create_detailed_analysis_section(report_data.analysis_items)
    
    return [
        html.Div([
            header_section,
            html.Hr(className="my-4"),
            summary_section,
            html.Hr(className="my-4"),
            by_material_section,
            html.Hr(className="my-4"),
            radar_chart_section,
            html.Hr(className="my-4"),
            detailed_analysis_section
        ], className="hr-deep-dive-content")
    ] 