import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Optional, Any
import json

# 변경된 임포트 경로
from .db import load_candidate_json
from .llm_report_parser import parse_llm_report
from .report_schema import ReportData

# 보고서 유형별 렌더링 함수 임포트
from .components.executive_report import render_executive_report
from .components.full_report import render_full_report
from .components.hr_report import render_hr_report


def render_report_tab() -> html.Div:
    """'보고서 생성' 탭의 전체 레이아웃을 렌더링합니다."""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="report-candidate-dropdown",
                            placeholder="분석 결과를 조회할 후보자를 선택하세요.",
                        ),
                        width=9,
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="report-type-dropdown",
                            options=[
                                {"label": "경영진 요약 보고서", "value": "executive"},
                                {"label": "전체 종합 보고서", "value": "full"},
                                {"label": "HR 상세 보고서", "value": "hr"},
                            ],
                            value="full",
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
            "후보자와 보고서 유형을 선택해주세요.", className="text-center mt-4"
        )

    try:
        # 1. DB에서 원시 JSON 데이터 로드 (이 함수는 dict를 반환)
        raw_json_dict = load_candidate_json(candidate_id)
        if not raw_json_dict:
            return dbc.Alert(
                f"오류: 후보자(ID: {candidate_id}) 데이터를 찾을 수 없습니다.",
                color="danger"
            )

        # 2. 파서가 문자열을 기대하므로 dict를 다시 JSON 문자열로 변환
        json_string = json.dumps(raw_json_dict, ensure_ascii=False)
        report_data: ReportData = parse_llm_report(json_string)

        # 3. 보고서 유형에 따라 적절한 렌더링 함수 호출
        if report_type == "executive":
            return render_executive_report(report_data)
        elif report_type == "full":
            return render_full_report(report_data)
        elif report_type == "hr":
            return render_hr_report(report_data)
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
