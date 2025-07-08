from dash import html, dcc, dash_table, Input, Output, State, callback, ctx
import pandas as pd
from app.db import load_candidates, delete_candidate

def render_candidate_table():
    df = load_candidates()
    # 필요한 컬럼만 추출 및 None -> '' 처리
    if df.empty:
        return html.Div("저장된 후보자가 없습니다.", style={"padding": "32px", "textAlign": "center", "color": "#888"})
    df = df.fillna("")
    df = df.rename(columns={
        "name": "이름",
        "created_at": "입력일자",
        "evaluator": "평가자",
        "position": "지원직급",
        "org": "지원조직"
    })
    # 지원직급/조직 컬럼이 없을 수 있으니 보정
    if "지원직급" not in df.columns:
        df["지원직급"] = ""
    if "지원조직" not in df.columns:
        df["지원조직"] = ""
    columns = [
        {"name": "선택", "id": "_select", "presentation": "markdown"},
        {"name": "이름", "id": "이름"},
        {"name": "지원조직", "id": "지원조직"},
        {"name": "지원직급", "id": "지원직급"},
        {"name": "평가자", "id": "평가자"},
        {"name": "입력일자", "id": "입력일자"},
        {"name": "삭제", "id": "_delete", "presentation": "markdown"}
    ]
    # 선택/삭제 버튼용 가상 컬럼 추가
    df["_select"] = [f"<input type='checkbox' id='row-select-{row['id']}'>" for _, row in df.iterrows()]
    df["_delete"] = [f"<button id='row-delete-{row['id']}' style='color:#d63031;background:none;border:none;cursor:pointer;font-size:1.1em'>🗑️</button>" for _, row in df.iterrows()]
    return dash_table.DataTable(
        id="candidate-table",
        columns=columns,
        data=df.to_dict("records"),
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "fontSize": "1.05rem"},
        style_header={"background": "#F4F7FB", "fontWeight": 700},
        row_selectable="multi",
        selected_rows=[],
        page_size=10,
        markdown_options={"html": True},
    )
