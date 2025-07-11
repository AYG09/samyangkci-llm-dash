from dash import html
import dash_bootstrap_components as dbc
from ..report_schema import ReportData

def render_hr_report(report_data: ReportData) -> html.Div:
    """
    HR 담당자용 보고서 UI를 생성합니다.
    """
    if not isinstance(report_data, ReportData):
        return html.Div("보고서 데이터가 올바른 형식이 아닙니다.", className="report-container")

    hr_points = report_data.hr_points
    info = report_data.candidate_info

    point_cards = []
    for point in hr_points:
        card = dbc.Card(
            dbc.CardBody([
                html.H5(point.title, className="card-title"),
                html.P(point.analysis, className="card-text"),
                html.Small(f"근거: {point.evidence}", className="text-muted"),
            ]),
            className="mb-3 h-100" # h-100 for equal height cards
        )
        point_cards.append(dbc.Col(card, md=6))


    return html.Div(
        [
            # 보고서 헤더
            html.Div([
                html.H1("HR Action Plan: Candidate Assessment"),
                html.H2(f"{info.name} - {info.position}"),
                html.Hr(),
            ], className="report-header-hr mb-4"),
            
            dbc.Row(point_cards),
        ],
        className="report-container-hr p-4",
        style={"backgroundColor": "#fff", "fontFamily": "'Pretendard', sans-serif"}
    )
