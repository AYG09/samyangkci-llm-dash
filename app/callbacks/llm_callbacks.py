"""LLM 분석 결과 입력 관련 콜백 함수들"""

import dash
from dash import Output, Input, State
import dash_bootstrap_components as dbc
from datetime import datetime

from ..db import save_llm_analysis_result
from ..utils_llm_parse import extract_candidate_info_from_text


def register_llm_callbacks(app):
    """LLM 관련 콜백들을 앱에 등록합니다."""
    
    @app.callback(
        [
            Output("analysis-confirmation-section", "style"),
            Output("llm-name-input", "value"),
            Output("llm-org-input", "value"),
            Output("llm-position-input", "value"),
            Output("llm-date-input", "value"),
            Output("llm-result-input", "value", allow_duplicate=True),
        ],
        [
            Input("start-analysis-btn", "n_clicks"),
            Input("final-save-btn", "n_clicks")
        ],
        [State("llm-result-input", "value")],
        prevent_initial_call=True
    )
    def parse_and_display_llm_result(
        start_clicks: int | None, save_clicks: int | None, raw_text: str | None
    ):
        print(f"[DEBUG] 콜백 실행됨: start_clicks={start_clicks}, save_clicks={save_clicks}")
        print(f"[DEBUG] raw_text 길이: {len(raw_text) if raw_text else 0}")
        
        ctx = dash.callback_context
        if not ctx.triggered:
            print("[DEBUG] ctx.triggered가 없음")
            return (dash.no_update,) * 6

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        print(f"[DEBUG] triggered_id: {triggered_id}")

        if triggered_id == "start-analysis-btn":
            print("[DEBUG] 분석 시작 버튼 클릭됨")
            if not raw_text:
                print("[DEBUG] raw_text가 비어있음")
                return (dash.no_update,) * 6
            print("[DEBUG] extract_candidate_info_from_text 호출 전")
            extracted_info = extract_candidate_info_from_text(raw_text)
            print(f"[DEBUG] 추출된 정보: {extracted_info}")
            return (
                {'display': 'block'},
                extracted_info.get("name", ""),
                extracted_info.get("organization", ""),
                extracted_info.get("position", ""),
                extracted_info.get("date", ""),
                dash.no_update
            )
        
        if triggered_id == "final-save-btn":
            # 저장 후 초기화
            return ({'display': 'none'}, "", "", "", "", "")

        return (dash.no_update,) * 6

    @app.callback(
        [
            Output("llm-org-input", "disabled"),
            Output("llm-position-input", "disabled"),
            Output("llm-date-input", "disabled"),
        ],
        [
            Input("start-analysis-btn", "n_clicks"),
            Input("edit-analysis-btn", "n_clicks"),
            Input("final-save-btn", "n_clicks"),
        ],
        prevent_initial_call=True
    )
    def toggle_input_fields_disabled(
        start_clicks: int | None, edit_clicks: int | None, save_clicks: int | None
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return (dash.no_update,) * 3

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if triggered_id == "start-analysis-btn":
            return True, True, True
        if triggered_id == "edit-analysis-btn":
            return False, False, False
        if triggered_id == "final-save-btn":
            return True, True, True

        return (dash.no_update,) * 3

    @app.callback(
        [
            Output("llm-save-msg", "children"),
            Output("save-signal-store", "data"),
        ],
        [Input("final-save-btn", "n_clicks")],
        [
            State("llm-name-input", "value"),
            State("llm-org-input", "value"),
            State("llm-position-input", "value"),
            State("llm-date-input", "value"),
            State("llm-result-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def final_save_data(
        n_clicks: int | None,
        name: str | None,
        org: str | None,
        pos: str | None,
        date: str | None,
        raw_text: str | None,
    ):
        if n_clicks is None:
            return dash.no_update, dash.no_update

        # 모든 필드가 채워졌는지 확인
        if not all([name, org, pos, date, raw_text]):
            return dbc.Alert("모든 필드를 채워주세요.", color="warning"), dash.no_update

        try:
            # 이 시점에서는 모든 변수가 str이므로 타입 오류가 발생하지 않음
            save_llm_analysis_result(
                name=str(name),
                organization=str(org),
                position=str(pos),
                interview_date=str(date),
                raw_llm_text=str(raw_text),
            )
            return (
                dbc.Alert(f"성공적으로 저장되었습니다: {name}", color="success"),
                datetime.now().isoformat(),
            )
        except Exception as e:
            return (
                dbc.Alert(f"저장 중 오류 발생: {e}", color="danger"),
                dash.no_update,
            ) 