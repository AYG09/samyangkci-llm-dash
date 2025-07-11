from dash import html
import dash_bootstrap_components as dbc

BRAND_BLUE = "#005BAC"
BRAND_GREEN = "#00B894"
BRAND_RED = "#d63031"
CARD_STYLE = {"marginBottom": "18px", "boxShadow": "0 2px 8px #005BAC22", "borderRadius": "12px"}

# 임원용 INSIGHT, HR담당자 포인트 카드 시각화

def render_insight_cards(json_data: dict):
    insights = json_data.get("임원용_INSIGHT", [])
    hr_points = json_data.get("HR담당자_포인트", [])
    def make_card(title, items, color):
        if not items:
            return None
        return dbc.Card([
            dbc.CardHeader(title, style={"fontWeight": 700, "fontSize": "1.08rem", "color": color}),
            dbc.CardBody([
                html.Ul([
                    html.Li([
                        html.B(f"{item.get('title', '-')}", style={"fontSize": "1.01rem"}),
                        html.Div(item.get("analysis", "-"), style={"fontSize": "0.99rem", "marginTop": "2px"}),
                        html.Div(f"근거: {item.get('evidence', '-')} (신뢰도: {item.get('reliability', '-')})", style={"fontSize": "0.95rem", "color": "#888"})
                    ]) for item in items
                ])
            ])
        ], style=CARD_STYLE)
    cards = [
        make_card("임원용 INSIGHT", insights, BRAND_BLUE),
        make_card("HR담당자 포인트", hr_points, BRAND_GREEN)
    ]
    cards = [c for c in cards if c]
    if not cards:
        return dbc.Alert("임원/HR 인사이트 데이터가 부족합니다.", color="warning")
    return html.Div(cards, style={"display": "flex", "gap": "32px", "marginBottom": "32px"})
