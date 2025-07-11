from dash import html
import dash_bootstrap_components as dbc
from typing import List
from ..report_schema import AnalysisItem

def create_detailed_analysis_section(items: List[AnalysisItem]) -> html.Div:
    """
    세부 역량 분석 섹션을 테이블 형태로 생성합니다.
    """
    if not items:
        return html.Div(dbc.Alert("세부 분석 항목이 없습니다.", color="warning"), className="p-4")

    table_header = [
        html.Thead(html.Tr([
            html.Th("Category"),
            html.Th("Analysis Title"),
            html.Th("Analysis & Evidence"),
            html.Th("Score"),
        ]))
    ]

    table_body = []
    for item in items:
        score_badge = dbc.Badge(f"{item.score:.1f}", color="primary", pill=True, className="ms-1")
        row = html.Tr([
            html.Td(dbc.Badge(item.category, color="secondary")),
            html.Td(html.Strong(item.title)),
            html.Td([
                html.P(item.analysis),
                html.Small(f"근거: {item.evidence}", className="text-muted")
            ]),
            html.Td(score_badge, className="text-center"),
        ])
        table_body.append(row)

    return html.Div(
        [
            html.H3("세부 역량 분석", className="mb-3"),
            dbc.Table(table_header + [html.Tbody(table_body)], bordered=True, hover=True, responsive=True, striped=True),
        ],
        className="detailed-analysis-section p-4 mb-4",
    ) 