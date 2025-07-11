import os
import json
from datetime import datetime

def safe_num(value, default=None):
    """
    입력값을 숫자로 안전하게 변환합니다.
    변환할 수 없거나 값이 None이면 기본값(default)을 반환합니다.
    """
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_uwes_level(score):
    """UWES 점수를 질적 수준(Level)으로 변환합니다."""
    score = safe_num(score)
    if score is None:
        return "-"
    if score >= 5.0:
        return "매우 높음"
    elif score >= 4.0:
        return "높음"
    elif score >= 2.5:
        return "보통"
    else:
        return "낮음"


def export_json_result(candidate_name: str, json_data: dict, export_dir: str = "exports") -> str:
    """
    후보자별 분석 결과를 JSON 파일로 내보내는 함수.
    파일명: {후보자명}_분석결과_YYYYMMDD.json
    """
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{candidate_name}_분석결과_{today}.json"
    filepath = os.path.join(export_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    return filepath


def try_parse_json(data: str):
    """
    문자열이 JSON이면 파싱해서 반환, 아니면 None 반환
    """
    try:
        return json.loads(data)
    except Exception:
        return None
