import dash_bootstrap_components as dbc
from dash import html

BRAND_PURPLE = "#6C5CE7"
CARD_STYLE = {"marginBottom": "18px", "boxShadow": "0 2px 8px #6C5CE722", "borderRadius": "12px"}

# 내러티브 분석(동기/역량/리스크 등) 카드 렌더링

def render_narrative_analysis(json_data: dict):
    # 영역별 키워드 정의
    sections = [
        ("동기", ["동기", "의욕", "몰입"]),
        ("역량", ["역량", "능력", "강점"]),
        ("리스크", ["리스크", "위험", "주의", "한계"]),
        ("성장", ["성장", "잠재력"]),
        ("조직적합", ["적합", "조직"]),
    ]
    cards = []
    for section, keywords in sections:
        items = [
            x for x in json_data.get("분석항목", [])
            if isinstance(x, dict) and any(
                k in x.get("title", "") or k in x.get("analysis", "") for k in keywords
            )
        ]
        if not items:
            continue
        cards.append(
            dbc.Card([
                dbc.CardHeader(section, style={"fontWeight": 700, "fontSize": "1.08rem", "color": BRAND_PURPLE}),
                dbc.CardBody([
                    html.Ul([
                        html.Li([
                            html.B(item.get("title", "-"), style={"fontSize": "1.01rem"}),
                            html.Div(item.get("analysis", "-"), style={"fontSize": "0.99rem", "marginTop": "2px"})
                        ]) for item in items
                    ])
                ])
            ], style=CARD_STYLE)
        )
    if not cards:
        return dbc.Alert("내러티브 분석 데이터가 부족합니다.", color="warning")
    return html.Div(cards, style={"marginBottom": "24px"})
