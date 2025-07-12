import json
import re
from typing import Dict, Any, List, TypedDict, cast
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


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


def remove_citation_markers(text: str) -> str:
    """
    텍스트에서 인용 마커를 제거합니다.
    
    Args:
        text (str): 원본 텍스트
        
    Returns:
        str: 인용 마커가 제거된 텍스트
    """
    if not text:
        return text
    
    # 인용 마커 패턴들을 정의
    citation_patterns = [
        r'\[cite_start\]',
        r'\[cite_end\]',
        r'\[cite:\s*\d+(?:,\s*\d+)*\]',
        r'\[ref:\s*\d+(?:,\s*\d+)*\]',
        r'\[source:\s*\d+(?:,\s*\d+)*\]',
        r'\[evidence:\s*\d+(?:,\s*\d+)*\]',
    ]
    
    # 각 패턴을 순차적으로 제거
    cleaned_text = text
    for pattern in citation_patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
    
    # 연속된 공백을 단일 공백으로 정리
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # 앞뒤 공백 제거
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def clean_analysis_report(report_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    분석 보고서에서 인용 마커를 제거합니다.
    
    Args:
        report_dict (Dict[str, Any]): 분석 보고서 딕셔너리
        
    Returns:
        Dict[str, Any]: 인용 마커가 제거된 분석 보고서
    """
    if not isinstance(report_dict, dict):
        return report_dict
    
    cleaned_report: Dict[str, Any] = {}
    
    for key, value in report_dict.items():
        if isinstance(value, str):
            # 문자열인 경우 인용 마커 제거
            cleaned_report[key] = remove_citation_markers(value)
        elif isinstance(value, list):
            # 리스트인 경우 각 요소에 대해 재귀적으로 처리
            cleaned_list: List[Any] = []
            for item in value:
                if isinstance(item, dict):
                    cleaned_list.append(clean_analysis_report(item))
                elif isinstance(item, str):
                    cleaned_list.append(remove_citation_markers(item))
                else:
                    cleaned_list.append(item)
            cleaned_report[key] = cleaned_list
        elif isinstance(value, dict):
            # 딕셔너리인 경우 재귀적으로 처리
            cleaned_report[key] = clean_analysis_report(value)
        else:
            # 기타 타입은 그대로 유지
            cleaned_report[key] = value
    
    return cleaned_report


def safe_json_parse(json_str: str, default_value: Any = None) -> Any:
    """
    안전한 JSON 파싱 함수 - 삼양KCI 개발 원칙 11번, 12번 적용
    
    Args:
        json_str (str): 파싱할 JSON 문자열
        default_value (Any): 파싱 실패 시 반환할 기본값
        
    Returns:
        Any: 파싱된 JSON 객체 또는 기본값
        
    원칙 적용:
    - 방어적 코딩: 파싱 실패 시 기본값 반환
    - JSON 데이터 일관성: 마크다운 코드블록, 불필요한 문자 정제
    """
    if not json_str:
        logger.warning("빈 JSON 문자열 입력")
        return default_value if default_value is not None else {}
    
    try:
        # 1. 마크다운 코드블록 정제 (원칙 12번)
        cleaned_json = clean_json_string(json_str)
        
        # 2. JSON 파싱 시도
        parsed_data = json.loads(cleaned_json)
        
        logger.debug(f"JSON 파싱 성공: {len(str(parsed_data))} 문자")
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {e}")
        logger.debug(f"원본 JSON (처음 200자): {json_str[:200]}")
        
        # 3. 추가 정제 시도
        try:
            # 추가적인 정제 시도
            extra_cleaned = extra_clean_json_string(json_str)
            parsed_data = json.loads(extra_cleaned)
            logger.info("추가 정제 후 JSON 파싱 성공")
            return parsed_data
        except Exception as extra_e:
            logger.error(f"추가 정제 후에도 파싱 실패: {extra_e}")
    
    except Exception as e:
        logger.error(f"JSON 파싱 중 예상치 못한 오류: {e}")
    
    # 4. 모든 파싱 시도 실패 시 기본값 반환 (방어적 코딩)
    logger.warning("JSON 파싱 실패, 기본값 반환")
    return default_value if default_value is not None else {}


def clean_json_string(json_str: str) -> str:
    """
    JSON 문자열에서 불필요한 문자들을 정제 - 삼양KCI 개발 원칙 12번 적용
    
    Args:
        json_str (str): 정제할 JSON 문자열
        
    Returns:
        str: 정제된 JSON 문자열
    """
    if not json_str:
        return json_str
    
    # 1. 마크다운 코드블록 제거 (```json ... ```)
    cleaned = re.sub(r'```json\s*', '', json_str, 
                     flags=re.IGNORECASE)
    cleaned = re.sub(r'```\s*$', '', cleaned, 
                     flags=re.MULTILINE)
    
    # 2. 기타 마크다운 코드블록 제거 (``` ... ```)
    cleaned = re.sub(r'```[^`]*```', '', cleaned, 
                     flags=re.DOTALL)
    
    # 3. 불필요한 escape 문자 정제
    cleaned = cleaned.replace('\\"', '"')
    cleaned = cleaned.replace('\\n', '\n')
    cleaned = cleaned.replace('\\r', '\r')
    cleaned = cleaned.replace('\\t', '\t')
    
    # 4. 앞뒤 공백 정리
    cleaned = cleaned.strip()
    
    return cleaned


def extra_clean_json_string(json_str: str) -> str:
    """
    추가적인 JSON 문자열 정제 - 더 강력한 정제 시도
    
    Args:
        json_str (str): 정제할 JSON 문자열
        
    Returns:
        str: 정제된 JSON 문자열
    """
    if not json_str:
        return json_str
    
    # 1. 기본 정제 먼저 수행
    cleaned = clean_json_string(json_str)
    
    # 2. 첫 번째 { 찾기
    start_idx = cleaned.find('{')
    if start_idx == -1:
        return cleaned
    
    # 3. 마지막 } 찾기
    end_idx = cleaned.rfind('}')
    if end_idx == -1:
        return cleaned
    
    # 4. 중간 부분만 추출
    json_part = cleaned[start_idx:end_idx+1]
    
    # 5. 추가 정제
    # str(dict) 형태의 잘못된 문자열 정제
    json_part = re.sub(r"'([^']+)':", r'"\1":', json_part)  
    json_part = re.sub(r":\s*'([^']*)'", r': "\1"', json_part)  
    
    # 6. 불필요한 문자 제거
    json_part = re.sub(r'[^\x00-\x7F]+', '', json_part)  
    
    return json_part


def safe_get_nested_value(data: Dict[str, Any], keys: List[str], 
                         default: Any = None) -> Any:
    """
    중첩된 딕셔너리에서 안전하게 값 추출 - 삼양KCI 개발 원칙 11번 적용
    
    Args:
        data (Dict): 대상 딕셔너리
        keys (List[str]): 접근할 키 목록 
                         (예: ['level1', 'level2', 'level3'])
        default (Any): 키가 없을 때 반환할 기본값
        
    Returns:
        Any: 추출된 값 또는 기본값
        
    예시:
        safe_get_nested_value(data, ['candidate_info', 'name'], 
                             '알 수 없음')
    """
    if not isinstance(data, dict):
        return default
    
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current
