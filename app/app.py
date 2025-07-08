

# -------------------- IMPORTS/상수/초기화/콜백 등록 (최상단 1회 선언) --------------------
import os
import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
import re
from datetime import datetime
from app.prompt_logic import generate_custom_prompt
from app.ui_llm_input import render_llm_input_tab
from app.ui_candidate import render_candidate_management_tab, register_candidate_callbacks
from app.ui_analysis import render_analysis_tab
from app.ui_report import render_report_tab
from app.ui_settings import render_settings_tab
from .dash_prompt_generator import render_dash_prompt_generator
from .dash_prompt_guide import render_dash_prompt_guide
from .dash_prompt_copy import render_dash_copy_button
from app.db import init_db

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

# 앱 시작 시 DB 테이블 자동 생성
init_db()

# app 인스턴스는 단 한 번만 생성
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/custom.css'],
    suppress_callback_exceptions=True,
    assets_folder=ASSETS_PATH
)

# 후보자 관리 콜백 등록 (app 인스턴스 생성 후 반드시 1회)
register_candidate_callbacks(app)



app.layout = dbc.Container([
    html.Nav([
        html.Div([
            html.Span("SAMYANG", style={"fontWeight": 900, "fontSize": "1.6rem", "color": "#1A237E", "letterSpacing": "-1.5px", "fontFamily": "Pretendard, sans-serif"}),
            html.Br(),
            html.Span("KCI", style={"fontWeight": 700, "fontSize": "0.9rem", "color": "#1A237E", "letterSpacing": "0.1em", "fontFamily": "Pretendard, sans-serif"})
        ], style={"display": "inline-block", "verticalAlign": "middle"}),
    ], style={"display": "flex", "alignItems": "center", "padding": "18px 0 10px 0", "borderBottom": "1px solid #E0E4EA", "background": "#fff"}),
    html.Div([
        html.Div([
            html.H2([
                html.Span("📝", style={"fontSize": "1.5rem", "marginRight": "8px"}),
                "LLM 면접 분석 시스템"
            ], className="main-title", style={"fontWeight": 800, "fontSize": "2.1rem", "letterSpacing": "-1.2px", "marginBottom": "2px", "color": "#1A237E"}),
            html.Div("고객중심 · 혁신 · 신뢰 · 첨단소재 | 케미칼 · 바이오 · 소재", className="brand-slogan", style={"fontWeight": 500, "fontSize": "1.08rem", "color": "#005BAC", "letterSpacing": "-0.5px", "marginTop": "2px"}),
        ], style={"display": "flex", "flexDirection": "column", "justifyContent": "center", "marginLeft": "8px"})
    ], style={"display": "flex", "alignItems": "center", "gap": "18px", "marginBottom": "8px", "marginTop": "18px"}),
    html.Div([
        html.Img(src="/assets/industry_icon_chem.svg", style={"height": "32px", "marginRight": "12px"}),
        html.Img(src="/assets/industry_icon_bio.svg", style={"height": "32px", "marginRight": "12px"}),
        html.Div("케미칼", style={"color": "#00B894", "fontWeight": 600, "marginRight": "18px", "fontSize": "1.02rem"}),
        html.Div("바이오", style={"color": "#6C5CE7", "fontWeight": 600, "fontSize": "1.02rem"}),
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px", "marginLeft": "4px"}),
    html.Div(className="brand-gradient-bar"),
    dcc.Tabs([
        dcc.Tab(label="📋 프롬프트 생성", value="tab-prompt"),
        dcc.Tab(label="📝 LLM 분석 결과 입력", value="tab-result"),
        dcc.Tab(label="📑 보고서 생성", value="tab-report"),
        dcc.Tab(label="👤 후보자 조회 및 비교", value="tab-candidate"),
        dcc.Tab(label="⚙️ 설정", value="tab-settings"),
    ], id="main-tabs", value="tab-prompt", className="dash-tabs", style={"marginTop": "24px", "fontWeight": 600, "fontSize": "1.08rem", "letterSpacing": "-0.5px"}),
    html.Div(id='tab-content'),
], fluid=True, style={"maxWidth": "1200px", "margin": "0 auto", "padding": "0 0 64px 0", "background": "#F4F7FB"})



# 탭에 따라 tab-content에만 각 탭별 내용 렌더링 (후보자 관리도 포함)
@app.callback(Output('tab-content', 'children'), Input('main-tabs', 'value'))
def render_tab(tab: str):
    if tab == 'tab-prompt':
        return render_dash_prompt_generator()
    elif tab == 'tab-result':
        return html.Div([
            render_llm_input_tab()
        ], className="card section-card", style={"background": "#F8FAFF", "boxShadow": "0 2px 16px #005BAC11", "borderRadius": "18px", "padding": "32px 28px 24px 28px", "marginTop": "18px"})
    elif tab == 'tab-report':
        return render_report_tab()
    elif tab == 'tab-candidate':
        return render_candidate_management_tab()
    elif tab == 'tab-settings':
        return html.Div([
            render_settings_tab()
        ], className="card section-card", style={"background": "#F8FAFF", "boxShadow": "0 2px 16px #005BAC11", "borderRadius": "18px", "padding": "32px 28px 24px 28px", "marginTop": "18px"})
    return html.Div()

## 보고서 생성 탭 동적 콜백 제거 (ui_report.py에서 관리)

# 프롬프트 생성 콜백 복구

# 업로드 자료 체크박스/기타 입력 State 추가
@app.callback(
    [Output('prompt-generated-prompt-area', 'value'), Output('prompt-warning-message', 'children')],
    [Input('prompt-generate-prompt-btn', 'n_clicks')],
    [
        State('prompt-candidate-name-input', 'value'),
        State('prompt-candidate-org-input', 'value'),
        State('prompt-candidate-position-input', 'value'),
        State('prompt-candidate-date-input', 'value'),
        State('prompt-candidate-salary-input', 'value'),
        State('prompt-candidate-career-input', 'value'),
        State('prompt-upload-materials-0', 'value'),
        State('prompt-upload-materials-1', 'value'),
        State('prompt-upload-materials-2', 'value'),
        State('prompt-upload-materials-3', 'value'),
        State('prompt-upload-materials-4', 'value'),
        State('prompt-upload-materials-5', 'value'),
        State('prompt-upload-materials-6', 'value'),
        State('prompt-upload-materials-7', 'value'),
        State('prompt-upload-materials-8', 'value'),
        State('prompt-upload-materials-9', 'value'),
        State('prompt-upload-materials-10', 'value'),
        State('prompt-upload-materials-etc', 'value'),
    ]
)
def generate_prompt_callback(
    n_clicks: int,
    name: str,
    org: str,
    position: str,
    date: str,
    salary: str,
    career: str,
    mat0, mat1, mat2, mat3, mat4, mat5, mat6, mat7, mat8, mat9, mat10, etc_input
) -> tuple[str, str]:
    if not n_clicks:
        return '', ''
    # 업로드 자료 라벨 정의 (dash_prompt_generator.py와 동일 순서)
    material_labels = [
        "이력서",
        "면접평가표(1차)", "면접평가표(2차)", "면접평가표(3차)",
        "면접 녹취록(1차)", "면접 녹취록(2차)", "면접 녹취록(3차)",
        "포트폴리오", "평판보고서", "BIG5 성격유형검사표", "인성검사표"
    ]
    checked_materials = [label for val, label in zip([mat0, mat1, mat2, mat3, mat4, mat5, mat6, mat7, mat8, mat9, mat10], material_labels) if val]
    if etc_input and etc_input.strip():
        checked_materials.append(etc_input.strip())
    try:
        prompt = generate_custom_prompt(
            name or '',
            org or '',
            position or '',
            date or '',
            salary or '',
            career or '',
            upload_materials=checked_materials
        )
        return prompt, '프롬프트가 생성되었습니다.'
    except Exception as e:
        return '', f'프롬프트 생성 중 오류: {e}'

def normalize_date(date_str: str) -> str:
    """다양한 날짜 입력을 yyyy-mm-dd로 변환"""
    if not date_str:
        return ''
    date_str = date_str.strip().replace('.', '-').replace('/', '-').replace(' ', '')
    # 20250708 → 2025-07-08
    m = re.match(r'^(\d{4})[-]?(\d{2})[-]?(\d{2})$', date_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # 25-07-08 → 2025-07-08 (2000년대 가정)
    m = re.match(r'^(\d{2})[-]?(\d{2})[-]?(\d{2})$', date_str)
    if m:
        return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # yyyy-mm-dd 등
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    try:
        dt = datetime.strptime(date_str, '%y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    return date_str  # 변환 실패 시 원본 반환

@app.callback(
    [Output('llm-save-msg', 'children'),
     Output('llm-name-input', 'value'),
     Output('llm-result-input', 'value'),
     Output('llm-evaluator-input', 'value'),
     Output('llm-date-input', 'value')],
    [Input('llm-save-btn', 'n_clicks'), Input('llm-reset-btn', 'n_clicks')],
    [State('llm-name-input', 'value'),
     State('llm-result-input', 'value'),
     State('llm-evaluator-input', 'value'),
     State('llm-date-input', 'value')]
)
def llm_input_save_reset_callback(save_clicks, reset_clicks, name, result, evaluator, date):
    ctx = dash.callback_context
    if not ctx.triggered:
        return '', name, result, evaluator, date
    btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if btn_id == 'llm-reset-btn':
        return '', '', '', '', ''
    # 저장 버튼 클릭 시
    if not name or not result or not evaluator or not date:
        return '모든 항목을 입력하세요.', name, result, evaluator, date
    norm_date = normalize_date(date)
    # DB 저장 로직 추가
    from app.db import save_candidate_data
    save_candidate_data({
        "name": name,
        "raw_result": result,
        "evaluator": evaluator,
        "created_at": norm_date
    })
    msg = f'저장 완료! (날짜: {norm_date})'
    return msg, '', '', '', ''

if __name__ == '__main__':
    app.run_server(debug=True)
