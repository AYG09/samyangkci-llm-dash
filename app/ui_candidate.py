from dash.dependencies import Output, Input, State
import dash
from dash import dash_table, Dash, html, dcc
import io
import base64
import pandas as pd
import json
from datetime import datetime
from app.utils import export_json_result, try_parse_json
from app.db import load_candidates
# 콜백: 선택 삭제, 비교, 다운로드, 피드백 메시지, 비교 요약
def register_candidate_callbacks(app: Dash):
    # 선택된 행에 따라 버튼 활성/비활성 동적 제어 콜백
    @app.callback(
        [
            Output('candidate-delete-btn', 'disabled'),
            Output('candidate-compare-btn', 'disabled'),
            Output('candidate-download-btn', 'disabled'),
            Output('candidate-json-export-btn', 'disabled')
        ],
        [Input('candidate-table', 'selected_rows'), Input('candidate-table', 'data')]
    )
    def update_button_states(selected_rows, data):
        # Dash DataTable selected_rows는 None일 수 있음
        selected = selected_rows if selected_rows is not None else []
        # 삭제: 1개 이상 선택 시 활성화
        delete_disabled = not (len(selected) > 0)
        # 비교: 2개 이상 선택 시 활성화
        compare_disabled = not (len(selected) >= 2)
        # 다운로드: 데이터 1개 이상 있을 때만 활성화
        has_data = data is not None and len(data) > 0
        download_disabled = not has_data
        # JSON 내보내기: 1명만 선택 시 활성화
        json_export_disabled = not (len(selected) == 1 and has_data)
        return delete_disabled, compare_disabled, download_disabled, json_export_disabled

    @app.callback(
        [Output('candidate-table', 'data'),
         Output('candidate-table', 'selected_rows'),
         Output('candidate-table', 'selected_row_ids'),
         Output('candidate-action-msg', 'children'),
         Output('candidate-table', 'page_current')],
        [Input('candidate-delete-btn', 'n_clicks'), Input('candidate-download-btn', 'n_clicks')],
        [State('candidate-table', 'data'), State('candidate-table', 'selected_rows'), State('candidate-table', 'selected_row_ids')]
    )
    def candidate_action_callback(delete_clicks, download_clicks, data, selected_rows, selected_row_ids):
        from app.db import delete_candidate, load_candidates
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # 삭제 버튼 클릭
        if btn_id == 'candidate-delete-btn':
            if not delete_clicks:
                raise dash.exceptions.PreventUpdate
            if not selected_row_ids:
                return data, [], [], "삭제할 후보자를 선택하세요.", dash.no_update
            # --- 진단용 로그 추가 ---
            print("[삭제] data:", data)
            print("[삭제] selected_rows:", selected_rows)
            print("[삭제] selected_row_ids(raw):", selected_row_ids)
            
            # ID가 UUID 문자열이므로 더 이상 숫자로 변환하지 않습니다.
            ids_to_delete = selected_row_ids
            
            # 실제 data에 존재하는 id만 추출
            data_ids = {row.get('id') for row in data}
            valid_ids_to_delete = [i for i in ids_to_delete if i in data_ids]
            
            print("[삭제] ids_to_delete(valid):", valid_ids_to_delete)
            # ----------------------
            if not valid_ids_to_delete:
                return data, selected_rows, selected_row_ids, "유효한 삭제 대상을 찾을 수 없습니다.", dash.no_update

            for cid in valid_ids_to_delete:
                delete_candidate(cid)
            msg = f"{len(valid_ids_to_delete)}명 삭제 완료"
            # 삭제 후 최신 데이터 반환 및 순번 컬럼 추가
            df = load_candidates()
            display_cols = ["순번", "id", "name", "created_at", "evaluator", "position", "org", "overall_score"]
            col_map = {
                "순번": "순번",
                "id": "ID",
                "name": "이름",
                "created_at": "입력일자",
                "evaluator": "평가자",
                "position": "지원직급",
                "org": "지원조직",
                "overall_score": "점수(요약)"
            }
            for col in display_cols:
                if col not in df.columns:
                    df[col] = ""
            df["순번"] = list(range(1, len(df) + 1))
            df = df[display_cols].fillna("")
            # 안내 메시지 강화: 남은 데이터 안내
            if len(df) == 0:
                msg += " (남은 데이터가 없습니다)"
            else:
                msg += f" (남은 데이터 {len(df)}명, 첫 페이지로 이동)"
            return df.to_dict('records'), [], [], msg, 0
        # 다운로드 버튼 클릭
        elif btn_id == 'candidate-download-btn':
            if not download_clicks:
                raise dash.exceptions.PreventUpdate
            if not data or len(data) == 0:
                return dash.no_update, [], [], "다운로드할 데이터가 없습니다.", dash.no_update
            output = io.BytesIO()
            df = pd.DataFrame(data)
            df.to_excel(output, index=False)
            b64 = base64.b64encode(output.getvalue()).decode()
            href = f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
            link = html.A("엑셀 다운로드(여기 클릭)", href=href, download="candidates.xlsx", target="_blank", style={"color": "#0984e3", "fontWeight": 600})
            return dash.no_update, [], [], link, dash.no_update
        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output('candidate-compare-summary', 'children'),
        [Input('candidate-compare-btn', 'n_clicks')],
        [State('candidate-table', 'data'), State('candidate-table', 'selected_rows')]
    )
    def compare_candidates(n_clicks, data, selected_rows):
        if n_clicks:
            if not selected_rows or len(selected_rows) < 2:
                return html.Div("2명 이상 선택 시만 비교가 가능합니다.", style={"color": "#d63031", "fontWeight": 600, "marginTop": "8px"})
            # 간단 비교: 이름, 지원조직, 지원직급, 점수만 요약
            rows = [data[i] for i in selected_rows]
            header = html.Tr([html.Th("이름"), html.Th("지원조직"), html.Th("지원직급"), html.Th("점수(요약)")])
            body = [html.Tr([
                html.Td(r.get("name")),
                html.Td(r.get("org")),
                html.Td(r.get("position")),
                html.Td(r.get("overall_score"))
            ]) for r in rows]
            return html.Table([header] + body, style={"marginTop": "12px", "width": "100%", "borderCollapse": "collapse", "fontSize": "1.05rem"})
        raise dash.exceptions.PreventUpdate

    def render_candidate_detail(candidate):
        """
        후보자 상세 분석 결과 표시 및 JSON 내보내기 버튼 제공
        """
        result_raw = candidate.get('analysis_result', '')
        json_data = try_parse_json(result_raw)
        if json_data is not None:
            # JSON 데이터 정상 표시 + 내보내기 버튼
            export_btn = html.Button(
                "JSON 내보내기",
                id={"type": "export-json-btn", "index": candidate.get('id')},
                n_clicks=0,
                className="btn btn-success",
                style={"marginLeft": "12px", "fontWeight": 600, "borderRadius": "8px", "padding": "6px 16px"}
            )
            return html.Div([
                html.H5("분석 결과 (JSON)", style={"marginTop": "18px", "color": "#005BAC"}),
                dcc.Textarea(
                    value=result_raw,
                    style={"width": "100%", "height": "220px", "fontFamily": "monospace", "fontSize": "1.01rem"},
                    readOnly=True
                ),
                export_btn
            ])
        else:
            # 구버전 텍스트 데이터 안내
            return html.Div([
                html.H5("분석 결과 (구버전 텍스트)", style={"marginTop": "18px", "color": "#d63031"}),
                html.P("이 데이터는 JSON 형식이 아닙니다. 변환이 필요합니다.", style={"color": "#d63031", "fontWeight": 600}),
                dcc.Textarea(
                    value=result_raw,
                    style={"width": "100%", "height": "220px", "fontFamily": "monospace", "fontSize": "1.01rem", "background": "#fffbe6"},
                    readOnly=True
                )
            ])

    # (예시) 콜백: JSON 내보내기 버튼 클릭 시 파일 저장
    # 실제로는 후보자 상세 조회/상세화면 콜백에 연동 필요
    @app.callback(
        Output({'type': 'export-json-btn', 'index': dash.ALL}, 'children'),
        Input({'type': 'export-json-btn', 'index': dash.ALL}, 'n_clicks'),
        State('candidate-table', 'data')
    )
    def export_json_callback(n_clicks_list, data):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate
        triggered = ctx.triggered[0]['prop_id']
        # 버튼 index 추출
        import re
        m = re.search(r'index":(\d+)', triggered)
        if not m:
            raise dash.exceptions.PreventUpdate
        idx = int(m.group(1))
        # 해당 후보자 데이터 찾기
        candidate = next((row for row in data if row.get('id') == idx), None)
        if not candidate:
            return ["JSON 내보내기"]
        result_raw = candidate.get('analysis_result', '')
        json_data = try_parse_json(result_raw)
        if json_data is None:
            return ["JSON 내보내기"]
        # 파일로 저장
        path = export_json_result(candidate.get('name', f'candidate_{idx}'), json_data)
        return [f"저장됨: {path}"]
    @app.callback(
        Output('candidate-json-export-link', 'children'),
        Input('candidate-json-export-btn', 'n_clicks'),
        State('candidate-table', 'data'),
        State('candidate-table', 'selected_rows')
    )
    def export_json_callback(n_clicks, data, selected_rows):
        if not n_clicks or not data or not selected_rows or len(selected_rows) != 1:
            return ""
        idx = selected_rows[0]
        candidate = data[idx]
        result_raw = candidate.get('analysis_result', '')
        json_data = try_parse_json(result_raw)
        if json_data is None:
            return html.Span("JSON 데이터가 아닙니다.", style={"color": "#d63031", "fontWeight": 600})
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        b64 = base64.b64encode(json_str.encode('utf-8')).decode()
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{candidate.get('name', 'candidate')}_분석결과_{today}.json"
        href = f"data:application/json;base64,{b64}"
        return html.A("JSON 다운로드(여기 클릭)", href=href, download=filename, target="_blank", style={"color": "#0984e3", "fontWeight": 600})
