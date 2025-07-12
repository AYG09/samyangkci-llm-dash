from dash import html
from typing import Any

def create_decision_points_section(decision_points: Any) -> html.Div:
    """
    종합 보고서용 '핵심 의사결정 포인트' 섹션을 생성합니다.
    """
    if not decision_points or (
        not decision_points.strengths and not decision_points.risks
    ):
        return html.Div()

    strengths_items = []
    if decision_points.strengths:
        for item in decision_points.strengths:
            strengths_items.append(
                html.Div([
                    html.H5(
                        item.title, className="decision-point-title text-primary"
                    ),
                    html.P(item.analysis, className="decision-point-analysis"),
                    html.P(
                        f"근거: {item.evidence}", 
                        className="decision-point-evidence text-muted"
                    ),
                ], className="decision-point-item mb-4")
            )

    risks_items = []
    if decision_points.risks:
        for item in decision_points.risks:
            risks_items.append(
                html.Div([
                    html.H5(
                        item.title, className="decision-point-title text-danger"
                    ),
                    html.P(item.analysis, className="decision-point-analysis"),
                    html.P(
                        f"근거: {item.evidence}", 
                        className="decision-point-evidence text-muted"
                    ),
                ], className="decision-point-item mb-4")
            )

    return html.Div([
        html.H2("III. 핵심 의사결정 포인트", className="report-main-section-title"),
        html.Div([
            html.Div([
                html.H4(
                    "👍 Strengths (강점 및 기회 요인)", 
                    className="decision-section-title"
                ),
                html.Div(
                    strengths_items if strengths_items 
                    else [html.P("분석된 강점이 없습니다.", className="text-muted")]
                )
            ], className="strengths-section"),
            
            html.Hr(className="my-5"),

            html.Div([
                html.H4(
                    "⚠️ Risks (리스크 및 우려 사항)", 
                    className="decision-section-title"
                ),
                html.Div(
                    risks_items if risks_items 
                    else [html.P("분석된 리스크가 없습니다.", className="text-muted")]
                )
            ], className="risks-section"),
        ])
    ], className="report-section-container") 