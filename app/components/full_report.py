from dash import html
from ..report_schema import ReportData

# 컴포넌트 임포트
from .full_report_header import create_full_report_header
from .full_report_summary import create_full_report_summary
from .full_report_by_material import create_full_report_by_material
from .radar_chart import create_radar_chart
from .decision_points_section import create_decision_points_section
from .full_report_detailed_analysis import create_detailed_analysis_section


def render_full_report(report_data: ReportData) -> html.Div:
    """
    전체 종합 보고서 UI를 생성합니다.
    - Executive Summary
    - 자료별 분석
    - 핵심 의사결정 포인트 (강점/리스크)
    - 세부 역량 분석
    """
    # 각 섹션 생성
    header_section = create_full_report_header(report_data.candidate_info)
    summary_section = create_full_report_summary(
        report_data.comprehensive_report
    )
    by_material_section = create_full_report_by_material(
        report_data.material_analysis
    )
    decision_points = create_decision_points_section(
        report_data.decision_points
    )
    radar_chart_section = create_radar_chart(report_data.analysis_items)
    detailed_analysis_section = create_detailed_analysis_section(
        report_data.analysis_items
    )

    return html.Div(
        [
            header_section,
            summary_section,
            by_material_section,
            decision_points,
            radar_chart_section,
            detailed_analysis_section,
        ],
        className="report-container"
    )


# No callbacks needed anymore for toggling
