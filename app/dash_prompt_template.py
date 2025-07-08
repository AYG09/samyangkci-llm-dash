from dash import html, dcc

def render_dash_prompt_template(prompt):
    return html.Div([
        html.H4('프롬프트 템플릿'),
        dcc.Textarea(id='template-area', value=prompt, style={'width': '100%', 'height': 200}),
        html.Button('템플릿 복사', id='copy-template-btn', n_clicks=0, style={'marginTop': 16, 'fontWeight': 600}),
        html.Div(id='copy-template-status', style={'marginTop': '16px'})
    ], style={'marginTop': 30})
