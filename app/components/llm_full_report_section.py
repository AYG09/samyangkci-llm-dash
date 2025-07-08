from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from app.llm_report_parser import parse_llm_report

BRAND_BLUE = "#005BAC"
BRAND_GREEN = "#00B894"
BRAND_PURPLE = "#6C5CE7"
BRAND_NAVY = "#1A237E"

# LLM 분석결과 파싱 후 항목별 시각화 섹션 생성

def render_llm_full_report_section(raw_result):
    try:
        parsed = parse_llm_report(raw_result)
    except Exception:
        parsed = []
    if not parsed:
        return html.Div("LLM 분석결과에서 항목별 정보를 추출할 수 없습니다.", style={"color": "#888", "textAlign": "center", "margin": "32px 0 18px 0", "fontSize": "1.05rem"})

    # 점수/신뢰도 Bar 차트
    bar_labels = [f"({item['index']}) {item['title']}" for item in parsed]
    bar_scores = [item['score'] if item['score'] is not None else 0 for item in parsed]
    bar_reliabilities = [item['reliability'] if item['reliability'] is not None else 0 for item in parsed]
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=bar_labels,
        y=bar_scores,
        name="점수",
        marker_color=BRAND_BLUE,
        text=bar_scores,
        textposition="auto",
    ))
    bar_fig.add_trace(go.Bar(
        x=bar_labels,
        y=bar_reliabilities,
        name="신뢰도",
        marker_color=BRAND_GREEN,
        text=bar_reliabilities,
        textposition="auto",
    ))
    bar_fig.update_layout(
        barmode='group',
        title="항목별 점수/신뢰도",
        yaxis={"range": [0, 10], "title": "점수/신뢰도"},
        xaxis={"title": "항목"},
        plot_bgcolor="#F8FAFF",
        paper_bgcolor="#F8FAFF",
        font={"family": "Pretendard, sans-serif"},
        height=420,
        margin={"b": 120}
    )

    # 항목별 자연어 분석/산출근거 카드
    analysis_cards = []
    for item in parsed:
        analysis_cards.append(
            dbc.Card([
                dbc.CardHeader(f"({item['index']}) {item['title']}", style={"fontWeight": 700, "fontSize": "1.04rem", "color": BRAND_BLUE}),
                dbc.CardBody([
                    html.Div([
                        html.Span("점수: ", style={"fontWeight": 600}),
                        html.Span(item['score'] if item['score'] is not None else "-"),
                        html.Span("  |  신뢰도: ", style={"fontWeight": 600, "marginLeft": "8px"}),
                        html.Span(item['reliability'] if item['reliability'] is not None else "-")
                    ], style={"marginBottom": "6px", "fontSize": "1.01rem"}),
                    html.Div([
                        html.Span("자연어 분석: ", style={"fontWeight": 600}),
                        html.Span(item['analysis'] or "-")
                    ], style={"marginBottom": "6px", "fontSize": "1.01rem"}),
                    html.Div([
                        html.Span("점수 산출근거: ", style={"fontWeight": 600}),
                        html.Span(item['evidence'] or "-")
                    ], style={"fontSize": "0.99rem", "color": "#444"})
                ])
            ], style={"marginBottom": "14px", "boxShadow": "0 2px 8px #005BAC11", "borderRadius": "8px"})
        )

    return html.Div([
        html.H4("항목별 점수/신뢰도 (자동 추출)", style={"fontWeight": 700, "fontSize": "1.12rem", "color": BRAND_BLUE, "marginBottom": "12px"}),
        dcc.Graph(figure=bar_fig, config={"displayModeBar": False}, style={"marginBottom": "18px"}),
        html.H4("항목별 자연어 분석/산출근거", style={"fontWeight": 700, "fontSize": "1.12rem", "color": BRAND_BLUE, "marginBottom": "12px"}),
        html.Div(analysis_cards)
    ], style={"marginTop": "24px", "marginBottom": "12px"})
