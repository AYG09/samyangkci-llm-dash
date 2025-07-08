from dash import html, dcc
import dash_bootstrap_components as dbc

# LLM 분석 결과 입력 폼 (Dash)
def LLMInputForm():
    return html.Div([
        html.Div([
            html.Img(src="https://www.samyangkci.com/resources/kr/local/images/common/logo.svg", height="40", style={"marginLeft": "16px", "verticalAlign": "middle"}),
            html.Span("삼양KCI LLM 분석 결과 입력", style={"color": "white", "fontSize": "2rem", "fontWeight": "bold", "marginLeft": "16px", "verticalAlign": "middle"})
        ], style={"backgroundColor": "#24278B", "padding": "16px 0 8px 0", "marginBottom": "24px"}),
        html.H4("📝 LLM 분석 결과 입력", style={"color": "#24278B", "marginBottom": "8px"}),
        html.Div("LLM으로부터 받은 분석 결과(프롬프트 구조에 맞는 개조식 텍스트)를 아래에 붙여넣고 '저장하기' 버튼을 눌러주세요.", style={"marginBottom": "12px"}),
        dcc.Textarea(
            id="llm-result-input",
            placeholder="프롬프트 구조에 맞는 LLM 분석 결과를 붙여넣으세요...",
            style={"width": "100%", "height": 500, "fontSize": "1.08rem", "marginBottom": "16px"}
        ),
        dbc.Button("결과 저장하기", id="save-result-btn", color="primary", style={"width": "100%", "fontWeight": "bold", "fontSize": "1.15rem"}),
        html.Div(id="llm-result-feedback", style={"marginTop": "16px"})
    ])

# 콜백 예시 (app.py에서 등록 필요)
# @callback(
#     Output("llm-result-feedback", "children"),
#     Input("save-result-btn", "n_clicks"),
#     State("llm-result-input", "value"),
#     prevent_initial_call=True
# )
# def save_llm_result(n_clicks, text_input):
#     if n_clicks:
#         if text_input:
#             # save_candidate_data({"raw_result": text_input})
#             return dbc.Alert("✅ 분석 결과가 성공적으로 저장되었습니다!", color="success")
#         else:
#             return dbc.Alert("⚠️ 저장할 데이터가 없습니다.", color="warning")
#     return ""