# 복사본: render_candidate_management_tab 함수


def render_candidate_management_tab():
    # DB에서 모든 후보자 데이터 한 번에 로드
    df = load_candidates()

    if df.empty:
        return html.Div([
            html.H4("등록된 후보자가 없습니다.", style={"marginTop": "32px", "color": "#888"})
        ])

    # 테이블에 표시할 데이터 리스트 생성
    data = []
    for _, row in df.iterrows():
        json_data = try_parse_json(row.get('json_data', '{}'))
        info = json_data.get('면접자정보', {})
        overall_assessment = json_data.get('종합평가', {})
        
        data.append({
            'id': row.get('id', ''),
            'name': row.get('name', ''),
            'created_at': info.get('입력일자', ''),
            'evaluator': info.get('평가자', ''),
            'position': info.get('지원직급', ''),
            'org': info.get('지원조직', ''),
            'overall_score': overall_assessment.get('종합점수', ''),
            'analysis_result': row.get('json_data', '{}') # 상세보기를 위한 원본 JSON 문자열
        })

    # 순번 추가
    for i, row in enumerate(data):
        row['순번'] = i + 1

    # 테이블 컬럼 정의
    columns = [
        {"name": "순번", "id": "순번", "type": "numeric"},
        {"name": "이름", "id": "name"},
        {"name": "입력일자", "id": "created_at"},
        {"name": "평가자", "id": "evaluator"},
        {"name": "지원직급", "id": "position"},
        {"name": "지원조직", "id": "org"},
        {"name": "점수(요약)", "id": "overall_score"},
    ]

    return html.Div([
        html.H3("후보자 관리", style={"color": "#003A70", "marginBottom": "20px"}),
        html.Div([
            html.Button("선택 삭제", id="candidate-delete-btn", className="btn btn-danger", style={"marginRight": "8px"}, disabled=True),
            html.Button("선택 비교", id="candidate-compare-btn", className="btn btn-info", style={"marginRight": "8px"}, disabled=True),
            html.Button("전체 다운로드 (Excel)", id="candidate-download-btn", className="btn btn-secondary", style={"marginRight": "8px"}, disabled=False),
            html.Button("선택 내보내기 (JSON)", id="candidate-json-export-btn", className="btn btn-primary", style={"marginRight": "8px"}, disabled=True),
            html.Div(id="candidate-json-export-link", style={"display": "inline-block", "marginLeft": "10px"}),
        ], style={"marginBottom": "12px"}),
        html.Div(id="candidate-action-msg", style={"marginBottom": "12px", "fontWeight": "600", "minHeight": "24px"}),
        dash_table.DataTable(
            id='candidate-table',
            columns=columns,
            data=data,
            row_selectable='multi',
            page_size=10,
            page_current=0,
            sort_action='native',
            filter_action='native',
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px', 'fontFamily': 'S-CoreDream-4Regular'},
            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'color': '#003A70'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
        ),
        html.Div(id='candidate-compare-summary')
    ])
