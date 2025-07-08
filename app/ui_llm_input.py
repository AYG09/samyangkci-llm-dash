# 복사본: render_llm_input_tab 함수
from dash import html, dcc

def llm_result_input():
    return html.Div([
        html.Label("LLM 분석 결과", htmlFor="llm-result-input", style={"fontWeight": 600, "marginBottom": "6px"}),
        dcc.Textarea(
            id="llm-result-input",
            style={
                "width": "100%",
                "height": "120px",
                "resize": "vertical",
                "marginBottom": "22px",
                "background": "#F8FAFF",
                "borderRadius": "8px",
                "border": "1.5px solid #E0E4EA",
                "padding": "12px",
                "fontSize": "1.05rem"
            },
            placeholder="LLM 분석 결과를 입력하세요."
        ),
    ])

def evaluator_input():
    return html.Div([
        html.Label("평가자 이름", htmlFor="llm-evaluator-input", style={"fontWeight": 600, "marginBottom": "6px"}),
        dcc.Input(
            id="llm-evaluator-input",
            type="text",
            placeholder="예: 홍길동",
            style={
                "width": "100%",
                "background": "#F8FAFF",
                "borderRadius": "8px",
                "border": "1.5px solid #E0E4EA",
                "padding": "8px",
                "fontSize": "1.05rem"
            }
        ),
        html.Button(
            "저장",
            id="llm-save-btn",
            n_clicks=0,
            className="btn btn-primary",
            style={
                "width": "100%",
                "marginTop": "10px",
                "fontWeight": 600,
                "fontSize": "1.05rem"
            }
        ),
    ], style={"flex": 1, "marginRight": "18px", "display": "flex", "flexDirection": "column"})

def date_input():
    return html.Div([
        html.Label("입력 날짜", htmlFor="llm-date-input", style={"fontWeight": 600, "marginBottom": "6px"}),
        dcc.Input(
            id="llm-date-input",
            type="text",
            placeholder="예: 2025-07-08, 25/07/08, 20250708 등 자유입력",
            style={
                "width": "100%",
                "background": "#F8FAFF",
                "borderRadius": "8px",
                "border": "1.5px solid #E0E4EA",
                "padding": "8px",
                "fontSize": "1.05rem"
            }
        ),
        html.Button(
            "초기화",
            id="llm-reset-btn",
            n_clicks=0,
            className="btn btn-secondary",
            style={
                "width": "100%",
                "marginTop": "10px",
                "fontWeight": 600,
                "fontSize": "1.05rem"
            }
        ),
    ], style={"flex": 1, "display": "flex", "flexDirection": "column"})

def render_llm_input_tab():
    return html.Div([
        html.H3("LLM 분석 결과 입력", style={"fontWeight": 700, "fontSize": "1.3rem", "marginBottom": "18px", "color": "#1A237E"}),
        html.Div([
            html.Div([
                html.Label("이름", htmlFor="llm-name-input", style={"fontWeight": 600, "marginBottom": "6px"}),
                dcc.Input(
                    id="llm-name-input",
                    type="text",
                    placeholder="예: 홍길동",
                    style={
                        "width": "100%",
                        "background": "#F8FAFF",
                        "borderRadius": "8px",
                        "border": "1.5px solid #E0E4EA",
                        "padding": "8px",
                        "fontSize": "1.05rem",
                        "marginBottom": "18px"
                    }
                ),
            ], style={"marginBottom": "12px"}),
            llm_result_input(),
            html.Div([
                evaluator_input(),
                date_input()
            ], style={"display": "flex", "flexDirection": "row", "gap": "0", "marginBottom": "18px"}),
            html.Div([
                html.Span(id="llm-save-msg", style={"marginLeft": "4px", "color": "#0984e3", "fontWeight": 600, "fontSize": "1.08rem"})
            ], style={"marginTop": "8px", "display": "flex", "alignItems": "center"})
        ], className="llm-input-form", style={"background": "#fff", "borderRadius": "12px", "boxShadow": "0 2px 12px #005BAC11", "padding": "32px 28px 24px 28px", "width": "100%", "maxWidth": "900px"})
    ], style={"marginTop": "18px", "display": "flex", "justifyContent": "center", "width": "100%"})
