import json
import re
from typing import Dict, Any, List, TypedDict, cast


class CandidateInfo(TypedDict, total=False):
    name: str
    organization: str
    position: str
    interview_date: str


class LLMResult(TypedDict, total=False):
    candidate_info: CandidateInfo
    name: str
    organization: str
    position: str
    interview_date: str


def parse_llm_analysis(raw_result: str) -> List[Dict[str, Any]]:
    """
    LLM 분석결과 원문(raw_result)이 JSON 형식일 때 (1)~(17) 항목별 점수,
    분석, 산출근거, 신뢰도 등을 추출.
    반환: [{'index': 1, 'title': '캐롤 리프 모델 분석', 'score': 5.92,
           'analysis': ..., 'evidence': ..., 'reliability': ...}, ...]
    """
    try:
        data = json.loads(raw_result)
    except Exception:
        return []
    results: List[Dict[str, Any]] = []
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


def _clean_value(value: Any) -> Any:
    """ "자료기준:" 같은 접두어를 제거하는 헬퍼 함수 """
    if isinstance(value, str):
        return value.split(":", 1)[-1].strip()
    return value


def extract_candidate_info_from_text(text: str) -> Dict[str, str]:
    """
    LLM 텍스트에서 후보자 정보를 추출합니다.
    1. 텍스트에서 JSON 객체만 정확히 분리하여 파싱을 시도합니다.
    2. 실패 시 정규표현식으로 파싱합니다.
    """
    info = {
        "name": "",
        "organization": "",
        "position": "",
        "date": ""
    }

    print(f"[DEBUG] 추출 시작 - 텍스트 길이: {len(text)}")
    print(f"[DEBUG] 텍스트 시작 500자: {text[:500]}")

    json_found_and_parsed = False

    # 1. JSON 추출 및 파싱 시도
    try:
        json_text = text
        # Markdown 코드 블록(```json ... ```)이 있는지 확인하고 추출
        match = re.search(r"```json\s*([\s\S]+?)\s*```", text)
        if match:
            json_text = match.group(1).strip()
            print("[DEBUG] JSON 코드 블록 발견")

        # 텍스트에서 첫 '{'를 찾아 JSON 파싱 시작점으로 설정
        start_index = json_text.find('{')
        if start_index != -1:
            # candidate_info 부분만 먼저 추출 시도
            candidate_info_match = re.search(
                r'"candidate_info"\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
                json_text,
                re.DOTALL
            )
            
            if candidate_info_match:
                print("[DEBUG] candidate_info 블록 발견")
                candidate_info_text = '{"candidate_info": {' + candidate_info_match.group(1) + '}}'
                try:
                    data = json.loads(candidate_info_text)
                    candidate_info = data.get("candidate_info", {})
                    
                    info["name"] = _clean_value(candidate_info.get("name", ""))
                    info["organization"] = _clean_value(
                        candidate_info.get("organization", "")
                    )
                    info["position"] = _clean_value(
                        candidate_info.get("position", "")
                    )
                    info["date"] = _clean_value(
                        candidate_info.get("interview_date", "")
                    )
                    print(f"[DEBUG] candidate_info에서 추출: {info}")
                    
                    if any(info.values()):
                        json_found_and_parsed = True
                        print(f"[DEBUG] candidate_info 파싱 성공: {info}")
                except json.JSONDecodeError as inner_e:
                    print(f"[DEBUG] candidate_info 파싱 실패: {inner_e}")
            
            # candidate_info가 실패했다면 전체 JSON 파싱 시도
            if not json_found_and_parsed:
                try:
                    decoded_obj, _ = json.JSONDecoder().raw_decode(
                        json_text[start_index:]
                    )
                    data = cast(LLMResult, decoded_obj)
                    print(f"[DEBUG] 전체 JSON 파싱 성공: {list(data.keys())}")
                    
                    # candidate_info 블록에서 정보 추출
                    candidate_info = data.get("candidate_info")
                    if candidate_info:
                        info["name"] = _clean_value(candidate_info.get("name", ""))
                        info["organization"] = _clean_value(
                            candidate_info.get("organization", "")
                        )
                        info["position"] = _clean_value(
                            candidate_info.get("position", "")
                        )
                        info["date"] = _clean_value(
                            candidate_info.get("interview_date", "")
                        )
                        print(f"[DEBUG] 전체 JSON candidate_info에서 추출: {info}")

                    # 루트 레벨 정보 추출 (백업)
                    if not info["name"] and "name" in data:
                        info["name"] = _clean_value(data.get("name", ""))
                    if not info["organization"] and "organization" in data:
                        info["organization"] = _clean_value(
                            data.get("organization", "")
                        )
                    if not info["position"] and "position" in data:
                        info["position"] = _clean_value(data.get("position", ""))
                    if not info["date"] and "interview_date" in data:
                        info["date"] = _clean_value(
                            data.get("interview_date", "")
                        )

                    # JSON에서 하나라도 정보를 성공적으로 추출했다면 플래그 설정
                    if any(info.values()):
                        json_found_and_parsed = True
                        print(f"[DEBUG] 전체 JSON에서 정보 추출 성공: {info}")
                        
                except (json.JSONDecodeError, StopIteration, TypeError) as inner_e:
                    print(f"[DEBUG] 전체 JSON 파싱도 실패: {inner_e}")

    except Exception as e:
        print(f"[DEBUG] JSON 추출 과정에서 오류: {e}")
        pass

    # JSON에서 정보를 성공적으로 찾았다면, 여기서 결과 반환
    if json_found_and_parsed:
        return info

    # 2. 정규표현식 파싱 (Fallback)
    # 이름 추출
    name_patterns = [
        r"(?:후보자|성명|이름)\s?[:는은]?\s?([가-힣]{2,5})",
        r"([가-힣]{2,5})\s?후보자",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            info["name"] = match.group(1).strip()
            break

    # 지원 조직 추출
    org_patterns = [
        r"(?:지원\s?조직|회사명?)\s?[:는은]?\s?"
        r"([가-힣A-Z]+(?:\s?KCI)?)",
        r"([가-힣A-Z]+(?:\s?KCI)?)(?:에|으로| 소속)",
    ]
    for pattern in org_patterns:
        match = re.search(pattern, text)
        if match:
            org_name = match.group(1).strip()
            if "지원" not in org_name:
                info["organization"] = org_name
                break
            
    # 지원 직급 추출
    pos_patterns = [
        r"(?:지원\s?직급|직책|직무|포지션)\s?[:는은]?\s?"
        r"(\S+)",
        r"(\S+)\s?(?:직급|직책|직무|포지션)",
    ]
    for pattern in pos_patterns:
        match = re.search(pattern, text)
        if match:
            pos_name = match.group(1).strip()
            info["position"] = re.sub(r"[으로에]$", "", pos_name)
            break

    # 면접일 추출
    date_patterns = [
        r"(\d{4}[-./]\d{1,2}[-./]\d{1,2})",
        r"(\d{4}년\s?\d{1,2}월\s?\d{1,2}일)",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            date_str = re.sub(r'년|월', '-', date_str)
            date_str = re.sub(r'일', '', date_str)
            date_str = date_str.replace(
                ' ', ''
            ).replace(
                '.', '-'
            ).replace(
                '/', '-'
            )
            parts = date_str.split('-')
            info["date"] = (
                f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
            )
            break
            
    return info
