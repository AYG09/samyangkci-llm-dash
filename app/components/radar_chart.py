from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from typing import List
from ..report_schema import AnalysisItem

# 통합 인재 평가 모델 5대 차원 한글 매핑
DIMENSION_MAP = {
    "CAPABILITY": "역량",
    "PERFORMANCE": "성과",
    "POTENTIAL": "잠재력",
    "PERSONALITY": "개인특성",
    "FIT": "적합성"
}

# 5대 차원 순서 (레이더 차트 표시 순서)
CORE_DIMENSIONS = ["CAPABILITY", "PERFORMANCE", "POTENTIAL", "PERSONALITY", "FIT"]

# 차원별 색상 맵 (시각적 구분을 위한 색상)
DIMENSION_COLORS = {
    "CAPABILITY": "#1f77b4",    # 파란색 - 역량
    "PERFORMANCE": "#ff7f0e",   # 주황색 - 성과
    "POTENTIAL": "#2ca02c",     # 녹색 - 잠재력
    "PERSONALITY": "#d62728",   # 빨간색 - 개인특성
    "FIT": "#9467bd"            # 보라색 - 적합성
}

def create_radar_chart(
    analysis_items: List[AnalysisItem], context: str = "hr"
) -> html.Div:
    """
    통합 인재 평가 모델 5대 차원 레이더 차트를 생성합니다.
    context에 따라 출력 형식을 다르게 설정합니다.
    - 'hr': 기존 HR 리포트 형식 (제목, 범례 포함)
    - 'comprehensive': 종합 대시보드 형식 (차트만)
    """
    if not analysis_items:
        return html.Div([
            dbc.Alert(
                "분석 항목이 없어 레이더 차트를 생성할 수 없습니다.",
                color="warning",
                className="text-center"
            )
        ])

    # 분석 항목을 DataFrame으로 변환
    df = pd.DataFrame([item.model_dump() for item in analysis_items])
    
    # 5대 차원만 필터링
    df_filtered = df[df['category'].isin(CORE_DIMENSIONS)]
    
    if df_filtered.empty:
        return html.Div([
            dbc.Alert(
                "5대 차원에 해당하는 분석 항목이 없습니다.",
                color="warning",
                className="text-center"
            )
        ])

    # 차원별 평균 점수 계산
    dimension_scores = df_filtered.groupby('category')['score'].mean().reset_index()
    dimension_scores['dimension_kr'] = dimension_scores['category'].map(DIMENSION_MAP)
    
    # 5대 차원 순서로 정렬
    dimension_order = [DIMENSION_MAP[dim] for dim in CORE_DIMENSIONS]
    dimension_scores = dimension_scores.set_index('dimension_kr').reindex(dimension_order, fill_value=0).reset_index()
    
    # 누락된 차원이 있는지 확인하고 0점으로 채움
    for dim in CORE_DIMENSIONS:
        dim_kr = DIMENSION_MAP[dim]
        if dim_kr not in dimension_scores['dimension_kr'].values:
            new_row = pd.DataFrame({
                'dimension_kr': [dim_kr],
                'category': [dim],
                'score': [0]
            })
            dimension_scores = pd.concat([dimension_scores, new_row], ignore_index=True)
    
    # 차트 생성
    fig = go.Figure()

    # 레이더 차트 추가
    fig.add_trace(go.Scatterpolar(
        r=dimension_scores['score'],
        theta=dimension_scores['dimension_kr'],
        fill='toself',
        name='역량 점수',
        line=dict(color='#0055A4', width=3),
        fillcolor='rgba(0, 85, 164, 0.15)',
        marker=dict(size=8, color='#0055A4'),
        hovertemplate='<b>%{theta}</b><br>점수: %{r:.1f}<extra></extra>'
    ))

    # 레이아웃 설정
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
                tickfont=dict(size=11, color='#666')
            ),
            angularaxis=dict(
                direction="clockwise",
                tickfont=dict(size=13, color='#333', weight='bold'),
                rotation=90
            )
        ),
        showlegend=False,
        height=400,
        title={
            'text': "역량 분석",
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Pretendard, -apple-system, BlinkMacSystemFont, sans-serif")
    )

    # 차트 컨테이너 생성
    chart_component = html.Div([
        dcc.Graph(
            figure=fig,
            config={'displayModeBar': False},
            className="radar-chart"
        )
    ], className="radar-chart-container")

    if context == "comprehensive":
        return html.Div([
            html.H2("IV. 5대 차원 역량 프로필", className="section-title"),
            chart_component
        ], className="radar-chart-section-comprehensive light-section-container")

    # 기본값은 'hr' 컨텍스트 (기존 구조 유지)
    return html.Div([
        html.Div([
            html.H3([
                html.I(className="bi bi-diagram-3 me-2"),
                "5대 차원 역량 분석"
            ], className="text-center mb-4"),
            chart_component
        ]),

        # 차원 설명
        html.Div([
            html.H5("차원 설명", className="mb-3"),
            html.Div([
                html.Div([
                    html.Div(
                        style={
                            'width': '16px',
                            'height': '16px',
                            'backgroundColor': DIMENSION_COLORS[dim],
                            'borderRadius': '3px',
                            'display': 'inline-block',
                            'marginRight': '8px'
                        }
                    ),
                    html.Span(f"{DIMENSION_MAP[dim]}: {dim}",
                             style={'fontSize': '0.9rem', 'color': '#666'})
                ], className="d-flex align-items-center mb-2")
                for dim in CORE_DIMENSIONS
            ])
        ], className="mt-4 p-3 bg-light rounded")
    ], className="radar-chart-section")


