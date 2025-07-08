from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from typing import Optional

# 후보자 관리 컴포넌트 (Dash)
def CandidateManagement(candidate_df: pd.DataFrame, selected_id: Optional[int] = None) -> html.Div:
    # candidate_df: DataFrame (id, created_at, raw_result 등 포함)
    # selected_id: 선택된 후보자 id
    options = [
        {"label": f"ID: {row['id']} | 저장일: {row['created_at']}", "value": row['id']} for _, row in candidate_df.iterrows()
    ] if not candidate_df.empty else []

    return html.Div([
        html.Div([
            html.Span("👤", className="emoji", style={"fontSize": "1.5rem", "marginRight": "8px"}),
            html.Span("삼양KCI 후보자 관리", style={"color": "#1A237E", "fontSize": "1.25rem", "fontWeight": "bold", "verticalAlign": "middle"})
        ], style={"backgroundColor": "#F4F7FB", "padding": "16px 0 8px 0", "marginBottom": "24px", "borderRadius": "14px"}),
        html.H4("👥 후보자 리스트 및 상세", style={"color": "#24278B", "marginBottom": "8px", "fontWeight": 800, "fontSize": "1.13rem"}),
        html.Div("저장된 후보자 목록에서 선택하면 LLM 분석 결과 전체를 확인할 수 있습니다.", style={"marginBottom": "12px", "color": "#555", "fontSize": "1.01rem"}),
        dbc.Button("새로고침", id="refresh-candidate-btn", color="primary", className="dash-button", style={"width": "100%", "marginBottom": "16px"}),
        html.Div([
            dbc.Table.from_dataframe(candidate_df[["id", "created_at"]], striped=True, bordered=True, hover=True, style={"marginBottom": "16px", "background": "#fff", "borderRadius": "12px"}) if not candidate_df.empty else html.Div([
                html.Span("ℹ️", className="emoji"),
                " 저장된 후보자 정보가 없습니다."
            ], className="info-card")
        ]),
        dcc.Dropdown(
            id="candidate-select",
            options=options,
            value=selected_id,
            placeholder="상세 분석 결과를 볼 후보자 선택",
            className="dash-dropdown",
            style={"marginBottom": "16px"}
        ) if not candidate_df.empty else None,
        html.Div(id="candidate-detail-area")
    ])

# 상세/삭제/다운로드 등은 app.py 콜백에서 처리 필요
# 예시 콜백:
# @callback(
#     Output("candidate-detail-area", "children"),
#     Input("candidate-select", "value"),
#     State("candidate_df", "data"),
# )
# def show_candidate_detail(selected_id, data):
#     # data: DataFrame dict
#     # selected_id: 선택된 후보자 id
#     # 상세/삭제/다운로드 구현
#     ...
