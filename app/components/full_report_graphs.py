from dash import dcc, html
import plotly.graph_objs as go

BRAND_BLUE = "#005BAC"

# 분석항목별 점수 레이더 차트

def render_analysis_graphs(json_data: dict):
    items = json_data.get("분석항목", [])
    labels = [x.get("title", "-") for x in items]
    values = [x.get("score", 0) for x in items]
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        name='분석항목 점수',
        line_color=BRAND_BLUE
    ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        title="분석항목별 점수(레이더 차트)",
        plot_bgcolor="#F8FAFF",
        paper_bgcolor="#F8FAFF",
        font={"family": "Pretendard, sans-serif"},
        height=340,
    )
    return dcc.Graph(figure=radar_fig, config={"displayModeBar": False}, style={"marginBottom": "18px"})
