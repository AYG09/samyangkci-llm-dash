"""면접자 조회 및 보고서 관련 콜백 함수들"""

import dash
from dash import Output, Input, State, html
import dash_bootstrap_components as dbc
import pandas as pd
import json

from ..db import load_candidates, delete_candidate
from ..ui_report import update_report_content
from ..llm_report_parser import parse_llm_report


def parse_row(row):
    """테이블의 각 행을 파싱하여 동적 컬럼(json_data, evaluator)을 처리합니다."""
    # json_data 파싱
    try:
        json_text = row['json_data']
        json_data = (
            json.loads(json_text)
            if json_text and json_text != 'NULL' else {}
        )
    except (json.JSONDecodeError, TypeError):
        json_data = {}

    # 'info' 키 없이 직접 접근하도록 수정
    row['organization'] = json_data.get('organization', '')
    row['position'] = json_data.get('position', '')

    # evaluator 파싱 - LLM 원문 텍스트를 파싱하여 평점과 추천 추출
    try:
        raw_llm_text = row['evaluator']
        if raw_llm_text and raw_llm_text.strip():
            parsed_result = parse_llm_report(raw_llm_text)
            # 파싱 결과가 ReportData 객체인지 확인
            if hasattr(parsed_result, 'comprehensive_report') and parsed_result.comprehensive_report:
                row['overall_score'] = parsed_result.comprehensive_report.score
                row['recommendation'] = parsed_result.comprehensive_report.recommendation
            elif isinstance(parsed_result, dict):
                # Dict 형태로 반환된 경우
                comp_report = parsed_result.get('comprehensive_report', {})
                if comp_report:
                    row['overall_score'] = comp_report.get('score', 0)
                    row['recommendation'] = comp_report.get('recommendation', 'N/A')
                else:
                    row['overall_score'] = 0
                    row['recommendation'] = 'N/A'
            else:
                row['overall_score'] = 0
                row['recommendation'] = 'N/A'
        else:
            row['overall_score'] = 0
            row['recommendation'] = 'N/A'
    except Exception:
        # 파싱 실패 시 기본값 설정
        row['overall_score'] = 0
        row['recommendation'] = 'N/A'
        
    return row


