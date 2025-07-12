"""페이지 라우팅 관련 콜백 함수들"""

import dash
from dash import Output, Input, html, Dash
from typing import Any


def render_main_layout():
    """메인 애플리케이션 레이아웃을 렌더링합니다."""
    from dash import dcc
    import dash_bootstrap_components as dbc
    
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
                                    style={
                                        "fontSize": "1.5rem", 
                                        "marginRight": "8px"
                                    },
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
                dcc.Tab(label="📖 가이드", value="tab-guide"),
            ],
            id="main-tabs",
            value="tab-report",
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


def register_routing_callbacks(app: Dash):
    """페이지 라우팅 관련 콜백들을 앱에 등록합니다."""
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname: str) -> html.Div:
        """URL 경로에 따라 페이지를 렌더링합니다."""
        if pathname and pathname.startswith('/print-report/'):
            try:
                import urllib.parse
                parts = pathname.split('/')
                candidate_id = urllib.parse.unquote(parts[2])
                report_type = parts[3]
                
                from ..components.print_optimized_reports import (
                    render_print_optimized_report
                )
                from ..report_schema import ReportData
                from ..utils import try_parse_json
                from ..db import get_candidate_by_id
                
                candidate = get_candidate_by_id(candidate_id)
                if not candidate:
                    return html.Div(f"후보자를 찾을 수 없습니다. (ID: {candidate_id})")
                
                evaluator_data = candidate.get('evaluator', '{}')
                json_data = try_parse_json(evaluator_data)
                
                if json_data is None:
                    try:
                        from ..llm_report_parser import parse_llm_report
                        report_data = parse_llm_report(evaluator_data)
                    except Exception as e:
                        error_detail = (
                            "분석 데이터를 읽을 수 없습니다. "
                            f"Error: {e}, Data: {evaluator_data[:100]}..."
                        )
                        return html.Div(error_detail)
                else:
                    report_data = ReportData.model_validate(json_data)
                
                return render_print_optimized_report(report_data, report_type)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                
                cid = locals().get('candidate_id', 'N/A')
                rtype = locals().get('report_type', 'N/A')
                
                return html.Div([
                    html.H3("보고서 생성 중 오류가 발생했습니다"),
                    html.P(f"오류 메시지: {str(e)}"),
                    html.P(f"후보자 ID: {cid}"),
                    html.P(f"보고서 타입: {rtype}")
                ])
        
        else:
            return render_main_layout()

    @app.callback(
        Output("tab-content", "children"), 
        [
            Input("main-tabs", "value"),
            Input("save-signal-store", "data")
        ]
    )
    def render_tab(tab: str, save_signal: bool | None) -> html.Div:
        """탭 전환 시 해당 탭의 내용을 렌더링합니다."""
        from ..ui_llm_input import render_llm_input_tab
        from ..ui_report import render_report_tab
        from ..dash_prompt_guide import render_guide_tab
        from ..dash_prompt_generator import render_dash_prompt_generator
        
        ctx = dash.callback_context
        if not ctx.triggered:
            return render_report_tab()
            
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == 'save-signal-store' and save_signal:
            return render_report_tab()

        if tab == "tab-prompt":
            return render_dash_prompt_generator()
        elif tab == "tab-result":
            return render_llm_input_tab()
        elif tab == "tab-report":
            return render_report_tab()
        elif tab == "tab-guide":
            return render_guide_tab()
        else:
            return render_report_tab() 