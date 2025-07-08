from dash import html, dash_table

def render_summary_report(candidate: dict):
    # 주요 점수 및 요약 정보 추출
    name = candidate.get('name', '-')
    position = candidate.get('position', '-')
    created_at = candidate.get('created_at', '-')
    overall_score = candidate.get('overall_score', '-')
    digital_lit = candidate.get('growth_potential_digital_literacy', '-')
    personal_growth = candidate.get('growth_potential_wb_personal_growth', '-')
    general_report = candidate.get('general_report', '-')

    # 표 형태로 주요 점수 표시
    score_table = dash_table.DataTable(
        columns=[
            {"name": "항목", "id": "item"},
            {"name": "점수", "id": "score"}
        ],
        data=[
            {"item": "종합 점수", "score": overall_score},
            {"item": "디지털 리터러시", "score": digital_lit},
            {"item": "자기주도 성장", "score": personal_growth},
        ],
        style_cell={"fontFamily": "Pretendard, sans-serif", "fontSize": "1.01rem", "textAlign": "center"},
        style_header={"backgroundColor": "#F4F7FB", "fontWeight": 700},
        style_data={"backgroundColor": "#fff"},
        style_table={"width": "340px", "margin": "0 auto 18px auto"},
    )

    return html.Div([
        html.H3(f"{name} ({position}) - 종합 분석 요약", style={"fontWeight": 700, "fontSize": "1.18rem", "color": "#005BAC", "marginBottom": "12px"}),
        html.Div(f"분석일: {created_at}", style={"color": "#888", "fontSize": "1.01rem", "marginBottom": "8px"}),
        score_table,
        html.Div([
            html.H4("요약", style={"fontWeight": 600, "fontSize": "1.08rem", "marginTop": "18px", "marginBottom": "6px"}),
            html.Div(general_report or "요약 내용이 없습니다.", style={"whiteSpace": "pre-line", "fontSize": "1.04rem", "color": "#222"})
        ], style={"marginTop": "12px"})
    ], style={"padding": "18px 8px 8px 8px", "background": "#F8FAFF", "borderRadius": "10px", "boxShadow": "0 2px 8px #005BAC11"})
