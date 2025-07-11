from dash import html
import dash_bootstrap_components as dbc
from typing import List
from ..report_schema import MaterialAnalysis


def create_custom_accordion(materials: List[MaterialAnalysis]) -> html.Div:
    """
    dbc.Card와 dbc.Collapse를 사용하여 커스텀 아코디언을 생성합니다.
    이렇게 하면 아코디언 제목이 사라지는 문제를 해결할 수 있습니다.
    """
    if not materials:
        return html.Div()

    cards = []
    for i, item in enumerate(materials):
        card = dbc.Card(
            [
                dbc.CardHeader(
                    html.Button(
                        [
                            html.Span(
                                item.material_name, 
                                className="accordion-btn-text"
                            ),
                            html.I(
                                className="bi bi-chevron-down accordion-arrow"
                            ),
                        ],
                        id={"type": "collapse-button", "index": i},
                        className="accordion-button collapsed",
                        n_clicks=0,
                    )
                ),
                dbc.Collapse(
                    dbc.CardBody(
                        [
                            html.H5("자료 요약", className="material-summary-title"),
                            html.Div(
                                item.summary, 
                                className="material-summary-text", 
                                style={'whiteSpace': 'pre-line'}
                            ),
                            html.Hr(className="my-4"),
                            html.H5(
                                "주요 분석 포인트", 
                                className="material-summary-title"
                            ),
                            html.Div(
                                item.analysis_points, 
                                className="material-insight-text", 
                                style={'whiteSpace': 'pre-line'}
                            ),
                        ]
                    ),
                    id={"type": "collapse", "index": i},
                    is_open=False,
                ),
            ],
            className="accordion-card",
        )
        cards.append(card)

    return html.Div(cards, className="custom-accordion")


def create_full_report_by_material(
    materials: List[MaterialAnalysis],
) -> html.Div:
    """
    자료별 분석 요약 섹션을 커스텀 아코디언 형태로 생성합니다.
    """
    return html.Div(
        [
            html.H2("II. 자료별 분석 요약", className="report-main-section-title"),
            create_custom_accordion(materials),
        ],
        className="report-section-container",
    )
