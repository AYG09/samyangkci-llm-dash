# -------------------- IMPORTS/상수/초기화 --------------------
import os
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from .db import init_db

# 콜백 등록 함수들 임포트
from .callbacks.llm_callbacks import register_llm_callbacks
from .callbacks.report_callbacks import register_report_callbacks
from .callbacks.prompt_callbacks import register_prompt_callbacks
from .callbacks.routing_callbacks import register_routing_callbacks
from .ui_candidate import register_candidate_callbacks

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

# 앱 시작 시 DB 테이블 자동 생성
init_db()

# app 인스턴스는 단 한 번만 생성
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
        (
            "https://fonts.googleapis.com/css2?"
            "family=Poppins:wght@300;400;500;600;700;800;900&display=swap"
        ),
        "https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css",
    ],
    suppress_callback_exceptions=True,
)
server = app.server

# -------------------- 레이아웃 정의 --------------------
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),  # URL 라우팅 지원
        dcc.Store(id='save-signal-store'),  # 탭 간 상태 공유를 위한 저장소
        html.Div(id='page-content'),  # 동적 페이지 내용

    ],
    fluid=True,
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "0 0 64px 0",
        "background": "#F4F7FB",
    },
)




# -------------------- 콜백 등록 --------------------
# 각 모듈에서 콜백들을 등록
register_llm_callbacks(app)
register_report_callbacks(app)
register_prompt_callbacks(app)
register_candidate_callbacks(app)
register_routing_callbacks(app)

# -------------------- 앱 실행 --------------------
if __name__ == "__main__":
    app.run(debug=True)
