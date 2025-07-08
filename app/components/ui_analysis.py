from dash import html, dcc
import plotly.express as px
import pandas as pd

# 후보자 비교/분석 컴포넌트 (Dash)
def AnalysisTab(candidates_df: pd.DataFrame) -> html.Div:
    # candidates_df: DataFrame (분석용)
    content = []
    content.append(html.H4("📊 후보자 비교/분석", style={"color": "#24278B", "marginBottom": "8px", "fontWeight": 800, "fontSize": "1.18rem"}))
    if not candidates_df.empty and len(candidates_df) > 1:
        content.append(html.H5("성장 잠재력 매트릭스 (Growth Potential Matrix)", style={"marginTop": "16px", "fontWeight": 700, "color": "#1A237E"}))
        content.append(html.Div("후보자들의 Digital Literacy와 개인적 성장(WB) 점수를 기준으로 잠재력을 시각화합니다. 원의 크기는 종합 점수를 나타냅니다.", style={"marginBottom": "12px", "color": "#555", "fontSize": "1.01rem"}))
        plot_df = candidates_df.dropna(subset=[
            'growth_potential_digital_literacy', 'growth_potential_wb_personal_growth', 'overall_score'
        ])
        if not plot_df.empty:
            fig = px.scatter(
                plot_df,
                x="growth_potential_digital_literacy",
                y="growth_potential_wb_personal_growth",
                size="overall_score",
                color="name",
                hover_name="name",
                hover_data={"position": True, "overall_score": True, "id": True},
                title="성장 잠재력 매트릭스",
                labels={
                    "growth_potential_digital_literacy": "Digital Literacy 역량 점수",
                    "growth_potential_wb_personal_growth": "개인적 성장 (WB) 점수",
                    "name": "후보자 이름"
                }
            )
            x_mean = plot_df['growth_potential_digital_literacy'].mean()
            y_mean = plot_df['growth_potential_wb_personal_growth'].mean()
            fig.add_vline(x=x_mean, line_dash="dash", line_color="gray")
            fig.add_hline(y=y_mean, line_dash="dash", line_color="gray")
            fig.update_layout(showlegend=True)
            content.append(dcc.Graph(figure=fig, style={"height": "600px", "background": "#fff", "borderRadius": "18px", "boxShadow": "0 2px 16px #005BAC11"}))
        else:
            content.append(html.Div([
                html.Span("⚠️", className="emoji"),
                " 시각화를 위한 데이터(성장 잠재력, 종합 점수)가 부족합니다."
            ], className="info-card", style={"color": "#B71C1C", "background": "#fff8f8"}))
    else:
        content.append(html.Div([
            html.Span("⚠️", className="emoji"),
            " 비교/분석을 위해서는 2명 이상의 후보자 데이터가 필요합니다."
        ], className="info-card", style={"color": "#B71C1C", "background": "#fff8f8"}))
    return html.Div(content)