def register_report_callbacks(app):
    """보고서 관련 콜백들을 앱에 등록합니다."""
    
    @app.callback(
        Output("candidate-table", "data", allow_duplicate=True),
        [
            Input("filter-btn", "n_clicks"),
            Input("delete-btn", "n_clicks"),
            Input("save-signal-store", "data"),  # 저장 신호를 여기서 감지
        ],
        [
            State("filter-name", "value"),
            State("filter-org", "value"),
            State("filter-pos", "value"),
            State("candidate-table", "selected_rows"),
            State("candidate-table", "data"),
        ],
        prevent_initial_call=True
    )
    def update_candidate_table(
        filter_clicks, delete_clicks, save_signal, name, org, pos,
        selected_rows, table_data
    ):
        """후보자 목록 테이블을 필터링, 삭제, 갱신합니다."""
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
            
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # 삭제 로직
        if triggered_id == "delete-btn" and selected_rows and table_data:
            selected_id = table_data[selected_rows[0]].get("id")
            if selected_id:
                delete_candidate(selected_id)

        # 데이터 로딩 및 파싱
        df = load_candidates()
        if not df.empty:
            df = df.apply(parse_row, axis=1)
            # 필터링 로직
            if triggered_id == "filter-btn":
                if name:
                    df = df[df["name"].str.contains(name, case=False, na=False)]
                if org:
                    df = df[
                        df["organization"].str.contains(org, case=False, na=False)
                    ]
                if pos:
                    df = df[df["position"].str.contains(pos, case=False, na=False)]

        return df.to_dict("records")

    @app.callback(
        Output("report-content-area", "children"),
        [
            Input("candidate-table", "selected_rows"),
            Input("report-type-dropdown", "value"),
        ],
        State("candidate-table", "data"),  # State로 변경하여 직접적인 트리거 방지
        prevent_initial_call=True,
    )
    def update_report_display(selected_rows, report_type, table_data):
        """선택된 후보자와 보고서 유형에 따라 보고서 내용을 표시합니다."""
        ctx = dash.callback_context
        # 콜백이 트리거된 이유가 selected_rows나 report_type 변경이 아니면 업데이트 방지
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if triggered_id not in ["candidate-table", "report-type-dropdown"]:
            raise dash.exceptions.PreventUpdate

        # 안전한 에러 핸들링으로 탭 리셋 방지
        try:
            if not selected_rows or not table_data:
                return html.Div(
                    "테이블에서 후보자를 선택하고 보고서 유형을 지정해주세요.",
                    className="text-center mt-4 p-4 text-muted",
                )

            selected_row_index = selected_rows[0]
            # 데이터가 변경되어도 인덱스가 유효한지 확인
            if selected_row_index >= len(table_data):
                return html.Div(
                    "테이블이 갱신되었습니다. 후보자를 다시 선택해주세요.",
                    className="text-center mt-4 p-4 text-muted",
                )
            
            selected_candidate_id = table_data[selected_row_index].get("id")

            if not selected_candidate_id:
                return dbc.Alert("선택된 후보자의 ID를 찾을 수 없습니다.", color="warning")

            # 보고서 생성 시도 - 안전한 방식으로
            try:
                report_content = update_report_content(selected_candidate_id, report_type)
                
                # 보고서 생성 성공 시 반환
                if report_content is not None:
                    return report_content
                else:
                    return dbc.Alert(
                        "보고서 생성이 완료되지 않았습니다. 잠시 후 다시 시도해주세요.",
                        color="info",
                        className="mt-4"
                    )
                    
            except Exception as report_error:
                # 보고서 생성 관련 에러만 처리
                print(f"Report generation error: {str(report_error)}")
                return dbc.Alert([
                    html.H5("보고서 생성 오류", className="alert-heading"),
                    html.P("선택한 후보자의 보고서를 생성하는 중 문제가 발생했습니다."),
                    html.P("다른 보고서 유형을 선택하거나 후보자를 다시 선택해주세요."),
                    html.Hr(),
                    html.Small(f"오류 세부사항: {str(report_error)}", className="text-muted")
                ], color="warning", className="mt-4")
            
        except Exception as e:
            # 최상위 예외 처리 - 절대 실패하지 않도록
            print(f"Critical error in update_report_display: {str(e)}")
            
            return dbc.Alert([
                html.H5("시스템 오류", className="alert-heading"),
                html.P("시스템에서 예기치 않은 오류가 발생했습니다."),
                html.P("페이지를 새로고침하거나 관리자에게 문의하세요."),
                html.Hr(),
                html.Small(f"오류 ID: {str(e)[:100]}", className="text-muted")
            ], color="danger", className="mt-4")

    @app.callback(
        Output("download-excel", "data"),
        Input("export-btn", "n_clicks"),
        State("candidate-table", "data"),
        prevent_initial_call=True,
    )
    def download_excel(n_clicks, table_data):
        """후보자 목록을 Excel 파일로 다운로드합니다."""
        if n_clicks is None:
            return dash.no_update
        
        if not table_data:
            return dash.no_update
            
        df = pd.DataFrame(table_data)
        return dash.dcc.send_data_frame(df.to_excel, "candidates.xlsx", index=False)

    @app.callback(
        Output("report-content-area", "children", allow_duplicate=True),
        [Input("report-pdf-btn", "n_clicks"), Input("report-ppt-btn", "n_clicks")],
        [State("candidate-table", "selected_rows"), State("candidate-table", "data")],
        prevent_initial_call=True,
    )
    def handle_pdf_ppt_export(pdf_clicks, ppt_clicks, selected_rows, table_data):
        """PDF/PPT 출력 버튼을 처리합니다."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
            
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if not selected_rows or not table_data:
            return dbc.Alert("PDF/PPT 출력을 위해 후보자를 1명 선택하세요.", color="warning")
        
        selected_candidate = table_data[selected_rows[0]]
        candidate_id = selected_candidate.get("id")
        candidate_name = selected_candidate.get("name", "후보자")
        
        if not candidate_id:
            return dbc.Alert("선택된 후보자의 ID를 찾을 수 없습니다.", color="danger")
        
        output_type = "PDF" if btn_id == "report-pdf-btn" else "PPT"
        color = "primary" if btn_id == "report-pdf-btn" else "success"
        
        return dbc.Alert([
            html.H5(f"{output_type} 출력 준비 완료", className="alert-heading"),
            html.P(f"{candidate_name} 후보자의 보고서를 {output_type}로 출력할 수 있습니다."),
            html.P("아래 링크를 클릭하여 각 보고서를 새 창에서 열고 브라우저의 인쇄 기능을 사용하세요:"),
            html.Div([
                dbc.Button(
                    f"📊 종합 대시보드 {output_type}",
                    href=f"/print-report/{candidate_id}/comprehensive",
                    target="_blank",
                    color=color,
                    outline=True,
                    size="sm",
                    className="me-2 mb-2"
                ),
                dbc.Button(
                    f"📈 임원용 보고서 {output_type}",
                    href=f"/print-report/{candidate_id}/executive",
                    target="_blank",
                    color=color,
                    outline=True,
                    size="sm",
                    className="me-2 mb-2"
                ),
                dbc.Button(
                    f"👥 HR 보고서 {output_type}",
                    href=f"/print-report/{candidate_id}/hr",
                    target="_blank",
                    color=color,
                    outline=True,
                    size="sm",
                    className="mb-2"
                ),
            ])
        ], color=color, className="mt-3") 