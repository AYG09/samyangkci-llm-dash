from dash import html, dcc
import dash_bootstrap_components as dbc
from .config import MATERIAL_LABELS


def render_dash_prompt_generator():
    llm_links = {
        "GPT-4": {"href": "https://chat.openai.com/", "class": "gpt4"},
        "Gemini": {"href": "https://gemini.google.com/", "class": "gemini"},
        "Claude 3": {"href": "https://claude.ai/", "class": "claude"},
        "Bing Copilot": {
            "href": "https://copilot.microsoft.com/", "class": "copilot"
        },
        "Perplexity": {
            "href": "https://www.perplexity.ai/", "class": "perplexity"
        },
    }

    return html.Div([
        html.H4('면접자 정보 입력', className="tab-section-title"),

        html.Div([
            html.Label(
                '업로드할 자료 내역을 선택하세요 (복수 선택 가능)',
                className="form-label-bold"
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Checkbox(
                        id={'type': 'prompt-upload-material', 'index': i},
                        value=False
                    ),
                    html.Span(label)
                ], width=3, className="checkbox-item")
                for i, label in enumerate(MATERIAL_LABELS)
            ], justify="start", className="checkbox-container"),

            html.Div([
                dbc.Label('기타(직접 입력)', html_for='prompt-upload-materials-etc'),
                dbc.Input(
                    id='prompt-upload-materials-etc',
                    placeholder='예: 추가 자료명 입력'
                ),
            ], className="etc-input-container")
        ], className="card-section form-section"),

        dbc.Row([
            dbc.Col([
                dbc.Label('이름', html_for='prompt-candidate-name-input'),
                dbc.Input(
                    id='prompt-candidate-name-input', placeholder='예: 홍길동'
                ),
            ], md=4),
            dbc.Col([
                dbc.Label('지원조직', html_for='prompt-candidate-org-input'),
                dbc.Input(
                    id='prompt-candidate-org-input', placeholder='예: 삼양KCI'
                ),
            ], md=4),
            dbc.Col([
                dbc.Label('지원직급', html_for='prompt-candidate-position-input'),
                dbc.Input(
                    id='prompt-candidate-position-input', placeholder='예: 팀장'
                ),
            ], md=4),
        ], className="mb-2"),
        dbc.Row([
            dbc.Col([
                dbc.Label('면접일', html_for='prompt-candidate-date-input'),
                dbc.Input(
                    id='prompt-candidate-date-input', placeholder='예: 20250708'
                ),
            ], md=4),
            dbc.Col([
                dbc.Label('연봉(만원)', html_for='prompt-candidate-salary-input'),
                dbc.Input(
                    id='prompt-candidate-salary-input', placeholder='예: 6000'
                ),
            ], md=4),
            dbc.Col([
                dbc.Label('경력(년)', html_for='prompt-candidate-career-input'),
                dbc.Input(
                    id='prompt-candidate-career-input', placeholder='예: 10'
                ),
            ], md=4),
        ]),

        html.Div([
            dbc.Button(
                '프롬프트 생성',
                id='prompt-generate-prompt-btn',
                className="btn-primary btn-full-width my-4"
            ),
            html.Span(
                id='prompt-warning-message',
                className="text-danger ms-2 fw-bold"
            )
        ]),
        dcc.Textarea(
            id='prompt-generated-prompt-area',
            readOnly=True,
            className="prompt-textarea"
        ),

        html.Div([
            dbc.Button(
                [
                    html.I(className="bi bi-clipboard me-2"),
                    html.Span("프롬프트 복사"),
                ],
                id="copy-prompt-button",
                color="primary",
                className="btn-full-width mt-3",
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            ),
            html.Div(
                id='copy-success-msg',
                className="copy-success-message mt-2",
                style={
                    "textAlign": "center",
                    "fontWeight": "bold",
                    "color": "#28a745"
                }
            ),
        ]),

        html.Hr(className="my-5"),
        html.Div([
            dbc.Button(
                name,
                href=details["href"],
                target='_blank',
                className=f"btn-llm-link {details['class']}"
            )
            for name, details in llm_links.items()
        ], className="llm-link-container"),

    ], className="page-container")
