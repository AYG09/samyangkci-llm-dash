"""페이지 라우팅 관련 콜백 함수들"""

import dash
from dash import Output, Input, html


def render_main_layout():
    """메인 애플리케이션 레이아웃을 렌더링합니다."""
    from dash import html, dcc
    import dash_bootstrap_components as dbc
    from ..ui_llm_input import render_llm_input_tab
    from ..ui_report import render_report_tab
    from ..ui_settings import render_settings_tab
    from ..dash_prompt_generator import render_dash_prompt_generator
    
    return html.Div([
        html.Nav(
            [
                html.Div(
                    [
                        html.Span(
                            "SAMYANG",
                            style={
                                "fontWeight": 900,
                                "fontSize": "1.6rem",
                                "color": "#1A237E",
                                "letterSpacing": "-1.5px",
                                "fontFamily": "Pretendard, sans-serif",
                            },
                        ),
                        html.Br(),
                        html.Span(
                            "KCI",
                            style={
                                "fontWeight": 700,
                                "fontSize": "0.9rem",
                                "color": "#1A237E",
                                "letterSpacing": "0.1em",
                                "fontFamily": "Pretendard, sans-serif",
                            },
                        ),
                    ],
                    style={"display": "inline-block", "verticalAlign": "middle"},
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "padding": "18px 0 10px 0",
                "borderBottom": "1px solid #E0E4EA",
                "background": "#fff",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            [
                                html.Span(
                                    "📝",
                                    style={"fontSize": "1.5rem", "marginRight": "8px"},
                                ),
                                "LLM 면접 분석 시스템",
                            ],
                            className="main-title",
                            style={
                                "fontWeight": 800,
                                "fontSize": "2.1rem",
                                "letterSpacing": "-1.2px",
                                "marginBottom": "2px",
                                "color": "#1A237E",
                            },
                        ),
                        html.Div(
                            "Powered by Samyang KCI HR Team",
                            className="brand-slogan",
                            style={
                                "fontWeight": 500,
                                "fontSize": "0.95rem",
                                "color": "#5A687D",
                                "letterSpacing": "0px",
                                "marginTop": "6px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "marginLeft": "8px",
                    },
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "18px",
                "marginBottom": "8px",
                "marginTop": "18px",
            },
        ),
        html.Div(className="brand-gradient-bar"),
        dcc.Tabs(
            [
                dcc.Tab(label="📋 프롬프트 생성", value="tab-prompt"),
                dcc.Tab(label="📝 LLM 분석 결과 입력", value="tab-result"),
                dcc.Tab(label="📊 면접자 조회", value="tab-report"),
                dcc.Tab(label="⚙️ 설정", value="tab-settings"),
            ],
            id="main-tabs",
            value="tab-prompt",
            className="dash-tabs",
            style={
                "marginTop": "24px",
                "fontWeight": 600,
                "fontSize": "1.08rem",
                "letterSpacing": "-0.5px",
            },
        ),
        html.Div(id="tab-content"),
    ])


def register_routing_callbacks(app):
    """페이지 라우팅 관련 콜백들을 앱에 등록합니다."""
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        """URL 경로에 따라 페이지를 렌더링합니다."""
        if pathname and pathname.startswith('/print-report/'):
            # 인쇄 보고서 페이지
            try:
                import urllib.parse
                parts = pathname.split('/')
                candidate_id = urllib.parse.unquote(parts[2])  # URL 디코딩
                report_type = parts[3]
                
                print(f"[DEBUG] 인쇄 보고서 요청: candidate_id='{candidate_id}', report_type='{report_type}'")
                
                from ..components.print_optimized_reports import render_print_optimized_report
                from ..report_schema import ReportData
                from ..utils import try_parse_json
                from ..db import get_candidate_by_id
                
                # 후보자 데이터 조회
                candidate = get_candidate_by_id(candidate_id)
                print(f"[DEBUG] 후보자 데이터 조회 결과: {candidate is not None}")
                if not candidate:
                    return html.Div(f"후보자를 찾을 수 없습니다. (ID: {candidate_id})")
                
                # evaluator 필드에서 실제 분석 데이터 파싱
                evaluator_data = candidate.get('evaluator', '{}')
                print(f"[DEBUG] evaluator 데이터 길이: {len(evaluator_data)}")
                print(f"[DEBUG] evaluator 데이터 시작 200자: {evaluator_data[:200]}")
                
                json_data = try_parse_json(evaluator_data)
                print(f"[DEBUG] JSON 데이터 파싱 결과: {json_data is not None}")
                if json_data is None:
                    # JSON 파싱 실패 시 LLM 텍스트로 처리
                    print(f"[DEBUG] JSON 파싱 실패 - LLM 텍스트로 처리 시도")
                    try:
                        from ..llm_report_parser import parse_llm_report
                        report_data = parse_llm_report(evaluator_data)
                        print(f"[DEBUG] LLM 텍스트 파싱 성공")
                    except Exception as e:
                        print(f"[DEBUG] LLM 텍스트 파싱도 실패: {e}")
                        return html.Div(f"분석 데이터를 읽을 수 없습니다. evaluator 데이터: {evaluator_data[:200]}...")
                else:
                    # JSON 데이터가 이미 구조화되어 있으므로 직접 ReportData로 변환
                    print(f"[DEBUG] ReportData 객체 생성 시도...")
                    report_data = ReportData.model_validate(json_data)
                    print(f"[DEBUG] ReportData 객체 생성 완료")
                
                # 인쇄 최적화 보고서 렌더링
                print(f"[DEBUG] 보고서 렌더링 시도...")
                result = render_print_optimized_report(report_data, report_type)
                print(f"[DEBUG] 보고서 렌더링 완료")
                return result
                
            except Exception as e:
                print(f"[ERROR] 보고서 생성 중 오류: {str(e)}")
                import traceback
                traceback.print_exc()
                return html.Div([
                    html.H3("보고서 생성 중 오류가 발생했습니다"),
                    html.P(f"오류 메시지: {str(e)}"),
                    html.P(f"후보자 ID: {candidate_id if 'candidate_id' in locals() else 'N/A'}"),
                    html.P(f"보고서 타입: {report_type if 'report_type' in locals() else 'N/A'}")
                ])
        
        else:
            # 메인 애플리케이션 페이지
            return render_main_layout()

    @app.callback(
        Output("tab-content", "children"), 
        Input("main-tabs", "value")
    )
    def render_tab(tab: str):
        """탭 전환 시 해당 탭의 내용을 렌더링합니다."""
        from ..ui_llm_input import render_llm_input_tab
        from ..ui_report import render_report_tab
        from ..ui_settings import render_settings_tab
        from ..dash_prompt_generator import render_dash_prompt_generator
        
        if tab == "tab-prompt":
            return render_dash_prompt_generator()
        elif tab == "tab-result":
            return render_llm_input_tab()
        elif tab == "tab-report":
            return render_report_tab()
        elif tab == "tab-settings":
            return render_settings_tab()
        else:
            return html.Div("알 수 없는 탭입니다.") 