def create_dimension_detail_table(df: pd.DataFrame) -> dbc.Card:
    """
    차원별 세부 점수 표를 생성합니다.
    """
    # 차원별 평균 점수 계산 및 정렬
    dimension_avg = df.groupby('category')['score'].mean().reset_index()
    dimension_avg['dimension_kr'] = dimension_avg['category'].map(DIMENSION_MAP)
    dimension_avg = dimension_avg.sort_values('score', ascending=False)
    
    # 테이블 행 생성
    table_rows = []
    
    for _, row in dimension_avg.iterrows():
        category = row['category']
        dimension_kr = row['dimension_kr']
        avg_score = row['score']
        
        # 해당 차원의 세부 항목들
        category_items = df[df['category'] == category].sort_values('score', ascending=False)
        
        # 점수에 따른 색상 설정
        if avg_score >= 80:
            score_color = "success"
        elif avg_score >= 60:
            score_color = "warning"
        else:
            score_color = "danger"
        
        # 차원 헤더 행
        table_rows.append(
            html.Tr([
                html.Td([
                    html.I(className="fas fa-chart-line me-2"),
                    html.Strong(dimension_kr)
                ], className="fw-bold text-primary"),
                html.Td([
                    dbc.Badge(
                        f"{avg_score:.1f}",
                        color=score_color,
                        className="px-3 py-2"
                    )
                ], className="text-end"),
                html.Td([
                    html.Div(
                        style={
                            'width': '100%',
                            'height': '8px',
                            'background': f'linear-gradient(90deg, {DIMENSION_COLORS.get(category, "#cccccc")} {avg_score}%, #f0f0f0 {avg_score}%)',
                            'borderRadius': '4px'
                        }
                    )
                ], style={'width': '150px'})
            ], className="table-primary")
        )
        
        # 세부 항목들
        for _, item in category_items.iterrows():
            score_badge_color = "success" if item['score'] >= 80 else "warning" if item['score'] >= 60 else "danger"
            
            table_rows.append(
                html.Tr([
                    html.Td([
                        html.Span("└─ ", className="text-muted"),
                        item['title']
                    ], className="ps-4 text-muted small"),
                    html.Td([
                        dbc.Badge(
                            f"{item['score']:.1f}",
                            color=score_badge_color,
                            className="px-2 py-1"
                        )
                    ], className="text-end"),
                    html.Td("")  # 빈 셀
                ])
            )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-table me-2"),
            html.H6("차원별 세부 점수", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("평가 차원", style={'width': '50%'}),
                        html.Th("점수", className="text-end", style={'width': '20%'}),
                        html.Th("진행률", style={'width': '30%'})
                    ])
                ]),
                html.Tbody(table_rows)
            ], striped=True, hover=True, size="sm")
        ])
    ], className="mb-4")


def create_dimension_legend() -> dbc.Card:
    """
    5대 차원에 대한 설명 범례를 생성합니다.
    """
    legend_items = []
    
    dimension_descriptions = {
        "CAPABILITY": {
            "name": "역량",
            "description": "전문 지식, 기술, 능력 등 업무 수행에 필요한 핵심 역량",
            "theory": "KSA 모델 기반"
        },
        "PERFORMANCE": {
            "name": "성과",
            "description": "과거 성과 및 달성도, 성과 창출 패턴 분석",
            "theory": "성과 관리 이론 기반"
        },
        "POTENTIAL": {
            "name": "잠재력",
            "description": "학습 능력, 성장 마인드셋, 적응력 등 미래 발전 가능성",
            "theory": "개발 및 성장 이론 기반"
        },
        "PERSONALITY": {
            "name": "개인특성",
            "description": "성격 특성, 행동 양식, 동기 및 가치관 등 개인의 특성",
            "theory": "개인차 이론 기반"
        },
        "FIT": {
            "name": "적합성",
            "description": "조직 문화, 직무, 팀과의 적합성 및 가치관 일치도",
            "theory": "개인-조직 적합성 이론 기반"
        }
    }
    
    for category in CORE_DIMENSIONS:
        info = dimension_descriptions[category]
        color = DIMENSION_COLORS[category]
        
        legend_items.append(
            dbc.Row([
                dbc.Col([
                    html.Div(
                        style={
                            'width': '20px',
                            'height': '20px',
                            'backgroundColor': color,
                            'borderRadius': '50%',
                            'display': 'inline-block',
                            'marginRight': '12px'
                        }
                    ),
                    html.Strong(info['name'], className="me-2"),
                    html.Span(info['description'], className="text-muted"),
                    html.Br(),
                    html.Small(
                        f"이론적 기반: {info['theory']}", 
                        className="text-info ms-4"
                    )
                ], width=12)
            ], className="mb-2")
        )
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="fas fa-info-circle me-2"),
            html.H6("통합 인재 평가 모델 - 5대 차원 설명", className="mb-0")
        ]),
        dbc.CardBody(legend_items)
    ]) 