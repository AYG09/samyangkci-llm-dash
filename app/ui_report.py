# 복사본: render_report_tab 함수
from dash import html, dcc, dash_table
from app.db import load_candidates
from app.components.executive_report import render_executive_report
from app.components.full_report import render_full_report
from dash.dependencies import Output, Input

def get_candidate_options():
    candidates_df = load_candidates()
    return [
        {"label": f"{row['name']} (ID: {row['id']})", "value": row['id']} for _, row in candidates_df.iterrows()
    ]

def render_report_tab():
    return html.Div([
        html.H2("보고서 생성", style={"fontWeight": 800, "fontSize": "1.3rem", "color": "#1A237E", "marginBottom": "18px"}),
        html.Div([
            html.Label("후보자 선택", style={"fontWeight": 600, "marginRight": "12px"}),
            dcc.Dropdown(
                id="report-candidate-dropdown",
                options=get_candidate_options(),
                placeholder="후보자를 선택하세요",
                style={"width": "320px", "display": "inline-block"}
            ),
            html.Label("보고서 유형", style={"fontWeight": 600, "marginLeft": "32px", "marginRight": "12px"}),
            dcc.Dropdown(
                id="report-type-dropdown",
                options=[
                    {"label": "임원용 보고서", "value": "executive"},
                    {"label": "HR담당자용 보고서", "value": "hr"},
                    {"label": "종합 분석 요약", "value": "summary"},
                ],
                value="executive",
                style={"width": "220px", "display": "inline-block"}
            ),
            html.Button(
                "보고서 생성", id="report-generate-btn", n_clicks=0,
                style={"marginLeft": "32px", "fontWeight": 600, "background": "#005BAC", "color": "#fff", "border": "none", "borderRadius": "6px", "padding": "8px 22px", "fontSize": "1.02rem", "boxShadow": "0 2px 8px #005BAC22"}
            ),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "24px"}),
        html.Div(id="report-content-area")
    ], style={"background": "#fff", "borderRadius": "12px", "boxShadow": "0 2px 12px #005BAC11", "padding": "32px 28px 24px 28px", "width": "100%", "maxWidth": "1100px", "margin": "0 auto", "marginTop": "24px"})



# 버튼 클릭 시에만 보고서 생성
def update_report_content(candidate_id, report_type, n_clicks):
    if not n_clicks or n_clicks < 1:
        return html.Div("보고서 생성 버튼을 눌러주세요.", style={"color": "#888", "fontSize": "1.1rem"})
    if not candidate_id:
        return html.Div("후보자를 선택하세요.", style={"color": "#888", "fontSize": "1.1rem"})
    candidates_df = load_candidates()
    candidate = candidates_df[candidates_df['id'] == candidate_id].iloc[0].to_dict()
    if report_type == 'executive':
        return render_executive_report(candidate)
    elif report_type == 'summary':
        return render_full_report(candidate)
    # HR 보고서 등 다른 유형은 추후 구현
    return html.Div("보고서 내용 영역(구현 필요)", style={"color": "#888", "fontSize": "1.1rem"})

from dash import callback
callback(
    Output('report-content-area', 'children'),
    [Input('report-candidate-dropdown', 'value'),
     Input('report-type-dropdown', 'value'),
     Input('report-generate-btn', 'n_clicks')]
)(update_report_content)
