import dash_bootstrap_components as dbc
from dash import html
from typing import List
from ..report_schema import MaterialAnalysis

BRAND_NAVY = "#1A237E"
CARD_STYLE = {"marginBottom": "18px", "boxShadow": "0 2px 8px #1A237E22", "borderRadius": "12px"}

# 자료별 분석(이력서, 평판, 인성검사 등) 카드 렌더링

def render_analysis_by_material(json_data: dict):
    # 자료별 키워드/분류 정의
    materials = [
        ("이력서", ["이력서", "경력"]),
        ("평판", ["평판", "추천"]),
        ("인성검사", ["인성", "성격", "Big5"]),
        ("면접", ["면접", "인터뷰"]),
    ]
    cards = []
    for mat, keywords in materials:
        items = [
            x for x in json_data.get("분석항목", [])
            if isinstance(x, dict) and any(
                k in x.get("title", "") or k in x.get("evidence", "") for k in keywords
            )
        ]
        if not items:
            continue
        cards.append(
            dbc.Card([
                dbc.CardHeader(mat, style={"fontWeight": 700, "fontSize": "1.08rem", "color": BRAND_NAVY}),
                dbc.CardBody([
                    html.Ul([
                        html.Li([
                            html.B(item.get("title", "-"), style={"fontSize": "1.01rem"}),
                            html.Div(item.get("analysis", "-"), style={"fontSize": "0.99rem", "marginTop": "2px"}),
                            html.Div(f"근거: {item.get('evidence', '-')}", style={"fontSize": "0.95rem", "color": "#888"})
                        ]) for item in items
                    ])
                ])
            ], style=CARD_STYLE)
        )
    if not cards:
        return dbc.Alert("자료별 분석 데이터가 부족합니다.", color="warning")
    return html.Div(cards, style={"marginBottom": "24px"})

def create_full_report_by_material(materials: List[MaterialAnalysis]) -> html.Div:
    """
    자료별 분석 요약 섹션을 아코디언 형태로 생성합니다.
    """
    if not materials:
        return html.Div()

    accordion_items = []
    for i, material in enumerate(materials):
        item = dbc.AccordionItem(
            [
                html.H6("자료 요약", className="mb-2"),
                html.P(material.summary),
                html.H6("주요 분석 포인트", className="mt-4 mb-2"),
                html.P(material.analysis_points),
            ],
            title=f"자료 {i+1}: {material.material_name}",
            item_id=f"material-item-{i}",
        )
        accordion_items.append(item)

    return html.Div(
        [
            html.H3("자료별 분석 요약", className="mb-3"),
            dbc.Accordion(accordion_items, start_collapsed=True, always_open=True),
        ],
        className="materials-section p-4 mb-4",
    )
