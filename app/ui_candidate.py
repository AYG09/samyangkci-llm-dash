from dash.dependencies import Output, Input, State
import dash
import io
import base64
from dash import dash_table
# 콜백: 선택 삭제, 비교, 다운로드, 피드백 메시지, 비교 요약
def register_candidate_callbacks(app):
    # 선택된 행에 따라 버튼 활성/비활성 동적 제어 콜백
    @app.callback(
        [
            Output('candidate-delete-btn', 'disabled'),
            Output('candidate-compare-btn', 'disabled'),
            Output('candidate-download-btn', 'disabled')
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
        return delete_disabled, compare_disabled, download_disabled

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
            # id 타입 일치화 및 유효성 체크
            try:
                ids_to_delete = [int(i) for i in selected_row_ids]
            except Exception as e:
                print("[삭제] id 변환 오류:", e)
                return data, [], [], "삭제할 후보자 id 변환 오류", dash.no_update
            # 실제 data에 존재하는 id만 추출
            data_ids = set(row.get('id') for row in data)
            valid_ids_to_delete = [i for i in ids_to_delete if i in data_ids]
            print("[삭제] ids_to_delete(valid):", valid_ids_to_delete)
            # ----------------------
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
            import pandas as pd
            import io, base64
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
# 복사본: render_candidate_management_tab 함수
from dash import html, dcc
from dash import dash_table
import pandas as pd
from app.db import load_candidates

def render_candidate_management_tab():
    # DB에서 후보자 데이터 로드
    df = load_candidates()
    # 주요 컬럼만 추출 및 None/빈값 안전 처리
    if df.empty:
        return html.Div([
            html.H4("등록된 후보자가 없습니다.", style={"marginTop": "32px", "color": "#888"})
        ])
    # 컬럼명 매핑 및 표시용 컬럼만 선택 + 순번 컬럼 추가
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
    # DataTable은 내부적으로 영문 키 사용, 표시만 한글
    table = dash_table.DataTable(
        id='candidate-table',
        columns=[{"name": col_map.get(i, i), "id": i, "deletable": False, "selectable": True} for i in display_cols],
        data=df.to_dict('records'),
        row_selectable='multi',
        selected_rows=[],
        selected_row_ids=[],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "fontSize": "1.02rem"},
        style_header={"backgroundColor": "#F4F7FB", "fontWeight": 700},
        style_data_conditional=[
            {"if": {"column_id": "overall_score"}, "color": "#005BAC", "fontWeight": 600}
        ],
        filter_action="native",
        sort_action="native",
        row_deletable=False
        # DataTable에는 key 속성 미지원, 안전한 row 추적은 id 컬럼 활용
    )
    # 디자인 원칙(사람 중심, 신뢰, 단순함, 브랜드 일관성, 피드백, 접근성 등) 반영 컨테이너
    return html.Section([
        html.H2("👤 후보자 조회 및 비교", style={
            "fontWeight": 800,
            "fontSize": "1.45rem",
            "marginBottom": "16px",
            "color": "#1A237E",
            "letterSpacing": "-0.5px",
            "fontFamily": "Pretendard, sans-serif"
        }),
        html.P("후보자 정보를 안전하게 관리하고, 신뢰할 수 있는 데이터로 비교·분석하세요.", style={
            "color": "#005BAC",
            "fontWeight": 500,
            "fontSize": "1.08rem",
            "marginBottom": "18px",
            "letterSpacing": "-0.2px"
        }),
        dcc.Store(id="candidate-selected-rows-store"),
        html.Div([
            dcc.Loading([
                html.Button(
                    "선택 삭제",
                    id="candidate-delete-btn",
                    n_clicks=0,
                    className="btn btn-danger",
                    style={
                        "marginRight": "12px",
                        "fontWeight": 600,
                        "borderRadius": "8px",
                        "padding": "8px 18px",
                        "fontSize": "1.04rem"
                    },
                    disabled=True  # 기본 비활성화, 콜백에서 동적 제어
                ),
                html.Button(
                    "엑셀 다운로드",
                    id="candidate-download-btn",
                    n_clicks=0,
                    className="btn btn-secondary",
                    style={
                        "marginRight": "12px",
                        "fontWeight": 600,
                        "borderRadius": "8px",
                        "padding": "8px 18px",
                        "fontSize": "1.04rem"
                    },
                    disabled=True  # 기본 비활성화, 콜백에서 동적 제어
                ),
                html.Button(
                    "간단 비교",
                    id="candidate-compare-btn",
                    n_clicks=0,
                    className="btn btn-primary",
                    style={
                        "fontWeight": 600,
                        "borderRadius": "8px",
                        "padding": "8px 18px",
                        "fontSize": "1.04rem"
                    },
                    disabled=True  # 기본 비활성화, 콜백에서 동적 제어
                ),
                html.Span(id="candidate-action-msg", style={
                    "marginLeft": "18px",
                    "color": "#0984e3",
                    "fontWeight": 600,
                    "fontSize": "1.08rem"
                })
            ])
        ], style={"marginBottom": "18px", "display": "flex", "flexWrap": "wrap", "alignItems": "center"}),
        html.Div([
            table
        ], style={
            "background": "#F8FAFF",
            "borderRadius": "10px",
            "boxShadow": "0 1px 8px #005BAC11",
            "padding": "18px 10px 10px 10px",
            "marginBottom": "8px"
        }),
        html.Div(id="candidate-compare-summary", style={"marginTop": "24px"})
    ], style={
        "background": "#fff",
        "borderRadius": "16px",
        "boxShadow": "0 2px 16px #005BAC18",
        "padding": "38px 32px 28px 32px",
        "width": "100%",
        "maxWidth": "1100px",
        "margin": "0 auto",
        "marginTop": "18px",
        "marginBottom": "32px",
        "transition": "box-shadow 0.2s"
    })
