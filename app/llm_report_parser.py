import re
from typing import List, Dict, Any

def parse_llm_report(text: str) -> List[Dict[str, Any]]:
    """
    (1)~(17) 항목별 점수, 신뢰도, 자연어 분석, 산출근거 등 추출
    반환: [
        {
            'index': 1,
            'title': '캐롤리프 모델(심리적 안녕감) 분석',
            'score': 4.3,
            'reliability': 4.5,
            'analysis': '...자연어 분석...'
            'evidence': '...점수 산출근거...'
        }, ...
    ]
    """
    # 항목별 구간 추출
    pattern = re.compile(r"\*\*\((\d{1,2})\) ([^*\n]+)\*\*([\s\S]*?)(?=\*\*\(|$)")
    matches = pattern.findall(text)
    results = []
    for idx, title, body in matches:
        # 점수
        score_match = re.search(r"점수[:：]?\s*([0-9.]+)", body)
        score = float(score_match.group(1)) if score_match else None
        # 신뢰도
        reliability_match = re.search(r"신뢰도[:：]?\s*([0-9.]+)", body)
        reliability = float(reliability_match.group(1)) if reliability_match else None
        # 자연어 분석
        analysis_match = re.search(r"자연어 분석[:：]?([\s\S]*?)(?:\n- |\n\*\*|\n점수 산출근거|\n신뢰도|$)", body)
        analysis = analysis_match.group(1).strip() if analysis_match else ''
        # 점수 산출근거
        evidence_match = re.search(r"점수 산출근거[:：]?([\s\S]*?)(?:\n- |\n\*\*|\n신뢰도|$)", body)
        evidence = evidence_match.group(1).strip() if evidence_match else ''
        results.append({
            'index': int(idx),
            'title': title.strip(),
            'score': score,
            'reliability': reliability,
            'analysis': analysis,
            'evidence': evidence
        })
    return results
