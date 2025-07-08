from dash import html, dcc
import dash_bootstrap_components as dbc
from app.components.prompt_templates import generate_custom_prompt, DEFAULT_PROMPT

def PromptGuide():
    return html.Div([
        # 1. 면접자 정보 입력 + 프롬프트 생성/복사 (최상단, 단일 카드)
        html.Div([
            html.Div([
                html.Span("👤 면접자 정보 입력", style={"fontWeight": 800, "fontSize": "1.18rem", "color": "#24278B"}),
                html.Br(),
                html.Span("(이름, 지원조직, 지원직급, 면접일자, 희망연봉, 경력)", style={"fontWeight": 500, "fontSize": "1.01rem", "color": "#6C5CE7", "letterSpacing": "-0.2px"})
            ], style={"lineHeight": "1.2", "marginBottom": "18px"}),
            dbc.Row([
                dbc.Col([
                    html.B("이름"),
                    dcc.Input(type="text", id="prompt-candidate-name-input", className="dash-input", placeholder="예: 홍길동", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
                dbc.Col([
                    html.B("지원 조직"),
                    dcc.Input(type="text", id="prompt-candidate-org-input", className="dash-input", placeholder="예: 전략기획팀", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
                dbc.Col([
                    html.B("지원 직급"),
                    dcc.Input(type="text", id="prompt-candidate-position-input", className="dash-input", placeholder="예: 팀장", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
            ], style={"marginBottom": "0"}),
            dbc.Row([
                dbc.Col([
                    html.B("면접 일자"),
                    dcc.Input(type="text", id="prompt-candidate-date-input", className="dash-input", placeholder="예: 2025-07-07", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
                dbc.Col([
                    html.B("희망 연봉(만원)"),
                    dcc.Input(type="number", id="prompt-candidate-salary-input", className="dash-input", placeholder="예: 7000", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
                dbc.Col([
                    html.B("경력(년수)"),
                    dcc.Input(type="number", id="prompt-candidate-career-input", className="dash-input", placeholder="예: 10", style={"width": "100%", "marginBottom": "12px"})
                ], md=4),
            ]),
            html.Div([
                dbc.Button("📝 프롬프트 생성", id="prompt-generate-prompt-btn", className="dash-button", n_clicks=0, style={"width": "100%", "margin": "22px 0 0 0", "fontSize": "1.08rem", "background": "linear-gradient(90deg, #24278B 70%, #3a3e9e 100%)"})
            ]),
            # 경고 메시지 영역
            html.Div(id="prompt-warning-message", style={"color": "#e74c3c", "fontWeight": 600, "marginTop": "12px", "minHeight": "24px", "fontSize": "1.01rem"}),
            dcc.Textarea(id="prompt-generated-prompt-area", className="dash-input", placeholder="여기에 생성된 프롬프트가 표시됩니다.", style={"width": "100%", "minHeight": "120px", "marginTop": "18px", "marginBottom": "0", "fontSize": "1.08rem", "background": "#f8f9fa"}, readOnly=True),
            html.Div([
                dbc.Button("📋 프롬프트 복사", id="prompt-copy-prompt-btn", className="dash-button", n_clicks=0, style={"width": "100%", "margin": "18px 0 0 0", "fontSize": "1.08rem", "background": "linear-gradient(90deg, #005BAC 70%, #3a3e9e 100%)"})
            ]),
            # 복사 성공 메시지
            html.Div(id="prompt-copy-success-message", style={"color": "#00B894", "fontWeight": 600, "marginTop": "10px", "minHeight": "20px", "fontSize": "1.01rem"}),
        ], className="card section-card", style={"background": "#fff", "boxShadow": "0 2px 16px #005BAC11", "borderRadius": "18px", "padding": "32px 28px 24px 28px", "marginTop": "18px", "marginBottom": "36px"}),
        # 2. 구분선
        html.Hr(style={"border": "none", "borderTop": "1.5px solid #e0e3f3", "margin": "0 0 32px 0"}),
        # 3. LLM 링크 (ChatGPT, Claude, Gemini, Perplexity, Bing Copilot)
        html.Div([
            html.Div([
                dbc.Button([html.Span("ChatGPT", style={"fontWeight": 700})], href="https://chat.openai.com/", external_link=True, target="_blank", rel="noopener noreferrer", className="llm-link-btn", id="llm-link-chatgpt", n_clicks=0, style={"width": "220px", "height": "80px", "borderRadius": "16px", "background": "linear-gradient(90deg, #005BAC 70%, #3a3e9e 100%)", "color": "#fff", "fontSize": "1.13rem", "marginRight": "0", "marginBottom": "0", "boxShadow": "0 4px 16px #005BAC22", "display": "flex", "alignItems": "center", "justifyContent": "center"}, title="ChatGPT 바로가기"),
                dbc.Button([html.Span("Claude", style={"fontWeight": 700})], href="https://claude.ai/", external_link=True, target="_blank", rel="noopener noreferrer", className="llm-link-btn", id="llm-link-claude", n_clicks=0, style={"width": "220px", "height": "80px", "borderRadius": "16px", "background": "linear-gradient(90deg, #00B894 70%, #00C9A7 100%)", "color": "#fff", "fontSize": "1.13rem", "marginRight": "0", "marginBottom": "0", "boxShadow": "0 4px 16px #00B89422", "display": "flex", "alignItems": "center", "justifyContent": "center"}, title="Claude 바로가기"),
                dbc.Button([html.Span("Gemini", style={"fontWeight": 700})], href="https://gemini.google.com/", external_link=True, target="_blank", rel="noopener noreferrer", className="llm-link-btn", id="llm-link-gemini", n_clicks=0, style={"width": "220px", "height": "80px", "borderRadius": "16px", "background": "linear-gradient(90deg, #6C5CE7 70%, #8e7cff 100%)", "color": "#fff", "fontSize": "1.13rem", "marginRight": "0", "marginBottom": "0", "boxShadow": "0 4px 16px #6C5CE722", "display": "flex", "alignItems": "center", "justifyContent": "center"}, title="Gemini 바로가기"),
                dbc.Button([html.Span("Perplexity", style={"fontWeight": 700})], href="https://www.perplexity.ai/", external_link=True, target="_blank", rel="noopener noreferrer", className="llm-link-btn", id="llm-link-perplexity", n_clicks=0, style={"width": "220px", "height": "80px", "borderRadius": "16px", "background": "linear-gradient(90deg, #6C47DC 70%, #00B8D9 100%)", "color": "#fff", "fontSize": "1.13rem", "marginRight": "0", "marginBottom": "0", "boxShadow": "0 4px 16px #6C47DC22", "display": "flex", "alignItems": "center", "justifyContent": "center"}, title="Perplexity 바로가기"),
                dbc.Button([html.Span("Bing Copilot", style={"fontWeight": 700})], href="https://copilot.microsoft.com/", external_link=True, target="_blank", rel="noopener noreferrer", className="llm-link-btn", id="llm-link-bingcopilot", n_clicks=0, style={"width": "220px", "height": "80px", "borderRadius": "16px", "background": "linear-gradient(90deg, #1A237E 70%, #00B8D9 100%)", "color": "#fff", "fontSize": "1.13rem", "marginRight": "0", "marginBottom": "0", "boxShadow": "0 4px 16px #1A237E22", "display": "flex", "alignItems": "center", "justifyContent": "center"}, title="Bing Copilot 바로가기"),
            ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between", "alignItems": "center", "gap": "24px", "width": "100%", "minHeight": "80px", "padding": "8px 0"})
        ], className="card section-card", style={"background": "#fff", "boxShadow": "0 2px 16px #005BAC11", "borderRadius": "18px", "padding": "32px 28px 24px 28px", "marginTop": "0", "marginBottom": "24px", "width": "100%"})
    ])
