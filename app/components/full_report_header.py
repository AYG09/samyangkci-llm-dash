from dash import html
import dash_bootstrap_components as dbc
from ..report_schema import CandidateInfo

def create_full_report_header(candidate_info: CandidateInfo) -> html.Div:
    """
    상세 보고서의 헤더 섹션을 생성합니다.
    """
    return html.Div(
        [
            html.P("CONFIDENTIAL | COMPREHENSIVE ANALYSIS REPORT", className="report-confidential"),
            html.H1(f"상세 종합분석 리포트: {candidate_info.name}", className="report-main-title"),
            html.H2(f"지원 직무: {candidate_info.position}", className="report-sub-title"),
            html.Hr(className="my-4"),
            dbc.Row(
                [
                    dbc.Col(f"경력 요약: {candidate_info.career_summary}", width=6),
                    dbc.Col(f"면접일: {candidate_info.interview_date}", width=3),
                    dbc.Col(f"연봉 정보: {candidate_info.salary_info}", width=3),
                ],
                className="report-meta-info",
            ),
        ],
        className="report-header p-4 mb-4",
    ) 