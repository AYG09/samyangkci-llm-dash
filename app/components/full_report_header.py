from dash import html
import dash_bootstrap_components as dbc
from ..report_schema import CandidateInfo


def create_info_card(icon_class: str, title: str, content: str) -> dbc.Col:
    """Helper function to create a small info card with an icon."""
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            html.I(className=f"{icon_class} h3"),
                            width="auto",
                            className="d-flex align-items-center",
                        ),
                        dbc.Col(
                            [
                                html.Strong(f"{title}: ", className="info-card-title"),
                                html.Span(content, className="info-card-content"),
                            ]
                        ),
                    ],
                    className="g-2",
                )
            ),
            className="info-card h-100",
        ),
        lg=4,
        md=12,
        className="mb-3 mb-lg-0",
    )


def create_full_report_header(candidate_info: CandidateInfo) -> html.Div:
    """
    상세 보고서의 헤더 섹션을 새로운 디자인으로 생성합니다.
    """
    return html.Div(
        [
            # Main Title Section
            html.Div(
                [
                    html.H1("종합 분석 리포트", className="report-main-title"),
                    html.P(
                        "CONFIDENTIAL | COMPREHENSIVE ANALYSIS",
                        className="report-confidential",
                    ),
                ],
                className="report-title-section",
            ),
            # Candidate Info Section
            html.Div(
                [
                    html.H2(candidate_info.name, className="candidate-name"),
                    html.P(
                        f"지원 직무: {candidate_info.position}",
                        className="candidate-position",
                    ),
                ],
                className="candidate-info-section",
            ),
            # Meta Info Section
            dbc.Row(
                [
                    create_info_card(
                        "bi bi-briefcase-fill", "경력", candidate_info.career_summary
                    ),
                    create_info_card(
                        "bi bi-calendar-event-fill",
                        "면접일",
                        candidate_info.interview_date,
                    ),
                    create_info_card(
                        "bi bi-cash-coin", "연봉 정보", candidate_info.salary_info
                    ),
                ],
                className="g-3 mt-3 justify-content-center",
            ),
        ],
        className="report-header-modern",
    ) 