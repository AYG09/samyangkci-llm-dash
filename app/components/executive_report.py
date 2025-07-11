from dash import html
import dash_bootstrap_components as dbc
from ..report_schema import ReportData
from .executive_graphs import create_executive_summary_charts

def render_executive_report(report_data: ReportData) -> html.Div:
    """
    경영진 보고서 UI를 생성합니다.
    """
    if not isinstance(report_data, ReportData):
        return html.Div("보고서 데이터가 올바른 형식이 아닙니다.", className="report-container")

    insights = report_data.executive_insights
    info = report_data.candidate_info
    
    # 주요 Insight를 카드로 표시
    insight_cards = []
    for insight in insights:
        card = dbc.Card(
            dbc.CardBody([
                html.H5(insight.title, className="card-title"),
                html.P(insight.analysis, className="card-text"),
                html.Small(f"근거: {insight.evidence}", className="text-muted"),
            ]),
            className="mb-3",
        )
        insight_cards.append(card)

    return html.Div(
        [
            # 보고서 헤더
            html.Div([
                html.H1("Executive Briefing: Candidate Assessment"),
                html.H2(f"{info.name} - {info.position}"),
                html.Hr(),
            ], className="report-header-executive mb-4"),
            
            dbc.Row([
                # 좌측: 종합 차트
                dbc.Col(
                    create_executive_summary_charts(
                        report_data.comprehensive_report,
                        report_data.analysis_items
                    ), 
                    md=5
                ),
                # 우측: 주요 Insight
                dbc.Col(insight_cards, md=7),
            ]),
        ],
        className="report-container-executive p-4",
        style={"backgroundColor": "#fff", "fontFamily": "'Pretendard', sans-serif"}
    )
