import dash_bootstrap_components as dbc
from dash import html
from ..report_schema import ReportData
from .full_report_header import create_full_report_header
from .full_report_summary import create_full_report_summary
from .full_report_by_material import create_full_report_by_material
from .full_report_detailed_analysis import create_detailed_analysis_section

def render_full_report(report_data: ReportData) -> html.Div:
    """
    전체 보고서 UI를 생성합니다.
    - 입력: ReportData Pydantic 모델 객체
    - 출력: Dash HTML Div 컴포넌트
    """
    if not isinstance(report_data, ReportData):
        return html.Div("보고서 데이터가 올바른 형식이 아닙니다.", className="report-container")

    # 1. 보고서 헤더 생성
    header_section = create_full_report_header(report_data.candidate_info)

    # 2. 종합 분석 및 레이더 차트 생성
    summary_section = create_full_report_summary(
        report_data.comprehensive_report,
        report_data.analysis_items
    )

    # 3. 자료별 분석 요약 생성
    materials_section = create_full_report_by_material(report_data.material_analysis)

    # 4. 세부 역량 분석 (Can Do, Will Do, Will Fit)
    detailed_analysis_section = create_detailed_analysis_section(report_data.analysis_items)

    return html.Div(
        [
            header_section,
            summary_section,
            materials_section,
            detailed_analysis_section,
        ],
        className="report-container p-4",
        style={"backgroundColor": "#fff", "fontFamily": "'Pretendard', sans-serif"}
    )
