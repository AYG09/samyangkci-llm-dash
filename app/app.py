# -------------------- IMPORTS/상수/초기화/콜백 등록 (최상단 1회 선언) --------------------
import os
import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import re
from datetime import datetime
import uuid

from app.prompt_logic import generate_custom_prompt
from app.ui_llm_input import render_llm_input_tab
from app.ui_candidate import (
    render_candidate_management_tab,
    register_candidate_callbacks,
)
from app.ui_report import render_report_tab, update_report_content
from app.ui_settings import render_settings_tab
from .dash_prompt_generator import render_dash_prompt_generator
from app.db import init_db, load_candidates
from .config import MATERIAL_LABELS

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

# 앱 시작 시 DB 테이블 자동 생성
init_db()

# app 인스턴스는 단 한 번만 생성
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/custom.css"],
    suppress_callback_exceptions=True,
    assets_folder=ASSETS_PATH,
)

# 후보자 관리 콜백 등록 (app 인스턴스 생성 후 반드시 1회)
register_candidate_callbacks(app)


app.layout = dbc.Container(
    [
        html.Nav(
            [
                html.Div(
                    [
                        html.Span(
                            "SAMYANG",
                            style={
                                "fontWeight": 900,
                                "fontSize": "1.6rem",
                                "color": "#1A237E",
                                "letterSpacing": "-1.5px",
                                "fontFamily": "Pretendard, sans-serif",
                            },
                        ),
                        html.Br(),
                        html.Span(
                            "KCI",
                            style={
                                "fontWeight": 700,
                                "fontSize": "0.9rem",
                                "color": "#1A237E",
                                "letterSpacing": "0.1em",
                                "fontFamily": "Pretendard, sans-serif",
                            },
                        ),
                    ],
                    style={"display": "inline-block", "verticalAlign": "middle"},
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "padding": "18px 0 10px 0",
                "borderBottom": "1px solid #E0E4EA",
                "background": "#fff",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H2(
                            [
                                html.Span(
                                    "📝",
                                    style={"fontSize": "1.5rem", "marginRight": "8px"},
                                ),
                                "LLM 면접 분석 시스템",
                            ],
                            className="main-title",
                            style={
                                "fontWeight": 800,
                                "fontSize": "2.1rem",
                                "letterSpacing": "-1.2px",
                                "marginBottom": "2px",
                                "color": "#1A237E",
                            },
                        ),
                        html.Div(
                            "고객중심 · 혁신 · 신뢰 · 첨단소재 | 케미칼 · 바이오 · 소재",
                            className="brand-slogan",
                            style={
                                "fontWeight": 500,
                                "fontSize": "1.08rem",
                                "color": "#005BAC",
                                "letterSpacing": "-0.5px",
                                "marginTop": "2px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "marginLeft": "8px",
                    },
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "gap": "18px",
                "marginBottom": "8px",
                "marginTop": "18px",
            },
        ),
        html.Div(
            [
                html.Img(
                    src="/assets/industry_icon_chem.svg",
                    style={"height": "32px", "marginRight": "12px"},
                ),
                html.Img(
                    src="/assets/industry_icon_bio.svg",
                    style={"height": "32px", "marginRight": "12px"},
                ),
                html.Div(
                    "케미칼",
                    style={
                        "color": "#00B894",
                        "fontWeight": 600,
                        "marginRight": "18px",
                        "fontSize": "1.02rem",
                    },
                ),
                html.Div(
                    "바이오",
                    style={
                        "color": "#6C5CE7",
                        "fontWeight": 600,
                        "fontSize": "1.02rem",
                    },
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "4px",
                "marginLeft": "4px",
            },
        ),
        html.Div(className="brand-gradient-bar"),
        dcc.Tabs(
            [
                dcc.Tab(label="📋 프롬프트 생성", value="tab-prompt"),
                dcc.Tab(label="📝 LLM 분석 결과 입력", value="tab-result"),
                dcc.Tab(label="📑 보고서 생성", value="tab-report"),
                dcc.Tab(label="👤 후보자 조회 및 비교", value="tab-candidate"),
                dcc.Tab(label="⚙️ 설정", value="tab-settings"),
            ],
            id="main-tabs",
            value="tab-prompt",
            className="dash-tabs",
            style={
                "marginTop": "24px",
                "fontWeight": 600,
                "fontSize": "1.08rem",
                "letterSpacing": "-0.5px",
            },
        ),
        html.Div(id="tab-content"),
    ],
    fluid=True,
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "0 0 64px 0",
        "background": "#F4F7FB",
    },
)


# 탭에 따라 tab-content에만 각 탭별 내용 렌더링 (후보자 관리도 포함)
@app.callback(Output("tab-content", "children"), Input("main-tabs", "value"))
def render_tab(tab: str):
    if tab == "tab-prompt":
        return render_dash_prompt_generator()
    elif tab == "tab-result":
        return html.Div(
            [render_llm_input_tab()],
            className="card section-card",
            style={
                "background": "#F8FAFF",
                "boxShadow": "0 2px 16px #005BAC11",
                "borderRadius": "18px",
                "padding": "32px 28px 24px 28px",
                "marginTop": "18px",
            },
        )
    elif tab == "tab-report":
        return render_report_tab()
    elif tab == "tab-candidate":
        return render_candidate_management_tab()
    elif tab == "tab-settings":
        return html.Div(
            [render_settings_tab()],
            className="card section-card",
            style={
                "background": "#F8FAFF",
                "boxShadow": "0 2px 16px #005BAC11",
                "borderRadius": "18px",
                "padding": "32px 28px 24px 28px",
                "marginTop": "18px",
            },
        )
    return html.Div()


# 보고서 후보자 목록 동적 로딩 콜백
@app.callback(
    Output("report-candidate-dropdown", "options"), Input("main-tabs", "value")
)
def update_candidate_dropdown(tab_value):
    if tab_value == "tab-report":
        candidates = load_candidates()
        if not candidates.empty:
            options = [
                {"label": row["name"], "value": row["id"]}
                for _, row in candidates.iterrows()
            ]
            return options
    return []


# 보고서 생성 콜백 (드롭다운 선택 시 자동 실행)
@app.callback(
    Output("report-content-area", "children"),
    [Input("report-candidate-dropdown", "value")],
    [State("report-type-dropdown", "value")],
)
def report_callback(candidate_id, report_type):
    if not candidate_id:
        return html.Div(
            "상단 드롭다운에서 후보자를 선택하면 보고서가 표시됩니다.",
            className="text-center text-muted mt-5",
            style={"fontSize": "1.1rem"}
        )
    return update_report_content(candidate_id, report_type)


# 보고서 탭을 클릭할 때마다 드롭다운 선택을 초기화하는 콜백
@app.callback(
    Output('report-candidate-dropdown', 'value'),
    Input('main-tabs', 'value'),
    prevent_initial_call=True
)
def reset_report_dropdown(tab_value):
    """보고서 탭으로 전환 시 드롭다운 선택을 초기화합니다."""
    if tab_value == 'tab-report':
        return None  # 드롭다운 선택을 지웁니다.
    return dash.no_update


# 프롬프트 생성 콜백 복구


# 업로드 자료 체크박스/기타 입력 State 추가
@app.callback(
    [
        Output("prompt-generated-prompt-area", "value"),
        Output("prompt-warning-message", "children"),
    ],
    [Input("prompt-generate-prompt-btn", "n_clicks")],
    [
        State("prompt-candidate-name-input", "value"),
        State("prompt-candidate-org-input", "value"),
        State("prompt-candidate-position-input", "value"),
        State("prompt-candidate-date-input", "value"),
        State("prompt-candidate-salary-input", "value"),
        State("prompt-candidate-career-input", "value"),
        State({"type": "prompt-upload-material", "index": dash.ALL}, "value"),
        State("prompt-upload-materials-etc", "value"),
    ],
)
def generate_prompt_callback(
    n_clicks: int,
    name: str,
    org: str,
    position: str,
    date: str,
    salary: str,
    career: str,
    material_values: list[bool],
    etc_input: str | None,
) -> tuple[str, str]:
    if not n_clicks:
        return "", ""

    checked_materials = [
        label for label, checked in zip(MATERIAL_LABELS, material_values) if checked
    ]

    if etc_input and etc_input.strip():
        checked_materials.append(etc_input.strip())

    try:
        prompt = generate_custom_prompt(
            name=name or "",
            organization=org or "",
            position=position or "",
            interview_date=date or "",
            salary=salary or "",
            career_year=career or "",
            uploaded_materials_list=checked_materials,
            extra_instructions="",  # 별도 UI가 없으므로 빈 문자열 전달
        )
        return prompt, "프롬프트가 생성되었습니다."
    except Exception as e:
        return "", f"프롬프트 생성 중 오류: {e}"


def normalize_date(date_str: str) -> str:
    """다양한 날짜 입력을 yyyy-mm-dd로 변환"""
    if not date_str:
        return ""
    date_str = date_str.strip().replace(".", "-").replace("/", "-").replace(" ", "")
    # 20250708 → 2025-07-08
    m = re.match(r"^(\d{4})[-]?(\d{2})[-]?(\d{2})$", date_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # 25-07-08 → 2025-07-08 (2000년대 가정)
    m = re.match(r"^(\d{2})[-]?(\d{2})[-]?(\d{2})$", date_str)
    if m:
        return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # yyyy-mm-dd 등
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    try:
        dt = datetime.strptime(date_str, "%y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return date_str  # 변환 실패 시 원본 반환


@app.callback(
    [
        Output("llm-save-msg", "children"),
        Output("llm-name-input", "value"),
        Output("llm-result-input", "value"),
        Output("llm-evaluator-input", "value"),
        Output("llm-date-input", "value"),
    ],
    [Input("llm-save-btn", "n_clicks"), Input("llm-reset-btn", "n_clicks")],
    [
        State("llm-name-input", "value"),
        State("llm-result-input", "value"),
        State("llm-evaluator-input", "value"),
        State("llm-date-input", "value"),
    ],
)
def llm_input_save_reset_callback(
    save_clicks: int | None,
    reset_clicks: int | None,
    name: str | None,
    result: str | None,
    evaluator: str | None,
    date: str | None,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        # 페이지 로드 시, None 대신 빈 문자열을 반환하여 React 경고 방지
        return "", "", "", "", ""

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if triggered_id == "llm-reset-btn":
        return "", "", "", "", ""

    # 저장 버튼 클릭 시
    if not all([name, result, evaluator, date]):
        return (
            dbc.Alert(
                "모든 항목을 입력해야 저장이 가능합니다.",
                color="warning",
                duration=3000,
            ),
            name or "",
            result or "",
            evaluator or "",
            date or "",
        )

    assert date is not None
    norm_date = normalize_date(date)

    # DB 저장 로직 추가
    from app.db import save_candidate_data
    import json

    assert result is not None
    try:
        json_data = json.loads(result)
    except Exception:
        # JSON 파싱 실패 시 사용자에게 알림
        return (
            dbc.Alert(
                "입력된 LLM 분석 결과가 유효한 JSON 형식이 아닙니다.",
                color="danger",
                duration=5000,
            ),
            name,
            result,
            evaluator,
            date,
        )
    # id는 uuid4로 고유하게 생성
    unique_id = str(uuid.uuid4())

    save_candidate_data(
        {
            "id": unique_id,
            "name": name,
            "evaluator": evaluator,
            "interview_date": norm_date,
            "json_data": json.dumps(json_data),  # DB 저장을 위해 다시 문자열로
        }
    )

    msg = dbc.Alert(
        f"{name} 후보자 분석 결과가 성공적으로 저장되었습니다.",
        color="success",
        duration=3000,
    )
    return msg, "", "", "", ""


# HR 보고서 Candidate Profile 탭 전환 콜백 (리팩토링 버전)
@app.callback(
    [
        Output("content-personal", "className"),
        Output("content-career", "className"),
        Output("content-personality", "className"),
        Output("content-expertise", "className"),
        Output("content-weaknesses", "className"),
        Output("btn-personal", "className"),
        Output("btn-career", "className"),
        Output("btn-personality", "className"),
        Output("btn-expertise", "className"),
        Output("btn-weaknesses", "className"),
    ],
    [
        Input("btn-personal", "n_clicks"),
        Input("btn-career", "n_clicks"),
        Input("btn-personality", "n_clicks"),
        Input("btn-expertise", "n_clicks"),
        Input("btn-weaknesses", "n_clicks"),
    ],
)
def update_hr_profile_tabs(
    personal_clicks,
    career_clicks,
    personality_clicks,
    expertise_clicks,
    weaknesses_clicks,
):
    ctx = dash.callback_context

    # 클릭된 버튼이 없으면 기본값으로 'personal' 탭 활성화
    if not ctx.triggered:
        button_id = "btn-personal"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 모든 탭 ID와 기본 클래스 정보
    tabs = {
        "btn-personal": "personal",
        "btn-career": "career",
        "btn-personality": "personality",
        "btn-expertise": "expertise",
        "btn-weaknesses": "weaknesses",
    }

    outputs = []
    # 컨텐츠 클래스 설정
    for btn, _ in tabs.items():
        if btn == button_id:
            outputs.append("hr-profile-content")
        else:
            outputs.append("hr-profile-content hidden")

    # 버튼 클래스 설정
    for btn, theme in tabs.items():
        base_class = f"hr-profile-button {theme}"
        if btn == button_id:
            outputs.append(f"{base_class} active")
        else:
            outputs.append(base_class)

    return tuple(outputs)


if __name__ == "__main__":
    app.run(debug=True)
