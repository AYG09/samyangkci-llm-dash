import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from typing import Optional, Any
# import json

# 변경된 임포트 경로
from .db import load_candidate_raw_llm_text
from .llm_report_parser import parse_llm_report
from .report_schema import ReportData

# 보고서 유형별 렌더링 함수 임포트
# from .components.full_report import render_full_report - 더 이상 사용하지 않음
from .components.executive_visual_report import render_executive_visual_report
from .components.hr_visual_report import render_hr_visual_report
from .components.comprehensive_visual_report import create_comprehensive_visual_report


def render_report_tab() -> html.Div:
    """'보고서 생성' 탭의 전체 레이아웃을 렌더링합니다."""
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader("후보자 검색 필터"),
                    dbc.CardBody(
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Input(id="filter-name", placeholder="이름으로 검색..."),
                                    width=3,
                                ),
                                dbc.Col(
                                    dbc.Input(id="filter-org", placeholder="지원조직으로 검색..."),
                                    width=3,
                                ),
                                dbc.Col(
                                    dbc.Input(id="filter-pos", placeholder="지원직급으로 검색..."),
                                    width=3,
                                ),
                                dbc.Col(
                                    dbc.Button("조회", id="filter-btn", className="w-100"),
                                    width=2,
                                ),
                                dbc.Col(
                                    dbc.Button("삭제", id="delete-btn", color="danger", className="w-100"),
                                    width=1,
                                ),
                                dbc.Col(
                                    dbc.Button("Export", id="export-btn", color="success", className="w-100"),
                                    width=1,
                                ),
                                dbc.Col(
                                    dbc.Button("PDF", id="report-pdf-btn", color="warning", className="w-100"),
                                    width=1,
                                ),
                                dbc.Col(
                                    dbc.Button("PPT", id="report-ppt-btn", color="info", className="w-100"),
                                    width=1,
                                ),
                            ],
                            className="g-3",
                        )
                    ),
                ],
                className="mb-4",
            ),
            dcc.Download(id="download-excel"),
            # 필터링된 후보자 목록이 여기에 표시될 예정 (테이블)
            dbc.Row(
                [
                    dbc.Col(
                        dash_table.DataTable(
                            id='candidate-table',
                            columns=[
                                {"name": "이름", "id": "name"},
                                {"name": "지원조직", "id": "organization"},
                                {"name": "지원직급", "id": "position"},
                                {"name": "면접일", "id": "interview_date"},
                                {"name": "종합평점", "id": "overall_score"},
                                {"name": "채용추천", "id": "recommendation"},
                            ],
                            data=[],
                            row_selectable='single',
                            sort_action='native',
                            page_action='native',
                            page_size=10,
                            export_format='xlsx',
                            export_headers='display',
                            # Export 버튼 숨기기 위한 스타일
                            style_as_list_view=True, # 행 스타일 변경
                            style_header={
                                'backgroundColor': '#F8F9FA',
                                'fontWeight': 'bold',
                                'border': '1px solid #DEE2E6'
                            },
                            style_cell={
                                'padding': '10px',
                                'textAlign': 'left',
                                'border': '1px solid #DEE2E6'
                            },
                            # 기본 Export 버튼 숨기기
                            css=[{
                                'selector': '.export',
                                'rule': 'display: none !important'
                            }],
                        ),
                        width=9
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="report-type-dropdown",
                            options=[
                                {"label": "종합 대시보드", "value": "comprehensive"},
                                {"label": "임원용 비주얼 리포트", "value": "executive_visual"},
                                {"label": "HR 비주얼 리포트", "value": "hr_visual"},
                            ],
                            value="comprehensive",
                            clearable=False,
                        ),
                        width=3,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Spinner(html.Div(id="report-content-area")),
        ],
        className="p-4",
    )


def update_report_content(
    candidate_id: Optional[str], report_type: Optional[str]
) -> Any:
    """선택된 후보자와 보고서 유형에 따라 보고서 내용을 생성하고 업데이트합니다."""
    if not candidate_id or not report_type:
        return html.Div(
            "테이블에서 후보자를 선택하고 보고서 유형을 지정해주세요.", className="text-center mt-4"
        )

    try:
        # 1. DB에서 원시 LLM 텍스트 데이터 로드
        raw_llm_text = load_candidate_raw_llm_text(candidate_id)
        if not raw_llm_text:
            return dbc.Alert(
                f"오류: 후보자(ID: {candidate_id})의 LLM 분석 원문 데이터를 찾을 수 없습니다.",
                color="danger"
            )

        # 2. 강화된 파서로 ReportData 객체 생성
        report_data: ReportData = parse_llm_report(raw_llm_text)

        # 3. 보고서 유형에 따라 적절한 렌더링 함수 호출
        if report_type == "comprehensive":
            return create_comprehensive_visual_report(report_data)
        elif report_type == "executive_visual":
            return render_executive_visual_report(report_data)
        elif report_type == "hr_visual":
            return render_hr_visual_report(report_data)
        else:
            return dbc.Alert(
                f"알 수 없는 보고서 유형: {report_type}", color="warning"
            )

    except Exception as e:
        error_message = f"보고서 생성 중 오류 발생 (후보자 ID: {candidate_id}): {e}"
        return dbc.Alert(
            [
                html.H4("오류가 발생했습니다.", className="alert-heading"),
                html.P("LLM 분석 결과(JSON)가 새로운 보고서 형식과 맞지 않을 수 있습니다."),
                html.P("시스템 관리자에게 다음 오류 메시지를 전달해주세요:"),
                html.Code(error_message),
            ],
            color="danger",
        )


# 콜백은 app.py에서 등록됨
