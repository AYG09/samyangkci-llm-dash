
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from app.components.llm_full_report_section import render_llm_full_report_section
from app.utils import safe_num

# 브랜드 컬러
BRAND_BLUE = "#005BAC"
BRAND_GREEN = "#00B894"
BRAND_PURPLE = "#6C5CE7"
BRAND_NAVY = "#1A237E"

# 종합 분석 풀버전 보고서 렌더링

def render_full_report(candidate):
    # --- Big5/성장동기 등 확장 해석 매트릭스 카드 ---
    def get_big5_level(score):
        if score is None:
            return "-"
        if score >= 65:
            return "매우 높음"
        elif score >= 55:
            return "높음"
        elif score >= 45:
            return "보통"
        else:
            return "낮음"

    # 예시: Big5, 성장동기, 평판 등 주요 특성 값 추출 (필드명은 실제 데이터에 맞게 조정)
    big5_c = safe_num(candidate.get('big5_c'), 0)  # 규범지향성(성실성)
    big5_a = safe_num(candidate.get('big5_a'), 0)  # 대인수용성(친화성)
    growth_motivation = safe_num(candidate.get('growth_motivation'), 0)  # 성장동기(0~100)
    flexibility = safe_num(candidate.get('flexibility'), 0)  # 변화유연성(0~100)
    rep_report = candidate.get('reputation_report', '')  # 평판 보고서(텍스트)

    # 매트릭스 카드(2x2) 구성
    matrix_card = dbc.Card([
        dbc.CardHeader("후보자 핵심 특성 매트릭스", style={"fontWeight": 700, "fontSize": "1.08rem", "color": BRAND_BLUE}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5("책임감/성실성 (C-Factor)", style={"fontWeight": 600, "fontSize": "1.01rem"}),
                    html.Div([
                        html.I(className="fas fa-clipboard-check me-2", style={"color": "#0984e3"}),
                        f"NEO-PI Big5 규범지향성(C): {big5_c}점 ",
                        dbc.Badge(get_big5_level(big5_c), color="primary", className="ms-2")
                    ], style={"marginBottom": "8px"})
                ], md=6),
                dbc.Col([
                    html.H5("성장 잠재력 (Potential)", style={"fontWeight": 600, "fontSize": "1.01rem"}),
                    html.Div([
                        html.I(className="fas fa-seedling me-2", style={"color": "#00B894"}),
                        "총동기(ToMo) 모델 분석: 성장동기 ",
                        dbc.Progress(label="성장동기 매우 높음" if growth_motivation and growth_motivation >= 80 else "성장동기 보통", value=growth_motivation or 0, color="success", style={"height": "18px", "minWidth": "120px"})
                    ], style={"marginBottom": "8px"})
                ], md=6)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    html.H5("협력적/안정적 (A-Factor)", style={"fontWeight": 600, "fontSize": "1.01rem"}),
                    html.Div([
                        html.I(className="fas fa-users me-2", style={"color": "#6C5CE7"}),
                        f"NEO-PI Big5 대인수용성(A): {big5_a}점 ",
                        dbc.Badge(get_big5_level(big5_a), color="info", className="ms-2")
                    ], style={"marginBottom": "8px"})
                ], md=6),
                dbc.Col([
                    html.H5("변화 유연성 (Flexibility)", style={"fontWeight": 600, "fontSize": "1.01rem"}),
                    html.Div([
                        html.I(className="fas fa-exclamation-circle me-2", style={"color": "#FFA500"}),
                        f"평판보고서: {rep_report if rep_report else '정보 없음'} ",
                        dbc.Badge("주의 필요" if flexibility < 40 else "양호", color="warning" if flexibility < 40 else "success", className="ms-2")
                    ], style={"marginBottom": "8px"})
                ], md=6)
            ])
        ])
    ], style={"marginBottom": "18px", "boxShadow": "0 2px 8px #005BAC22", "borderRadius": "12px"})
    # --- 동적 요약문 생성 함수 ---
    def get_uwes_level(score):
        if score is None:
            return None
        if score >= 5.0:
            return "매우 높음"
        elif score >= 4.0:
            return "높음"
        elif score >= 2.5:
            return "보통"
        else:
            return "낮음"

    def get_burnout_level(score):
        if score is None:
            return None
        if score <= 3.9:
            return "안전"
        elif score <= 6.9:
            return "주의"
        else:
            return "위험"

    def generate_psychological_summary(uwes, burnout):
        uwes_level = get_uwes_level(uwes)
        burnout_level = get_burnout_level(burnout)
        # 템플릿 매트릭스 (주요 조합)
        templates = {
            ("매우 높음", "안전"): "높은 몰입도로 뛰어난 성과를 창출하면서도, 번아웃 위험은 매우 낮게 관리되어 장기적인 기여가 기대되는 '지속 가능한 고성과자' 유형입니다.",
            ("높음", "안전"): "긍정적 워크에너지가 충만한 상태로, 현재 직무에 대한 강한 자부심과 활력을 바탕으로 안정적인 성과를 낼 가능성이 높습니다.",
            ("보통", "안전"): "심리적으로 안정된 상태에서 맡은 바 역할을 꾸준히 수행하는 '안정적인 실무자' 유형입니다. 더 높은 성과를 위한 동기부여 방안을 고려해볼 수 있습니다.",
            ("낮음", "안전"): "번아웃 위험은 없으나 업무에 대한 몰입도와 열정이 다소 낮은 상태로, 새로운 동기부여나 역할 재설정이 필요한 '안주형' 상태일 수 있습니다.",
            ("매우 높음", "주의"): "일에 대한 높은 열정과 책임감으로 성과를 내고 있으나, 약간의 심리적 압박을 느끼는 '열정적인 노력가' 유형입니다. 스트레스 관리를 지원하면 더 나은 성과가 기대됩니다.",
            ("높음", "주의"): "높은 성과를 위해 스스로를 채찍질하고 있을 가능성이 있습니다. 현재의 열정이 소진으로 이어지지 않도록 예방적 차원의 관심이 필요합니다.",
            ("보통", "주의"): "업무 부담이나 스트레스로 인해 점차 몰입도가 저하되고 있는 '잠재적 소진 그룹'일 수 있습니다. 원인 파악 및 해결을 위한 면담이 필요한 시점입니다.",
            ("낮음", "주의"): "업무에 대한 흥미를 잃고 심리적 소진을 경험하고 있는 '무기력 상태'일 가능성이 있습니다. 이탈 위험을 방지하기 위한 관심과 지원이 필요합니다.",
            ("매우 높음", "위험"): "현재 높은 열정과 책임감으로 업무에 몰두하고 있으나, 번아웃 위험도가 '위험' 수준에 근접하여 소진 예방을 위한 즉각적인 관심과 지원이 필수적인 상태입니다.",
            ("높음", "위험"): "자기희생적 방식으로 성과를 창출하고 있을 가능성이 높습니다. 단기 성과는 뛰어나나, 장기적인 성과 저하 및 이탈 리스크가 매우 큰 유형입니다.",
            ("보통", "위험"): "업무에 대한 책임감은 남아있으나 심리적 에너지가 완전히 고갈된 '소진 상태'로 보입니다. 전문적인 상담이나 휴식 등 즉각적이고 적극적인 조치가 필요합니다.",
            ("낮음", "위험"): "업무에 대한 의미를 완전히 잃고 심각한 심리적 소진 상태에 처한 '고위험 이탈 그룹'입니다. 즉각적인 면담과 지원이 필수적입니다.",
        }
        key = (uwes_level, burnout_level)
        return templates.get(key, "심리 지표 해석을 위한 데이터가 부족합니다.")

    name = candidate.get('name', '-')
    position = candidate.get('position', '-')
    created_at = candidate.get('created_at', '-')
    overall_score = safe_num(candidate.get('overall_score'), 0)
    digital_lit = safe_num(candidate.get('growth_potential_digital_literacy'), 0)
    personal_growth = safe_num(candidate.get('growth_potential_wb_personal_growth'), 0)
    teamwork = safe_num(candidate.get('teamwork'), 0)
    problem_solving = safe_num(candidate.get('problem_solving'), 0)
    communication = safe_num(candidate.get('communication'), 0)
    reliability = safe_num(candidate.get('reliability'), 0)
    general_report = candidate.get('general_report', '-')
    raw_result = candidate.get('raw_result', '-')
    evaluator = candidate.get('evaluator', '-')

    # 점수 항목 및 값 리스트
    score_items = [
        ("종합 점수", overall_score),
        ("디지털 리터러시", digital_lit),
        ("자기주도 성장", personal_growth),
        ("팀워크", teamwork),
        ("문제해결력", problem_solving),
        ("커뮤니케이션", communication),
        ("전체 분석 신뢰도(%)", reliability)
    ]

    # 1. 점수 표 (신뢰도 포함)
    score_table = dash_table.DataTable(
        columns=[{"name": "항목", "id": "item"}, {"name": "점수", "id": "score"}],
    data=[{"item": item, "score": score} for item, score in score_items],
        style_cell={"fontFamily": "Pretendard, sans-serif", "fontSize": "1.01rem", "textAlign": "center"},
        style_header={"backgroundColor": "#F4F7FB", "fontWeight": 700},
        style_data={"backgroundColor": "#fff"},
        style_table={"width": "480px", "margin": "0 auto 18px auto"},
    )


    # 2. Bar 그래프 (항목별 점수, 값이 하나라도 있으면 출력, 없으면 안내)
    # 2. Bar 그래프 (신뢰도 제외, 역량만)
    bar_labels = [item for item, _ in score_items[1:-1]]
    bar_values = [score for _, score in score_items[1:-1]]
    bar_fig = go.Figure()
    has_bar_data = any(score for _, score in score_items[1:-1])
    if has_bar_data:
        bar_fig.add_trace(go.Bar(
            x=bar_labels,
            y=bar_values,
            marker_color=[BRAND_BLUE, BRAND_GREEN, BRAND_PURPLE, BRAND_NAVY, "#FFA500"],
            text=bar_values,
            textposition="auto",
        ))
    bar_fig.update_layout(
        title="핵심 역량 점수",
        yaxis={"range": [0, 100], "title": "점수"},
        xaxis={"title": "항목"},
        plot_bgcolor="#F8FAFF",
        paper_bgcolor="#F8FAFF",
        font={"family": "Pretendard, sans-serif"},
        height=320,
    )
    bar_graph_component = (
        dcc.Graph(figure=bar_fig, config={"displayModeBar": False}, style={"marginBottom": "18px"})
        if has_bar_data
        else html.Div("핵심 역량 점수 데이터가 없습니다.", style={"color": "#888", "textAlign": "center", "margin": "32px 0 18px 0", "fontSize": "1.05rem"})
    )

    # 3. Radar(레이더) 차트 (값이 하나라도 있으면 출력, 없으면 안내)
    radar_labels = bar_labels
    radar_values = bar_values
    radar_fig = go.Figure()
    has_radar_data = any(score for _, score in score_items[1:-1])
    if has_radar_data:
        radar_fig.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill='toself',
            name='역량 분포',
            line_color=BRAND_BLUE,
            marker_color=BRAND_BLUE
        ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="역량 분포(레이더 차트)",
        plot_bgcolor="#F8FAFF",
        paper_bgcolor="#F8FAFF",
        font={"family": "Pretendard, sans-serif"},
        height=340,
    )
    radar_graph_component = (
        dcc.Graph(figure=radar_fig, config={"displayModeBar": False}, style={"marginBottom": "18px"})
        if has_radar_data
        else html.Div("역량 분포(레이더 차트) 데이터가 없습니다.", style={"color": "#888", "textAlign": "center", "margin": "32px 0 18px 0", "fontSize": "1.05rem"})
    )

    # --- Gemini BI/UX 고도화: 상단 프로필 카드 + 좌/우 그리드 + 게이지 차트 ---
    profile_card = dbc.Card([
        dbc.CardBody([
            html.H3(f"{name}", style={"fontWeight": 800, "fontSize": "1.25rem", "color": BRAND_BLUE}),
            html.Div(f"지원직무: {position}", style={"fontSize": "1.05rem", "color": "#333", "marginBottom": "2px"}),
            html.Div(f"분석일: {created_at}", style={"fontSize": "0.98rem", "color": "#888"}),
            html.H4(f"최종 점수: {overall_score} / 10", style={"fontWeight": 700, "color": BRAND_NAVY, "marginTop": "10px"}),
            html.Div([
                dbc.Badge("강력 추천", color="primary", className="me-1", style={"fontSize": "1.01rem", "padding": "7px 14px"}),
                dbc.Badge("신뢰도: {}%".format(reliability), color="success", className="me-1", style={"fontSize": "1.01rem", "padding": "7px 14px"})
            ], style={"marginTop": "8px"}),
            html.Div("핵심 역량: 디지털, 성장, 팀워크, 문제해결, 커뮤니케이션", style={"fontSize": "0.99rem", "color": "#555", "marginTop": "8px"})
        ])
    ], style={"boxShadow": "0 2px 12px #005BAC22", "borderRadius": "12px", "marginBottom": "18px", "padding": "8px 0"})

    # Gemini BI/UX: 일 몰입도(UWES) + 번아웃 위험도 게이지 병렬 배치
    uwes_score = safe_num(candidate.get('uwes'), 5.17)
    burnout_score = safe_num(candidate.get('burnout_risk'), 2.5)
    # UWES 게이지
    uwes_gauge = dcc.Graph(
        figure=go.Figure(go.Indicator(
            mode="gauge+number",
            value=uwes_score,
            title={'text': "일 몰입도 (UWES)", 'font': {'size': 20}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 6], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "rgba(49, 130, 189, 0.7)"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray"
            }
        )),
        config={'displayModeBar': False},
        style={"height": "220px", "marginBottom": "12px"}
    )
    # 번아웃 위험도 게이지
    burnout_gauge = dcc.Graph(
        figure=go.Figure(go.Indicator(
            mode="gauge+number",
            value=burnout_score,
            title={'text': "번아웃 위험도", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 10]},
                'steps': [
                    {'range': [0, 4], 'color': '#90ee90'},
                    {'range': [4, 7], 'color': '#ffd700'},
                    {'range': [7, 10], 'color': '#ff7f7f'},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': burnout_score
                },
                'bar': {'color': 'black'}
            }
        )),
        config={'displayModeBar': False},
        style={"height": "220px", "marginBottom": "12px"}
    )
    # 게이지 2개 병렬 배치
    gauge_row = dbc.Row([
        dbc.Col(uwes_gauge, md=6),
        dbc.Col(burnout_gauge, md=6)
    ], className="mb-3")

    # --- 동적 요약문 생성 및 카드 시각화 ---
    summary_text = generate_psychological_summary(uwes_score, burnout_score)
    summary_card = dbc.Alert([
        html.H5("Key Psychological Indicators: 지속 가능한 고성과자 (Sustainable High-Performer)", style={"fontWeight": 700, "fontSize": "1.08rem", "marginBottom": "8px"}),
        html.I(className="fas fa-battery-full me-2", style={"color": "#0984e3", "fontSize": "1.2em"}),
        html.I(className="fas fa-shield-alt me-2", style={"color": "#00B894", "fontSize": "1.2em"}),
        html.Span(summary_text, style={"marginLeft": "8px", "fontSize": "1.04rem"})
    ], color="info", style={"marginBottom": "18px", "boxShadow": "0 2px 8px #005BAC22"})

    # 좌: 프로필+게이지+요약카드+매트릭스, 우: 기존 점수표/차트/분석
    return dbc.Row([
        dbc.Col([
            profile_card,
            summary_card,
            gauge_row,
            matrix_card
        ], width=4),
        dbc.Col([
            html.Div([
                score_table,
                bar_graph_component,
                radar_graph_component,
                render_llm_full_report_section(raw_result),
                html.Div([
                    html.H4("전체 분석 신뢰도(%)", style={"fontWeight": 600, "fontSize": "1.08rem", "marginTop": "18px", "marginBottom": "6px", "color": BRAND_BLUE}),
                    html.Div(f"{reliability} %", style={"fontSize": "1.08rem", "color": "#1A237E", "fontWeight": 700})
                ], style={"marginTop": "12px"}),
                html.Div([
                    html.H4("요약", style={"fontWeight": 600, "fontSize": "1.08rem", "marginTop": "18px", "marginBottom": "6px"}),
                    html.Div(general_report or "요약 내용이 없습니다.", style={"whiteSpace": "pre-line", "fontSize": "1.04rem", "color": "#222"})
                ], style={"marginTop": "12px"}),
                html.Div([
                    html.H4("LLM 분석 원문", style={"fontWeight": 600, "fontSize": "1.08rem", "marginTop": "18px", "marginBottom": "6px"}),
                    html.Div(raw_result or "원문 데이터가 없습니다.", style={"whiteSpace": "pre-line", "fontSize": "1.01rem", "color": "#444", "background": "#F4F7FB", "padding": "10px 14px", "borderRadius": "6px"})
                ], style={"marginTop": "12px"}),
                html.Div([
                    html.H4("평가자 코멘트", style={"fontWeight": 600, "fontSize": "1.08rem", "marginTop": "18px", "marginBottom": "6px"}),
                    html.Div(evaluator or "평가자 정보가 없습니다.", style={"fontSize": "1.01rem", "color": "#444"})
                ], style={"marginTop": "12px"}),
            ], style={"padding": "8px 8px 8px 8px", "background": "#F8FAFF", "borderRadius": "10px", "boxShadow": "0 2px 8px #005BAC11"})
        ], width=8)
    ], style={"marginTop": "8px", "marginBottom": "8px"})
