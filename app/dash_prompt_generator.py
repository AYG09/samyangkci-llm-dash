from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc

def render_dash_prompt_generator():
    return html.Div([
        html.H4('면접자 정보 입력', style={"fontWeight":700, "marginBottom":"18px"}),
        # 업로드 자료 선택 영역
        html.Div([
            html.Label('업로드할 자료 내역을 선택하세요 (복수 선택 가능)', style={"fontWeight":600, "fontSize":"1.07rem", "marginBottom":"10px", "display": "block"}),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.Checkbox(id=f'prompt-upload-materials-{i}', value=False, style={"marginRight": "8px"}),
                        html.Span(label, style={"fontWeight": 500, "fontSize": "1.04rem", "wordBreak": "keep-all", "whiteSpace": "pre-line"})
                    ], width=3, style={"display": "flex", "alignItems": "center", "gap": "6px", "marginBottom": "10px"})
                    for i, label in enumerate([
                        "이력서",
                        "면접평가표(1차)", "면접평가표(2차)", "면접평가표(3차)",
                        "면접 녹취록(1차)", "면접 녹취록(2차)", "면접 녹취록(3차)",
                        "포트폴리오", "평판보고서", "BIG5 성격유형검사표", "인성검사표"
                    ])
                ], justify="start", style={"flexWrap": "wrap", "rowGap": "0", "marginBottom": "0"})
            ], style={"width": "100%", "margin": "0 auto", "display": "flex", "flexWrap": "wrap"}),
            html.Div([
                dbc.Label('기타(직접 입력)', html_for='prompt-upload-materials-etc', style={"fontWeight":600, "marginTop":"2px"}),
                dbc.Input(id='prompt-upload-materials-etc', placeholder='예: 추가 자료명 입력', type='text', style={"marginBottom":"8px", "width":"320px"}),
            ], style={"marginBottom": "12px"})
        ], style={"marginBottom": "18px", "padding": "16px 18px 10px 18px", "background": "#F8FAFF", "borderRadius": "12px", "boxShadow": "0 2px 8px #005BAC11", "maxWidth": "900px", "marginLeft": "auto", "marginRight": "auto"}),
        dbc.Row([
            dbc.Col([
                dbc.Label('이름', html_for='prompt-candidate-name-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-name-input', placeholder='예: 홍길동', type='text', style={"marginBottom":"8px"}),
            ], md=4),
            dbc.Col([
                dbc.Label('지원조직', html_for='prompt-candidate-org-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-org-input', placeholder='예: 삼양KCI', type='text', style={"marginBottom":"8px"}),
            ], md=4),
            dbc.Col([
                dbc.Label('지원직급', html_for='prompt-candidate-position-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-position-input', placeholder='예: 팀장', type='text', style={"marginBottom":"8px"}),
            ], md=4),
        ], style={"marginBottom":"8px"}),
        dbc.Row([
            dbc.Col([
                dbc.Label('면접일', html_for='prompt-candidate-date-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-date-input', placeholder='예: 20250708, 25-07-08 등 자유입력', type='text', style={"marginBottom":"8px"}),
            ], md=4),
            dbc.Col([
                dbc.Label('연봉(만원)', html_for='prompt-candidate-salary-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-salary-input', placeholder='예: 6000', type='text', style={"marginBottom":"8px"}),
            ], md=4),
            dbc.Col([
                dbc.Label('경력(년)', html_for='prompt-candidate-career-input', style={"fontWeight":600}),
                dbc.Input(id='prompt-candidate-career-input', placeholder='예: 10', type='text', style={"marginBottom":"8px"}),
            ], md=4),
        ], style={"marginBottom":"8px"}),
        html.Div([
            dbc.Button('프롬프트 생성', id='prompt-generate-prompt-btn', color='primary', style={"fontWeight":700, "fontSize":"1.08rem", "padding":"12px 0", "width":"100%", "marginBottom":"18px", "borderRadius":"12px"}),
            html.Span(id='prompt-warning-message', style={'color': '#d63031', 'marginLeft': '8px', 'fontWeight': 600})
        ]),
        html.Div([
            dcc.Textarea(id='prompt-generated-prompt-area', value='', style={'width': '100%', 'height': 220, 'fontFamily': 'monospace', 'marginBottom': '18px', 'borderRadius':'10px'}, readOnly=True),
        ], id='prompt-generated-prompt-area-wrapper'),
        html.Div([
            dbc.Button('📋 프롬프트 복사', id='copy-btn', n_clicks=0, color='info', style={
                "width": "100%", "fontWeight": 700, "fontSize": "1.12rem", "padding": "16px 0", "marginBottom": "24px", "borderRadius": "12px", "boxShadow": "0 2px 12px #005BAC22"
            }, title="프롬프트 복사"),
            html.Span(id='copy-success-msg', style={'marginLeft': '18px', 'color': '#0984e3', 'fontWeight': 600, 'fontSize': '1.01rem'})
        ]),
        html.Hr(style={"margin":"32px 0 18px 0"}),
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button('GPT-4', href='https://chat.openai.com/', color='light', outline=True, target='_blank', style={
                        "background": "#10A37F", "color": "#fff", "fontWeight": 700, "fontSize": "1.08rem", "padding": "16px 0", "width": "100%", "borderRadius": "10px", "boxShadow": "0 2px 8px #10A37F22"
                    }),
                ], md=2),
                dbc.Col([
                    dbc.Button('Gemini', href='https://gemini.google.com/', color='light', outline=True, target='_blank', style={
                        "background": "#4285F4", "color": "#fff", "fontWeight": 700, "fontSize": "1.08rem", "padding": "16px 0", "width": "100%", "borderRadius": "10px", "boxShadow": "0 2px 8px #4285F422"
                    }),
                ], md=2),
                dbc.Col([
                    dbc.Button('Claude 3', href='https://claude.ai/', color='light', outline=True, target='_blank', style={
                        # Claude 브랜드 주황색
                        "background": "#E37A47", "color": "#fff", "fontWeight": 700, "fontSize": "1.08rem", "padding": "16px 0", "width": "100%", "borderRadius": "10px", "boxShadow": "0 2px 8px #E37A4722"
                    }),
                ], md=2),
                dbc.Col([
                    dbc.Button('Bing Copilot', href='https://copilot.microsoft.com/', color='light', outline=True, target='_blank', style={
                        "background": "#0078D4", "color": "#fff", "fontWeight": 700, "fontSize": "1.08rem", "padding": "16px 0", "width": "100%", "borderRadius": "10px", "boxShadow": "0 2px 8px #0078D422"
                    }),
                ], md=2),
                dbc.Col([
                    dbc.Button('Perplexity', href='https://www.perplexity.ai/', color='light', outline=True, target='_blank', style={
                        "background": "#6C47FF", "color": "#fff", "fontWeight": 700, "fontSize": "1.08rem", "padding": "16px 0", "width": "100%", "borderRadius": "10px", "boxShadow": "0 2px 8px #6C47FF22"
                    }),
                ], md=2),
                dbc.Col([], md=2),
            ], style={"marginTop": "0", "marginBottom": "0", "gap": "18px", "justifyContent": "center"}),
        ], style={"width": "100%", "margin": "0 auto", "marginBottom": "0"}),
    ], className="card section-card", style={"background": "#F8FAFF", "boxShadow": "0 2px 16px #005BAC11", "borderRadius": "18px", "padding": "32px 28px 24px 28px", "marginTop": "18px", "minHeight": "480px"})
