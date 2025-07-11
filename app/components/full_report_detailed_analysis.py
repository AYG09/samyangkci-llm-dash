from dash import html
import dash_bootstrap_components as dbc  # type: ignore
from typing import List
from app.report_schema import AnalysisItem


def create_detailed_analysis_section(items: List[AnalysisItem]) -> html.Div:
    """
    세부 역량 분석 섹션을 이미지와 같이 간결한 텍스트 리스트 형태로 생성합니다.
    """
    if not items:
        return html.Div(dbc.Alert("세부 분석 항목이 없습니다.", color="warning"))

    analysis_item_components: List[html.Div] = []
    for i, item in enumerate(items):
        # 'SIMULATION' 카테고리는 최종 보고서에 표시하지 않음
        if item.category == 'SIMULATION':
            continue

        item_component = html.Div(
            [
                html.H5(f"{i+1}. {item.title}", className="item-title-simple"),
                html.P(f"{item.score:.1f}", className="item-score-simple"),
                html.P(item.analysis, className="item-analysis-simple"),
                html.P(
                    [
                        html.Span("“", className="quote-icon"),
                        html.Strong(" 근거: "),
                        html.Span(item.evidence),
                    ],
                    className="item-evidence-simple",
                ),
            ],
            className="analysis-item-simple-container",
        )
        analysis_item_components.append(item_component)

    return html.Div(
        [
            html.H2("세부 역량 분석", className="section-title"),
            html.Div(analysis_item_components),
        ],
        className="light-section-container",
    ) 