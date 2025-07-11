"""프롬프트 생성 관련 콜백 함수들"""

import dash
from dash import Output, Input, State
from datetime import datetime

from ..prompt_logic import generate_custom_prompt


def normalize_date(date_str: str) -> str:
    """날짜 문자열을 정규화합니다."""
    if not date_str:
        return ""
    
    # 기본 형식들 처리
    date_formats = [
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y년 %m월 %d일",
        "%Y년%m월%d일",
    ]
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # 파싱 실패 시 원본 반환
    return date_str


def register_prompt_callbacks(app):
    """프롬프트 관련 콜백들을 앱에 등록합니다."""
    
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
        """프롬프트 생성 버튼 클릭 시 실행되는 콜백"""
        if not n_clicks:
            return dash.no_update, ""

        # 최소 필수 필드 검증 (이름만 필수)
        if not name or not name.strip():
            return (
                "",
                "⚠️ 후보자 이름을 입력해주세요.",
            )

        # 날짜 정규화
        normalized_date = normalize_date(date)

        # material_flags를 uploaded_materials_list로 변환
        from ..config import MATERIAL_LABELS
        uploaded_materials = []
        if material_values:
            for i, selected in enumerate(material_values):
                if selected and i < len(MATERIAL_LABELS):
                    uploaded_materials.append(MATERIAL_LABELS[i])
        
        # 프롬프트 생성
        try:
            prompt = generate_custom_prompt(
                name=name,
                organization=org,
                position=position,
                interview_date=normalized_date,
                salary=salary,
                career_year=career,
                uploaded_materials_list=uploaded_materials,
                extra_instructions=etc_input or "",
            )
            return prompt, ""
        except Exception as e:
            return (
                "",
                f"❌ 프롬프트 생성 중 오류가 발생했습니다: {str(e)}",
            )

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
        personal_clicks: int | None,
        career_clicks: int | None,
        personality_clicks: int | None,
        expertise_clicks: int | None,
        weaknesses_clicks: int | None,
    ):
        """HR 프로필 탭 전환을 처리합니다."""
        ctx = dash.callback_context
        if not ctx.triggered:
            # 기본값: personal 탭 활성화
            return (
                "tab-content active",
                "tab-content",
                "tab-content",
                "tab-content",
                "tab-content",
                "btn btn-primary active",
                "btn btn-outline-primary",
                "btn btn-outline-primary",
                "btn btn-outline-primary",
                "btn btn-outline-primary",
            )

        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # 모든 탭을 비활성화 상태로 초기화
        content_classes = ["tab-content"] * 5
        btn_classes = ["btn btn-outline-primary"] * 5
        
        # 클릭된 탭만 활성화
        if triggered_id == "btn-personal":
            content_classes[0] = "tab-content active"
            btn_classes[0] = "btn btn-primary active"
        elif triggered_id == "btn-career":
            content_classes[1] = "tab-content active"
            btn_classes[1] = "btn btn-primary active"
        elif triggered_id == "btn-personality":
            content_classes[2] = "tab-content active"
            btn_classes[2] = "btn btn-primary active"
        elif triggered_id == "btn-expertise":
            content_classes[3] = "tab-content active"
            btn_classes[3] = "btn btn-primary active"
        elif triggered_id == "btn-weaknesses":
            content_classes[4] = "tab-content active"
            btn_classes[4] = "btn btn-primary active"
        
        return (*content_classes, *btn_classes)

    @app.callback(
        [
            Output({"type": "collapse", "index": dash.MATCH}, "is_open"),
            Output({"type": "collapse-button", "index": dash.MATCH}, "className"),
        ],
        [Input({"type": "collapse-button", "index": dash.MATCH}, "n_clicks")],
        [
            State({"type": "collapse", "index": dash.MATCH}, "is_open"),
            State({"type": "collapse-button", "index": dash.MATCH}, "className"),
        ],
        prevent_initial_call=True,
    )
    def toggle_accordion(n_clicks, is_open, class_name):
        """아코디언 토글을 처리합니다."""
        if n_clicks is None:
            return dash.no_update, dash.no_update

        new_is_open = not is_open
        
        # 버튼 클래스 업데이트
        if new_is_open:
            new_class = class_name.replace("collapsed", "").strip()
        else:
            if "collapsed" not in class_name:
                new_class = f"{class_name} collapsed"
            else:
                new_class = class_name
        
        return new_is_open, new_class

    app.clientside_callback(
        """
        function(n_clicks, prompt_content) {
            if (n_clicks && prompt_content) {
                // 브라우저 클립보드 API를 사용하여 텍스트 복사
                navigator.clipboard.writeText(prompt_content).then(function() {
                    // 복사 성공 메시지 표시
                    return "✅ 프롬프트가 클립보드에 복사되었습니다!";
                }).catch(function(err) {
                    console.error('클립보드 복사 실패:', err);
                    return "❌ 클립보드 복사에 실패했습니다.";
                });
                return "✅ 프롬프트가 클립보드에 복사되었습니다!";
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("copy-success-msg", "children"),
        [Input("copy-prompt-button", "n_clicks")],
        [State("prompt-generated-prompt-area", "value")],
        prevent_initial_call=True,
    ) 