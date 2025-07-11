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
        html.Div([
            "LLM으로부터 받은 분석 결과(JSON 구조, 예시와 동일)를 아래에 붙여넣고 '저장하기' 버튼을 눌러주세요.",
            html.Br(),
            html.B("예시:"),
            dcc.Markdown('''
```
{
  "분석항목": [
    {"index": 1, "title": "캐롤 리프 모델 분석", "score": 4.3, "analysis": "심리적 안녕감이 높음", "evidence": "이력서 및 평가표 근거", "reliability": 4.5},
    ...
  ],
  "임원용_INSIGHT": [
    {"index": 1, "title": "조직/사업 전략과의 시너지 가능성", "analysis": "전략적 적합성 높음", "evidence": "경력기술서 근거", "reliability": 4.2},
    ...
  ],
  "HR담당자_포인트": [
    {"index": 1, "title": "입사 후 온보딩/적응 예상 이슈", "analysis": "적응력 우수 예상", "evidence": "면접평가표 근거", "reliability": 4.0},
    ...
  ]
}
```
''', style={"fontSize": "0.98rem", "background": "#f8f8f8", "padding": "8px", "borderRadius": "6px"})
        ], style={"marginBottom": "12px"}),
        dcc.Textarea(
            id="llm-result-input",
            placeholder="위 JSON 예시와 동일한 구조로 LLM 분석 결과를 붙여넣으세요...",
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
