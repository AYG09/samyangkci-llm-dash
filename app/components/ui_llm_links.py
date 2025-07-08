from dash import html
import dash_bootstrap_components as dbc

llm_services = [
    {
        "name": "© ChatGPT",
        "url": "https://chat.openai.com",
        "color": "linear-gradient(90deg,#6ec2b6 70%,#74aa9c 100%)",
        "caption": "💡 GPT-4o 또는 GPT-4를 선택하여 분석하세요",
        "fontSize": 20
    },
    {
        "name": "💎 Gemini",
        "url": "https://gemini.google.com",
        "color": "linear-gradient(90deg,#4285f4 70%,#3a3e9e 100%)",
        "caption": "💡 Gemini Pro 모델을 사용하세요",
        "fontSize": 20
    },
    {
        "name": "🧠 Copilot",
        "url": "https://copilot.microsoft.com",
        "color": "linear-gradient(90deg,#24278B 70%,#3a3e9e 100%)",
        "caption": "💡 GPT-4 모드로 설정하여 사용하세요",
        "fontSize": 20
    },
]

other_services = [
    {
        "name": "🔎 Claude",
        "url": "https://claude.ai",
        "color": "linear-gradient(90deg,#d97757 70%,#eab08a 100%)",
        "caption": "💡 Claude 3.5 Sonnet 모델 추천",
        "fontSize": 18
    },
    {
        "name": "⚡ Perplexity",
        "url": "https://www.perplexity.ai",
        "color": "linear-gradient(90deg,#1fb6d3 70%,#6ec2b6 100%)",
        "caption": "💡 Pro 모드에서 GPT-4 선택",
        "fontSize": 18
    },
]

def LLMLinks():
    return html.Div([
        html.H3("🚀 LLM 서비스 바로가기", style={"marginBottom": "8px"}),
        html.Div("위의 프롬프트를 복사한 후 아래 LLM 서비스에서 분석을 진행하세요:", style={
            "fontSize": "1.13rem", "color": "#24278B", "fontWeight": 600, "letterSpacing": "-0.2px", "marginBottom": "18px"
        }),
        dbc.Row([
            dbc.Col([
                html.A([
                    html.Button(
                        svc["name"],
                        style={
                            "width": "100%", "padding": "18px 0", "background": svc["color"], "color": "white",
                            "border": "none", "borderRadius": "12px", "fontSize": svc["fontSize"], "fontWeight": 700,
                            "letterSpacing": "-0.5px", "boxShadow": f"0 4px 16px {svc['color'].split('(')[-1].split()[0]}33", "cursor": "pointer"
                        }
                    )
                ], href=svc["url"], target="_blank"),
                html.Div(svc["caption"], style={"fontSize": "0.98rem", "color": "#666", "marginTop": "4px"})
            ], width=4) for svc in llm_services
        ], style={"marginBottom": "18px"}),
        html.Hr(),
        html.Div("기타 LLM 서비스:", style={"fontSize": "1.08rem", "color": "#24278B", "fontWeight": 500, "marginBottom": "10px"}),
        dbc.Row([
            dbc.Col([
                html.A([
                    html.Button(
                        svc["name"],
                        style={
                            "width": "100%", "padding": "16px 0", "background": svc["color"], "color": "white",
                            "border": "none", "borderRadius": "12px", "fontSize": svc["fontSize"], "fontWeight": 700,
                            "letterSpacing": "-0.5px", "boxShadow": f"0 4px 12px {svc['color'].split('(')[-1].split()[0]}33", "cursor": "pointer"
                        }
                    )
                ], href=svc["url"], target="_blank"),
                html.Div(svc["caption"], style={"fontSize": "0.95rem", "color": "#666", "marginTop": "4px"})
            ], width=6) for svc in other_services
        ])
    ])
