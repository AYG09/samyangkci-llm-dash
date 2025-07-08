from dash import html
from .executive_graphs import executive_summary_gauge, executive_risk_bar

def render_executive_report(candidate):
    # candidate: dict 또는 pandas.Series
    score = candidate.get('overall_score', 4.3)
    risk = candidate.get('risk_score', 3.5)
    summary = candidate.get('executive_summary', '핵심 인사이트 요약이 없습니다.')
    # NoneType 안전 처리
    if score is None:
        score = 0
    if risk is None:
        risk = 0
    return html.Div([
        html.H4('임원용 핵심 INSIGHT', style={"fontWeight":700, "marginBottom":"18px"}),
        html.Div([
            executive_summary_gauge(score/5 if score is not None else 0),
            executive_risk_bar(risk),
        ], style={"display":"flex", "gap":"32px", "marginBottom":"18px"}),
        html.Div([
            html.H5('핵심 요약', style={"fontWeight":600, "marginBottom":"8px"}),
            html.P(summary, style={"fontSize":"1.08rem", "color":"#222"})
        ], style={"marginBottom":"18px"}),
        # 추가 인사이트/표/리스트 등 필요시 확장
    ], style={"background":"#fff", "borderRadius":"14px", "boxShadow":"0 2px 12px #005BAC11", "padding":"32px 28px 24px 28px", "marginTop":"18px"})
