"""A4 사이즈 PDF/PPT 출력에 최적화된 레이아웃 컴포넌트"""

from dash import html
import pandas as pd

from ..report_schema import ReportData


# A4 사이즈 최적화용 공통 스타일
A4_STYLES = {
    'page': {
        'width': '210mm',
        'minHeight': '297mm',
        'margin': '0',
        'padding': '15mm',
        'backgroundColor': 'white',
        'fontFamily': 'Pretendard, sans-serif',
        'fontSize': '10pt',
        'lineHeight': '1.3',
        'pageBreakAfter': 'always'
    },
    'header': {
        'marginBottom': '10mm',
        'paddingBottom': '5mm',
        'borderBottom': '2px solid #1A237E'
    },
    'title': {
        'fontSize': '16pt',
        'fontWeight': 'bold',
        'color': '#1A237E',
        'marginBottom': '5mm'
    },
    'subtitle': {
        'fontSize': '12pt',
        'color': '#666',
        'marginBottom': '8mm'
    },
    'section': {
        'marginBottom': '8mm'
    },
    'table': {
        'width': '100%',
        'fontSize': '9pt',
        'borderCollapse': 'collapse'
    },
    'chart': {
        'width': '100%',
        'height': '60mm'
    }
}


def create_print_header(candidate_name: str, report_type: str) -> html.Div:
    """인쇄용 헤더 생성"""
    return html.Div([
        html.Div([
            html.H1(report_type, style=A4_STYLES['title']),
            html.H2(f"후보자: {candidate_name}", style=A4_STYLES['subtitle']),
            html.P(
                "삼양KCI 면접 분석 시스템",
                style={'fontSize': '10pt', 'color': '#999'}
            )
        ], style=A4_STYLES['header'])
    ])


def create_print_executive_summary(report_data: ReportData) -> html.Div:
    """인쇄용 임원 요약 페이지"""
    if not report_data.comprehensive_report:
        return html.Div("종합 평가 데이터가 없습니다.")
    
    # 5대 차원별 평균 점수 계산
    df = pd.DataFrame([{
        'category': item.category,
        'score': item.score,
        'title': item.title
    } for item in report_data.analysis_items])
    
    # 5대 차원만 필터링
    dimension_names = {
        'CAPABILITY': '역량',
        'PERFORMANCE': '성과',
        'POTENTIAL': '잠재력',
        'PERSONALITY': '개인특성',
        'FIT': '적합성'
    }
    
    df = df[df['category'].isin(dimension_names.keys())]
    category_scores = df.groupby('category')['score'].mean().reset_index()
    category_names = dimension_names
    
    category_scores['category_kr'] = category_scores['category'].map(
        lambda x: category_names.get(x, x)
    )
    category_scores = category_scores.sort_values('score', ascending=False)
    
    # 추천 등급별 색상
    recommendation_colors = {
        '강력 추천': '#28a745',
        '추천': '#007bff',
        '고려': '#ffc107',
        '보류': '#6c757d',
        '비추천': '#dc3545'
    }
    
    rec_color = recommendation_colors.get(
        report_data.comprehensive_report.recommendation, '#6c757d'
    )

    # 역량 점수표의 tbody에 들어갈 행(Tr)들을 생성
    table_body_rows = []
    for category_code in category_scores['category']:
        category_name = category_names.get(category_code, category_code)
        category_data = df[df['category'] == category_code]

        # 해당 카테고리의 첫 번째 행 (rowSpan 적용)
        first_row_items = category_data.iloc[0]
        table_body_rows.append(html.Tr([
            html.Td(
                category_name,
                style={'padding': '3mm', 'fontWeight': 'bold', 'backgroundColor': '#f0f8ff', 'fontSize': '10pt'},
                rowSpan=len(category_data)
            ),
            html.Td(
                first_row_items['title'],
                style={'padding': '3mm', 'fontSize': '9pt'}
            ),
            html.Td(
                f"{first_row_items['score']:.1f}",
                style={'padding': '3mm', 'textAlign': 'center', 'fontSize': '9pt'}
            )
        ]))

        # 해당 카테고리의 나머지 행들
        for _, other_row_items in category_data.iloc[1:].iterrows():
            table_body_rows.append(html.Tr([
                html.Td(
                    other_row_items['title'],
                    style={'padding': '3mm', 'fontSize': '9pt'}
                ),
                html.Td(
                    f"{other_row_items['score']:.1f}",
                    style={'padding': '3mm', 'textAlign': 'center', 'fontSize': '9pt'}
                )
            ]))
    
    return html.Div([
        create_print_header(report_data.candidate_info.name, "임원용 요약 보고서"),
        
        # 페이지 1: 최종 결론 및 점수
        html.Div([
            html.Table([
                html.Tr([
                    html.Td([
                        html.H3("최종 추천", style={'margin': '0', 'fontSize': '14pt'}),
                        html.H2(
                            report_data.comprehensive_report.recommendation,
                            style={'margin': '5mm 0', 'fontSize': '24pt', 'color': rec_color}
                        )
                    ], style={'width': '40%', 'verticalAlign': 'top', 'padding': '5mm'}),
                    html.Td([
                        html.H3("종합 점수", style={'margin': '0', 'fontSize': '14pt'}),
                        html.H2(
                            f"{report_data.comprehensive_report.score:.0f}/100",
                            style={'margin': '5mm 0', 'fontSize': '24pt', 'color': rec_color}
                        )
                    ], style={'width': '30%', 'verticalAlign': 'top', 'padding': '5mm'}),
                    html.Td([
                        html.H3(
                            "후보자 정보",
                            style={'margin': '0', 'fontSize': '12pt'}
                        ),
                        html.P(
                            f"지원직급: {report_data.candidate_info.position}",
                            style={'margin': '2mm 0', 'fontSize': '10pt'}
                        ),
                        html.P(
                            f"지원조직: {report_data.candidate_info.organization}",
                            style={'margin': '2mm 0', 'fontSize': '10pt'}
                        )
                    ], style={
                        'width': '30%', 'verticalAlign': 'top', 'padding': '5mm'
                    })
                ])
            ], style={
                'width': '100%', 'border': '2px solid #1A237E',
                'marginBottom': '8mm'
            }),
            
            # 종합 의견
            html.Div([
                html.H4("종합 의견", style={'fontSize': '12pt', 'marginBottom': '3mm'}),
                html.P(
                    report_data.comprehensive_report.summary,
                    style={'fontSize': '10pt', 'lineHeight': '1.4', 'textAlign': 'justify'}
                )
            ], style=A4_STYLES['section'])
        ], style=A4_STYLES['page']),
        
        # 페이지 2: 역량 점수표
        html.Div([
            create_print_header(report_data.candidate_info.name, "역량별 상세 점수"),
            
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th(
                            "역량 그룹",
                            style={'padding': '3mm', 'backgroundColor': '#f8f9fa',
                                   'fontSize': '10pt'}
                        ),
                        html.Th(
                            "세부 역량",
                            style={'padding': '3mm', 'backgroundColor': '#f8f9fa',
                                   'fontSize': '10pt'}
                        ),
                        html.Th(
                            "점수",
                            style={'padding': '3mm', 'backgroundColor': '#f8f9fa',
                                   'fontSize': '10pt', 'textAlign': 'center'}
                        )
                    ])
                ]),
                html.Tbody(table_body_rows)
            ], style={
                'width': '100%', 'border': '1px solid #dee2e6',
                'borderCollapse': 'collapse'
            })
        ], style=A4_STYLES['page'])
    ])


