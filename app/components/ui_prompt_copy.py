import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def CopyButton(prompt: str, button_id: str = "copy-btn"):
    return html.Div([
        dbc.Alert("복사 버튼 최신 코드가 반영되고 있습니다.", color="warning", style={"marginBottom": "16px"}),
        dcc.Textarea(
            value=prompt,
            style={
                "width": "100%", "minHeight": "120px", "fontFamily": "monospace",
                "fontSize": "16px", "marginBottom": "12px", "background": "#f8f9fa"
            },
            readOnly=True,
        ),
        html.Div([
            html.Button(
                ["📋 프롬프트 복사하기"],
                id=button_id,
                n_clicks=0,
                style={
                    "width": "100%",
                    "padding": "22px 32px",
                    "background": "linear-gradient(90deg, #24278B 70%, #3a3e9e 100%)",
                    "color": "#fff",
                    "border": "none",
                    "borderRadius": "18px",
                    "fontSize": "22px",
                    "fontWeight": "900",
                    "letterSpacing": "-0.5px",
                    "cursor": "pointer",
                    "boxShadow": "0 10px 32px rgba(36,39,139,0.18)",
                    "transition": "all 0.3s cubic-bezier(.4,0,.2,1)",
                    "fontFamily": "Pretendard, Noto Sans KR, Malgun Gothic, sans-serif",
                },
            ),
            dcc.Clipboard(
                target_id=button_id,
                style={"display": "none"},
                id=f"{button_id}-clipboard"
            ),
            html.Div(id=f"{button_id}-feedback", style={"marginTop": "12px", "textAlign": "center"})
        ], style={"textAlign": "center", "margin": "32px 0 40px 0"})
    ])

# 사용 예시 및 콜백은 app.py에서 등록 필요
# @callback(
#     Output("copy-btn-feedback", "children"),
#     Input("copy-btn", "n_clicks"),
#     prevent_initial_call=True
# )
# def update_feedback(n_clicks):
#     if n_clicks:
#         return html.Span("✅ 복사 완료!", style={"color": "#1a1d5c", "fontWeight": "bold", "fontSize": "20px"})
#     return ""
