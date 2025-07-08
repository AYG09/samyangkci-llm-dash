from dash import html, dcc
import dash_bootstrap_components as dbc

# 보고서 생성 컴포넌트 (Dash)
def ReportTab(candidates_df, selected_id=None, report_type=None):
    # candidates_df: DataFrame (id, name, general_report, executive_summary, hr_report 등)
    # selected_id: 선택된 후보자 id
    # report_type: 선택된 보고서 유형
    content = []
    content.append(html.H4("📄 보고서 생성", style={"color": "#24278B", "marginBottom": "8px"}))
    if not candidates_df.empty:
        content.append(html.H5("보고서 생성 및 다운로드", style={"marginTop": "16px"}))
        options = [
            {"label": f"{row['name']} (ID: {row['id']})", "value": row['id']} for _, row in candidates_df.iterrows()
        ]
        content.append(dcc.Dropdown(
            id="report-candidate-select",
            options=options,
            value=selected_id,
            placeholder="보고서를 생성할 후보자를 선택하세요",
            style={"marginBottom": "12px"}
        ))
        content.append(dcc.Dropdown(
            id="report-type-select",
            options=[
                {"label": "종합 보고서", "value": "종합 보고서"},
                {"label": "임원용 보고서", "value": "임원용 보고서"},
                {"label": "HR용 보고서", "value": "HR용 보고서"}
            ],
            value=report_type,
            placeholder="보고서 유형을 선택하세요",
            style={"marginBottom": "16px"}
        ))
        content.append(html.Div(id="report-content-area"))
    else:
        content.append(dbc.Alert("저장된 후보자 정보가 없습니다.", color="warning"))
    return html.Div(content)

# 상세/다운로드 등은 app.py 콜백에서 처리 필요
# 예시 콜백:
# @callback(
#     Output("report-content-area", "children"),
#     Input("report-candidate-select", "value"),
#     Input("report-type-select", "value"),
#     State("candidates_df", "data"),
# )
# def show_report_content(selected_id, report_type, data):
#     # data: DataFrame dict
#     # selected_id: 후보자 id, report_type: 보고서 유형
#     ...
