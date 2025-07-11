import json
from typing import Dict, Any, List

def parse_llm_analysis(raw_result: str) -> List[Dict[str, Any]]:
    """
    LLM 분석결과 원문(raw_result)이 JSON 형식일 때 (1)~(17) 항목별 점수, 분석, 산출근거, 신뢰도 등을 추출.
    반환: [{ 'index': 1, 'title': '캐롤 리프 모델 분석', 'score': 5.92, 'analysis': ..., 'evidence': ..., 'reliability': ... }, ...]
    """
    try:
        data = json.loads(raw_result)
    except Exception:
        return []
    results = []
    for item in data.get('분석항목', []):
        results.append({
            'index': item.get('index'),
            'title': item.get('title'),
            'score': item.get('score'),
            'score_max': item.get('score_max'),
            'score_text': item.get('score_text'),
            'analysis': item.get('analysis'),
            'evidence': item.get('evidence'),
            'reliability': item.get('reliability'),
        })
    return results

# 예시 사용법:
# from app.db import load_candidates
# df = load_candidates()
# row = df[df['id']==12].iloc[0]
# parsed = parse_llm_analysis(row['raw_result'])
# for item in parsed:
#     print(item)
