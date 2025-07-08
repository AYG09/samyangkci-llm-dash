from dash import html

def render_dash_copy_button(prompt):
    return html.Button('프롬프트 복사', id='copy-btn', n_clicks=0, style={'marginTop': 16, 'fontWeight': 600})
