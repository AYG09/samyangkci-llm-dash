from dash import html, dcc
import dash_bootstrap_components as dbc


def render_llm_input_tab():
    return dbc.Container([
        html.H2("LLM 분석 결과 입력", className="mb-4"),

        # 1단계: LLM 원문 입력
        dbc.Card([
            dbc.CardHeader("1단계: LLM 분석 결과 원문 붙여넣기"),
            dbc.CardBody([
                dcc.Textarea(
                    id="llm-result-input",
                    placeholder="LLM으로부터 받은 분석 결과를 여기에 그대로 붙여넣으세요.",
                    className="prompt-textarea form-control",
                    style={"height": "300px"}
                ),
                dbc.Button(
                    "분석 시작",
                    id="start-analysis-btn",
                    n_clicks=0,
                    className="btn-primary mt-3 w-100"
                )
            ])
        ]),

        # 2단계: 분석 결과 확인 및 수정 (처음에는 숨겨짐)
        html.Div(
            id="analysis-confirmation-section",
            className="mt-4",
            style={'display': 'none'},
            children=[
                dbc.Card([
                    dbc.CardHeader("2단계: 추출된 정보 확인 및 저장"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("이름", html_for="llm-name-input"),
                                dcc.Input(id="llm-name-input", className="form-control"),
                            ], md=6),
                            dbc.Col([
                                dbc.Label("지원조직", html_for="llm-org-input"),
                                dcc.Input(id="llm-org-input", className="form-control"),
                            ], md=6),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("지원직급", html_for="llm-position-input"),
                                dcc.Input(id="llm-position-input", className="form-control"),
                            ], md=6),
                            dbc.Col([
                                dbc.Label("면접일", html_for="llm-date-input"),
                                dcc.Input(id="llm-date-input", className="form-control"),
                            ], md=6),
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "수정",
                                    id="edit-analysis-btn",
                                    n_clicks=0,
                                    className="btn-secondary w-100"
                                ),
                            ]),
                            dbc.Col([
                                dbc.Button(
                                    "최종 저장",
                                    id="final-save-btn",
                                    n_clicks=0,
                                    className="btn-primary w-100"
                                ),
                            ]),
                        ]),
                    ])
                ])
            ]
        ),
        html.Div(id="llm-save-msg", className="save-message mt-3")

    ], className="page-container")
