from dash import html

def render_dash_prompt_guide():
    return html.Div([
        html.Hr(),
        html.Div('📝 LLM 분석 사용 가이드', style={'fontSize': '1.18rem', 'color': '#24278B', 'fontWeight': 700, 'marginBottom': '10px'}),
        html.Div([
            html.P([
                html.B('1단계: 프롬프트 복사'), html.Br(),
                '- 위에서 생성된 프롬프트를 전체 복사 (Ctrl+A → Ctrl+C)', html.Br(), html.Br(),
                html.B('2단계: LLM 서비스 접속'), html.Br(),
                '- 원하는 LLM 서비스 버튼 클릭하여 새 창에서 접속', html.Br(), html.Br(),
                html.B('3단계: 프롬프트 입력'), html.Br(),
                '- 복사한 프롬프트를 LLM 채팅창에 붙여넣기 (Ctrl+V)', html.Br(), html.Br(),
                html.B('4단계: 면접 자료 첨부'), html.Br(),
                '- 이력서, 면접 녹취록 등 선택한 자료들을 함께 업로드', html.Br(),
                '- 업로드 자료 중 면접 녹취록을 제외한 각 자료별로 LLM이 반드시 핵심 결과/특이점/리스크/강점 등을 1~2줄로 요약 제시하도록 프롬프트에 포함되어 있습니다.', html.Br(), html.Br(),
                html.B('5단계: 분석 실행'), html.Br(),
                '- Enter 또는 전송 버튼을 눌러 분석 시작', html.Br(), html.Br(),
                html.B('6단계: 결과 저장'), html.Br(),
                "- LLM 분석 결과(개조식)를 복사하여 'LLM 분석 결과 입력' 탭에 저장"
            ], style={'fontSize': '1.05rem', 'lineHeight': '1.7'})
        ])
    ])