def create_print_comprehensive_report(report_data: ReportData) -> html.Div:
    """인쇄용 종합 보고서"""
    return html.Div([
        create_print_header(report_data.candidate_info.name, "종합 분석 보고서"),
        
        # 페이지 1: 요약
        html.Div([
            html.Div([
                html.H4("후보자 기본 정보", style={'fontSize': '12pt', 'marginBottom': '3mm'}),
                html.Table([
                    html.Tr([
                        html.Td(
                            "이름",
                            style={'padding': '2mm', 'fontWeight': 'bold',
                                   'backgroundColor': '#f8f9fa', 'width': '20%'}
                        ),
                        html.Td(
                            report_data.candidate_info.name,
                            style={'padding': '2mm'}
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            "지원직급",
                            style={'padding': '2mm', 'fontWeight': 'bold',
                                   'backgroundColor': '#f8f9fa'}
                        ),
                        html.Td(
                            report_data.candidate_info.position,
                            style={'padding': '2mm'}
                        )
                    ]),
                    html.Tr([
                        html.Td(
                            "지원조직",
                            style={'padding': '2mm', 'fontWeight': 'bold',
                                   'backgroundColor': '#f8f9fa'}
                        ),
                        html.Td(
                            report_data.candidate_info.organization,
                            style={'padding': '2mm'}
                        )
                    ])
                ], style={
                    'width': '100%', 'border': '1px solid #dee2e6',
                    'marginBottom': '5mm'
                })
            ], style=A4_STYLES['section']),
            
            # 종합 평가 요약
            html.Div([
                html.H4("종합 평가 요약", style={'fontSize': '12pt',
                                            'marginBottom': '3mm'}),
                html.P(
                    report_data.comprehensive_report.summary
                    if report_data.comprehensive_report
                    else "종합 평가 데이터가 없습니다.",
                    style={'fontSize': '10pt', 'lineHeight': '1.4',
                           'textAlign': 'justify'}
                )
            ], style=A4_STYLES['section'])
        ], style=A4_STYLES['page']),
        
        # 페이지 2: 주요 분석 항목
        html.Div([
            create_print_header(
                report_data.candidate_info.name, "핵심 의사결정 포인트"
            ),
            html.H4(
                "👍 강점 및 기회 요인",
                style={'fontSize': '12pt', 'color': '#007bff',
                       'marginBottom': '3mm'}
            ),
            html.Ul([
                html.Li([
                    html.Strong(f"{item.title}: "),
                    html.Span(item.analysis)
                ], style={'marginBottom': '3mm', 'fontSize': '10pt'})
                for item in report_data.decision_points.strengths
            ]),
            html.Hr(style={'margin': '8mm 0'}),
            html.H4(
                "⚠️ 리스크 및 우려 사항",
                style={'fontSize': '12pt', 'color': '#dc3545',
                       'marginBottom': '3mm'}
            ),
            html.Ul([
                html.Li([
                    html.Strong(f"{item.title}: "),
                    html.Span(item.analysis)
                ], style={'marginBottom': '3mm', 'fontSize': '10pt'})
                for item in report_data.decision_points.risks
            ]),
        ], style=A4_STYLES['page']),

        # 페이지 3: 세부 역량 분석
        html.Div([
            create_print_header(
                report_data.candidate_info.name, "세부 역량 분석"
            ),
            html.Div([
                html.Ol([
                    html.Li([
                        html.Strong(f"{item.title}: "),
                        html.Span(item.analysis),
                        html.Br(),
                        html.Small(
                            f"점수: {item.score:.1f}/100",
                            style={'color': '#666'}
                        )
                    ], style={'marginBottom': '3mm', 'fontSize': '10pt'})
                    for item in report_data.analysis_items[:10]
                ])
            ])
        ], style=A4_STYLES['page'])
    ])


