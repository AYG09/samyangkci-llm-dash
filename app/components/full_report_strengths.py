from dash import html, dcc
import dash_bootstrap_components as dbc
from collections import Counter
import re
import plotly.graph_objs as go

BRAND_GREEN = "#00B894"
BRAND_RED = "#d63031"
CARD_STYLE = {"marginBottom": "18px", "boxShadow": "0 2px 8px #005BAC22", "borderRadius": "12px"}

# 강점/약점 자동 추출 및 카드 렌더링

def extract_strengths_weaknesses(json_data: dict):
    strengths, weaknesses = [], []
    for item in json_data.get("분석항목", []):
        score = item.get("score", 0)
        analysis = item.get("analysis", "")
        if score >= 4.5 or ("강점" in analysis or "우수" in analysis or "높음" in analysis):
            strengths.append(item)
        elif score <= 3.0 or ("주의" in analysis or "부족" in analysis or "리스크" in analysis or "보완" in analysis):
            weaknesses.append(item)
    return strengths, weaknesses

def generate_summary(items, label):
    """
    강점/약점 리스트에서 상위 1~2개 항목을 조합해 요약문장 생성
    """
    if not items:
        return f"주요 {label}이(가) 뚜렷하게 드러나지 않습니다."
    top_titles = [item.get("title", "-") for item in items[:2]]
    return f"핵심 {label}: {', '.join(top_titles)}"

def extract_keywords(items):
    """
    analysis 텍스트에서 주요 키워드 추출(빈도순)
    """
    texts = ' '.join([item.get("analysis", "") for item in items])
    # 한글/영문 단어만 추출, 2글자 이상
    words = re.findall(r"[가-힣a-zA-Z]{2,}", texts)
    counter = Counter(words)
    return counter.most_common(7)

def render_keyword_barchart(keywords, color):
    if not keywords:
        return html.Div("키워드 데이터 없음", style={"fontSize": "0.95rem", "color": "#888"})
    words, counts = zip(*keywords)
    fig = go.Figure(go.Bar(
        x=counts, y=words, orientation='h', marker_color=color
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0), height=180, width=320,
        xaxis=dict(showticklabels=False), yaxis=dict(tickfont=dict(size=13)),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return html.Div([
        html.Div("주요 키워드", style={"fontWeight": 600, "marginBottom": "4px", "fontSize": "0.97rem"}),
        html.Div(dcc.Graph(figure=fig, config={"displayModeBar": False}), style={"overflow": "hidden"})
    ])

def render_accordion(items, color):
    if not items:
        return html.Div("데이터 없음", style={"fontSize": "0.95rem", "color": "#888"})
    return dbc.Accordion([
        dbc.AccordionItem([
            html.B(item.get("title", "-"), style={"color": color}),
            html.Div(item.get("analysis", "-"), style={"marginTop": "4px", "fontSize": "0.97rem"}),
            html.Div(item.get("evidence", ""), style={"marginTop": "2px", "fontSize": "0.93rem", "color": "#888"})
        ], title=item.get("title", "-")) for item in items
    ], start_collapsed=True, style={"marginTop": "8px"})

def render_strengths_weaknesses_cards(json_data: dict):
    strengths, weaknesses = extract_strengths_weaknesses(json_data)
    # 요약문장
    strengths_summary = generate_summary(strengths, "강점")
    weaknesses_summary = generate_summary(weaknesses, "약점")
    # 리스트(ul/li) 형태로 강점/약점 주요 내용 정리
    def make_list(items, color):
        if not items:
            return html.Ul([
                html.Li(f"주요 내용이 없습니다.", style={"color": color, "fontWeight": 500})
            ], style={"margin": "0 0 0 1.2em", "fontSize": "1rem"})
        return html.Ul([
            html.Li([
                html.Strong(item.get("title", "-"), style={"color": color, "fontWeight": 700}),
                ": ",
                html.Span(item.get("analysis", "-"), style={"color": "#444", "marginLeft": "2px"})
            ], style={"marginBottom": "0.5em"}) for item in items[:4]
        ], style={"margin": "0 0 0 1.2em", "fontSize": "1rem"})
    return html.Div([
        html.Div([
            html.Div([
                html.H5("강점 (Strengths)", style={"color": BRAND_GREEN, "fontWeight": 700, "marginBottom": "6px"}),
                html.Div(strengths_summary, style={"marginBottom": "8px", "fontSize": "1.05rem", "fontWeight": 600}),
                make_list(strengths, BRAND_GREEN),
            ], style={"flex": 1, "padding": "18px 14px 14px 14px", "background": "#F8FFF8", "borderRadius": "12px", "boxShadow": "0 2px 8px #005BAC22"}),
            html.Div([
                html.H5("약점 (Areas for Development)", style={"color": BRAND_RED, "fontWeight": 700, "marginBottom": "6px"}),
                html.Div(weaknesses_summary, style={"marginBottom": "8px", "fontSize": "1.05rem", "fontWeight": 600}),
                make_list(weaknesses, BRAND_RED),
            ], style={"flex": 1, "padding": "18px 14px 14px 14px", "background": "#FFF8F8", "borderRadius": "12px", "boxShadow": "0 2px 8px #005BAC22"})
        ], style={"display": "flex", "gap": "32px", "marginBottom": "18px"}),
        # SWOT 그래프는 하단에 작게 배치
        html.Div(render_swot_barchart(strengths, weaknesses), style={"marginTop": "8px"})
    ])

def render_swot_barchart(strengths, weaknesses):
    # 강점/약점 각각 상위 5개 title/score 추출
    s_titles = [item.get("title", "-") for item in strengths[:5]]
    s_scores = [item.get("score", 0) for item in strengths[:5]]
    w_titles = [item.get("title", "-") for item in weaknesses[:5]]
    w_scores = [item.get("score", 0) for item in weaknesses[:5]]
    # y축: 강점+약점 항목명(좌: 강점, 우: 약점)
    y_labels = s_titles + w_titles
    x_values = s_scores + [-w for w in w_scores]  # 약점은 음수로 표현
    colors = [BRAND_GREEN]*len(s_titles) + [BRAND_RED]*len(w_titles)
    fig = go.Figure(go.Bar(
        x=x_values, y=y_labels,
        orientation='h', marker_color=colors,
        text=[f"{v:.1f}" for v in s_scores] + [f"{v:.1f}" for v in w_scores],
        textposition="outside"
    ))
    fig.update_layout(
        title="SWOT: 강점/약점 시각화",
        margin=dict(l=0, r=0, t=30, b=0), height=320, width=520,
        xaxis=dict(showticklabels=False, zeroline=True, zerolinewidth=2, zerolinecolor="#888"),
        yaxis=dict(tickfont=dict(size=13)),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
    )
    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False})
    ], style={"marginBottom": "18px"})
