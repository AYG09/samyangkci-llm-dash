# 추천 등급별 desc1/desc2/팁 반환 헬퍼
from typing import Tuple, Dict, Any, List

def get_recommendation_texts(level: str) -> Tuple[str, str]:
    """
    추천 등급별 desc1, desc2 반환
    level: 추천 등급명 (ex: '레전드 추천', '최우수 추천', ...)
    return: (desc1, desc2)
    """
    mapping = {
        "레전드 추천": (
            "역대 최고 수준의 역량과 적합도를 모두 갖춘 인재입니다. 조직의 미래를 이끌 핵심 인재로 강력히 추천합니다.",
            "즉각적인 성과 창출과 장기적 리더십, 혁신적 기여가 모두 기대됩니다."
        ),
        "최우수 추천": (
            "검증된 직무 역량, 성장 동기, 조직 적합도를 모두 갖춘 최적의 인재입니다.",
            "즉각적인 성과 창출과 장기적인 전략적 기여가 모두 기대됩니다."
        ),
        "강력 추천": (
            "직무 역량과 성장 가능성이 매우 우수하며, 조직에 빠르게 적응할 인재입니다.",
            "단기·장기 성과 모두 기대되며, 핵심 인재로 성장할 잠재력이 높습니다."
        ),
        "추천": (
            "직무 수행에 필요한 역량과 적합성을 충분히 갖춘 인재입니다.",
            "조직 내 빠른 적응과 안정적인 성과가 기대됩니다."
        ),
        "조건부 추천": (
            "대부분의 역량은 우수하나 일부 영역에서 보완이 필요합니다.",
            "특정 역량 개발 시 조직에 긍정적 기여가 가능할 것으로 판단됩니다."
        ),
        "보완 필요": (
            "기본 역량은 갖추었으나, 여러 영역에서 추가 개발이 필요합니다.",
            "단기 성과보다는 중장기 성장 관점에서 지원이 필요합니다."
        ),
        "비추천": (
            "핵심 역량 및 적합성에서 기준 미달로 판단됩니다.",
            "현 시점에서는 채용 추천이 어렵습니다."
        ),
    }
    return mapping.get(level, ("평가 결과에 따라 별도 안내가 필요합니다.", "추가 검토가 필요합니다."))

def get_extra_tip(stddev: float, can_do: float, will_do: float, will_fit: float) -> str:
    tip = ""
    if stddev >= 0.5:
        tip += "(영역별 편차가 크니 특정 역량 보완 필요) "
    if can_do == 5.0:
        tip += "(직무수행역량 만점) "
    if will_do == 5.0:
        tip += "(동기/성향 만점) "
    if will_fit == 5.0:
        tip += "(조직적합성 만점) "
    return tip.strip()

def validate_section_schema(section: Dict[str, Any]) -> Dict[str, Any]:
    """
    section dict의 필수 필드/이상치/누락 체크 및 기본값/경고 자동 부여
    - 필수: title, score, percent, desc, evidence
    - 누락 시 안내문구/기본값
    - score 이상치(0~5 범위) 자동 보정 및 경고
    """
    s = section.copy()
    # 필수 필드
    s.setdefault("title", "항목명 없음")
    s.setdefault("score", 0.0)
    s.setdefault("percent", 0.0)
    s.setdefault("desc", "분석 설명 없음")
    s.setdefault("evidence", "근거 자료 없음")
    # score 이상치 보정
    if not isinstance(s["score"], (int, float)):
        s["score"] = 0.0
        s["desc"] += " (점수 형식 오류 자동 보정)"
    if s["score"] < 0 or s["score"] > 5:
        s["desc"] += f" (점수 {s['score']} → 0~5로 자동 보정)"
        s["score"] = max(0.0, min(5.0, s["score"]))
    # percent 자동 보정
    s["percent"] = round(s["score"] / 5, 2)
    # evidence 누락/불일치 안내
    if not s["evidence"] or s["evidence"] in ["-", "없음"]:
        s["evidence"] = "근거 자료 없음 (LLM 분석 결과에 근거 미제공)"
    elif "불일치" in s["evidence"]:
        s["desc"] += " (근거와 평가 결과 불일치 주의)"
    return s

def get_section_tags(section: Dict[str, Any]) -> List[str]:
    """
    section dict에서 동적 태그(만점, 주의, 누락, 불일치 등) 리스트 반환
    """
    tags: List[str] = []
    score = section.get("score", 0)
    if score == 5.0:
        tags.append("만점")
    if score < 4.0:
        tags.append("주의")
    if "불일치" in section.get("desc", ""):
        tags.append("불일치")
    return tags