def create_print_hr_report(report_data: ReportData) -> html.Div:
    """인쇄용 HR 보고서"""
    return html.Div([
        create_print_header(report_data.candidate_info.name, "HR 상세 분석 보고서"),

        # 페이지 1: HR 핵심 의사결정 포인트
        html.Div([
            html.H4(
                "👍 강점 및 기회 요인",
                style={'fontSize': '12pt', 'color': '#007bff',
                       'marginBottom': '3mm'}
            ),
            html.Ul([
                html.Li([
                    html.Strong(f"{item.title}: "),
                    html.Span(item.analysis),
                    html.Br(),
                    html.Small(f"근거: {item.evidence}", style={'color': '#666'})
                ], style={'marginBottom': '5mm', 'fontSize': '10pt'})
                for item in report_data.decision_points.strengths
            ]),
            html.Hr(style={'margin': '8mm 0'}),
            html.H4(
                "⚠️ 리스크 및 우려 사항",
                style={'fontSize': '12pt', 'color': '#dc3545',
                       'marginBottom': '3mm'}
            ),
            html.Ul([
                html.Li([
                    html.Strong(f"{item.title}: "),
                    html.Span(item.analysis),
                    html.Br(),
                    html.Small(f"근거: {item.evidence}", style={'color': '#666'})
                ], style={'marginBottom': '5mm', 'fontSize': '10pt'})
                for item in report_data.decision_points.risks
            ])
        ], style=A4_STYLES['page']),

        # 페이지 2: 자료별 분석
        html.Div([
            create_print_header(report_data.candidate_info.name, "자료별 분석 요약"),
            
            html.Div([
                html.Div([
                    html.H5(
                        f"📄 {item.material_name}",
                        style={'fontSize': '11pt', 'marginBottom': '2mm'}
                    ),
                    html.P(
                        item.summary,
                        style={'fontSize': '10pt', 'marginBottom': '3mm',
                               'textAlign': 'justify'}
                    ),
                    html.P([
                        html.Strong("분석 포인트: "),
                        html.Span(item.analysis_points)
                    ], style={'fontSize': '9pt', 'marginBottom': '5mm',
                              'color': '#666'})
                ]) for item in report_data.material_analysis[:6]
            ])
        ], style=A4_STYLES['page'])
    ])


def render_print_optimized_report(report_data: ReportData, report_type: str) -> html.Div:
    """인쇄 최적화된 보고서 렌더링"""
    print_style = {
        'fontFamily': 'Pretendard, sans-serif',
        'backgroundColor': 'white',
        'color': 'black'
    }
    
    if report_type == "executive":
        content = create_print_executive_summary(report_data)
    elif report_type == "comprehensive":
        content = create_print_comprehensive_report(report_data)
    elif report_type == "hr":
        content = create_print_hr_report(report_data)
    else:
        content = html.Div("지원하지 않는 보고서 유형입니다.")
    
    return html.Div([
        # 인쇄 안내 (화면에서만 보임)
        html.Div([
            html.Div([
                html.Strong("📄 인쇄 방법: "),
                html.Span("Ctrl+P를 누르거나 브라우저 메뉴에서 인쇄를 선택하세요"),
                html.Br(),
                html.A(
                    "← 뒤로가기", href="/",
                    style={'marginLeft': '10px', 'color': '#007bff',
                           'textDecoration': 'none'}
                )
            ], style={
                'position': 'fixed',
                'top': '10px',
                'right': '10px',
                'zIndex': '1000',
                'backgroundColor': '#f8f9fa',
                'border': '1px solid #dee2e6',
                'padding': '10px 15px',
                'borderRadius': '5px',
                'fontSize': '14px',
                'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
            })
        ], style={'display': 'block'}),
        
        # 실제 보고서 내용
        html.Div(content, style=print_style)
    ]) 