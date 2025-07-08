from dash import html, dcc
import dash_bootstrap_components as dbc

# 설정 탭 컴포넌트 (Dash)
def SettingsTab():
    return html.Div([
        html.H4("⚙️ 설정", style={"color": "#24278B", "marginBottom": "8px", "fontWeight": 800, "fontSize": "1.18rem"}),
        html.Div([
            html.Span("ℹ️", className="emoji"),
            " DB 경로 등 환경설정 기능이 여기에 구현됩니다."
        ], className="info-card", style={"background": "#f7f8fa"}),
        html.H5("데이터베이스 설정", style={"marginTop": "18px", "fontWeight": 700, "color": "#1A237E"}),
        dcc.Input(
            id="db-path-input",
            value="candidates.db",
            type="text",
            disabled=True,
            className="dash-input",
            style={"width": "100%", "marginBottom": "16px"}
        ),
        html.H5("시스템 설정", style={"marginTop": "18px", "fontWeight": 700, "color": "#1A237E"}),
        dcc.Checklist(
            options=[{"label": "자동 백업 활성화", "value": "auto-backup"}],
            value=["auto-backup"],
            style={"marginBottom": "12px", "opacity": 0.5, "pointerEvents": "none"},
            inputClassName="dash-checkbox"
        ),
        dcc.Dropdown(
            id="language-select",
            options=[{"label": "한국어", "value": "한국어"}, {"label": "English", "value": "English"}],
            value="한국어",
            disabled=True,
            className="dash-dropdown",
            style={"width": "200px", "marginBottom": "16px"}
        ),
        html.Hr(),
        html.Div("설정 기능은 향후 업데이트에서 활성화됩니다.", style={"color": "#888", "fontSize": "0.98rem"})
    ])
