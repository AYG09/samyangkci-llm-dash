from dash import html
import dash_bootstrap_components as dbc

BRAND_BLUE = "#005BAC"
CARD_STYLE = {"marginBottom": "18px", "boxShadow": "0 2px 8px #005BAC22", "borderRadius": "12px"}
CARD_BODY_STYLE = {"padding": "12px 10px 10px 10px"}

def render_profile_card(info: dict):
    return dbc.Card([
        dbc.CardBody([
            html.H3(info.get("이름", "-"), style={"fontWeight": 800, "fontSize": "1.25rem", "color": BRAND_BLUE}),
            html.Div(f"지원조직: {info.get('지원조직', '-')}", style={"fontSize": "1.05rem", "color": "#333"}),
            html.Div(f"지원직급: {info.get('지원직급', '-')}", style={"fontSize": "1.05rem", "color": "#333"}),
            html.Div(f"경력: {info.get('경력', '-')}", style={"fontSize": "1.01rem", "color": "#555"}),
            html.Div(f"희망연봉: {info.get('희망연봉', '-')}", style={"fontSize": "1.01rem", "color": "#555"}),
            html.Div(f"지원일자: {info.get('지원일자', '-')}", style={"fontSize": "0.98rem", "color": "#888"}),
        ], style=CARD_BODY_STYLE)
    ], style={**CARD_STYLE, "marginBottom": "18px"})
