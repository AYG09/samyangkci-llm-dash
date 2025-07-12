# -*- coding: utf-8 -*-
"""
LLM 응답 파싱 및 검증 모듈
- 통합 인재 평가 모델(5대 차원) 기반으로 완전히 재설계
- JSON 파싱, 스키마 검증, 오류 처리 등 포함
"""

import logging
from typing import Dict, Any, List, Optional, Union
from pydantic import ValidationError
from app.report_schema import ReportData
from app.utils_llm_parse import (
    remove_citation_markers,
    safe_json_parse
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 통합 인재 평가 모델 5대 차원 정의
VALID_CATEGORIES = {
    'CAPABILITY', 'PERFORMANCE', 'POTENTIAL', 'PERSONALITY', 'FIT'
}

# 차원별 표준 분석 항목 (이론적 기반)
DIMENSION_ITEMS = {
    'CAPABILITY': [
        '전문 지식 및 기술',
        '핵심 역량',
        '기능 역량',
        '업무 수행 능력'
    ],
    'PERFORMANCE': [
        '과거 성과 분석',
        '성과 창출 패턴',
        '목표 달성 능력',
        '성과 지속성'
    ],
    'POTENTIAL': [
        '학습 능력',
        '성장 마인드셋',
        '적응력',
        '리더십 잠재력'
    ],
    'PERSONALITY': [
        '성격 특성',
        '행동 양식',
        '동기 및 가치관',
        '정서 조절'
    ],
    'FIT': [
        '조직 문화 적합성',
        '직무 적합성',
        '팀 적합성',
        '가치관 일치도'
    ]
}

# 제목-차원 매핑 (자동 보정용)
TITLE_TO_CATEGORY_MAP = {
    # CAPABILITY 관련
    '전문 지식 및 기술': 'CAPABILITY',
    '핵심 역량': 'CAPABILITY',
    '기능 역량': 'CAPABILITY',
    '업무 수행 능력': 'CAPABILITY',
    '전문성': 'CAPABILITY',
    '기술적 역량': 'CAPABILITY',
    '직무 능력': 'CAPABILITY',
    '전문 기술': 'CAPABILITY',
    
    # PERFORMANCE 관련
    '과거 성과 분석': 'PERFORMANCE',
    '성과 창출 패턴': 'PERFORMANCE',
    '목표 달성 능력': 'PERFORMANCE',
    '성과 지속성': 'PERFORMANCE',
    '성과': 'PERFORMANCE',
    '달성도': 'PERFORMANCE',
    '실적': 'PERFORMANCE',
    '성과 관리': 'PERFORMANCE',
    
    # POTENTIAL 관련
    '학습 능력': 'POTENTIAL',
    '성장 마인드셋': 'POTENTIAL',
    '적응력': 'POTENTIAL',
    '리더십 잠재력': 'POTENTIAL',
    '잠재력': 'POTENTIAL',
    '성장 가능성': 'POTENTIAL',
    '발전 가능성': 'POTENTIAL',
    '학습 민첩성': 'POTENTIAL',
    
    # PERSONALITY 관련
    '성격 특성': 'PERSONALITY',
    '행동 양식': 'PERSONALITY',
    '동기 및 가치관': 'PERSONALITY',
    '정서 조절': 'PERSONALITY',
    '성격': 'PERSONALITY',
    '개인 특성': 'PERSONALITY',
    '행동 특성': 'PERSONALITY',
    '동기': 'PERSONALITY',
    '가치관': 'PERSONALITY',
    
    # FIT 관련
    '조직 문화 적합성': 'FIT',
    '직무 적합성': 'FIT',
    '팀 적합성': 'FIT',
    '가치관 일치도': 'FIT',
    '조직 적합성': 'FIT',
    '문화 적합성': 'FIT',
    '적합성': 'FIT',
    '조직 부합도': 'FIT'
}


def fix_analysis_item_categories(analysis_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    분석 항목들의 카테고리를 새로운 5대 차원 구조에 맞게 보정
    """
    logger.info(f"분석 항목 카테고리 보정 시작 (총 {len(analysis_items)}개 항목)")
    
    fixed_items = []
    category_counts = {cat: 0 for cat in VALID_CATEGORIES}
    
    for item in analysis_items:
        title = item.get('title', '').strip()
        category = item.get('category', '').strip()
        
        # 제목 기반 카테고리 자동 매핑
        if title in TITLE_TO_CATEGORY_MAP:
            correct_category = TITLE_TO_CATEGORY_MAP[title]
            if category != correct_category:
                logger.info(f"카테고리 보정: '{title}' {category} -> {correct_category}")
                item['category'] = correct_category
        
        # 유효하지 않은 카테고리 처리
        elif category not in VALID_CATEGORIES:
            # 제목에서 키워드 추출하여 카테고리 추정
            inferred_category = infer_category_from_title(title)
            if inferred_category:
                logger.info(f"카테고리 추정: '{title}' {category} -> {inferred_category}")
                item['category'] = inferred_category
            else:
                logger.warning(f"카테고리 추정 실패: '{title}' ({category})")
                # 기본값으로 CAPABILITY 할당
                item['category'] = 'CAPABILITY'
        
        # 차원별 항목 수 카운트
        final_category = item.get('category', 'CAPABILITY')
        if final_category in VALID_CATEGORIES:
            category_counts[final_category] += 1
        
        fixed_items.append(item)
    
    logger.info(f"차원별 항목 수: {category_counts}")
    return fixed_items


def infer_category_from_title(title: str) -> Optional[str]:
    """
    제목에서 키워드를 추출하여 카테고리를 추정
    """
    title_lower = title.lower()
    
    # 키워드 기반 카테고리 추정
    if any(keyword in title_lower for keyword in ['지식', '기술', '능력', '역량', '전문', '스킬']):
        return 'CAPABILITY'
    elif any(keyword in title_lower for keyword in ['성과', '결과', '달성', '실적', '완수']):
        return 'PERFORMANCE'
    elif any(keyword in title_lower for keyword in ['잠재력', '성장', '발전', '학습', '적응', '리더십']):
        return 'POTENTIAL'
    elif any(keyword in title_lower for keyword in ['성격', '특성', '행동', '동기', '가치', '정서']):
        return 'PERSONALITY'
    elif any(keyword in title_lower for keyword in ['적합성', '문화', '조직', '팀', '부합']):
        return 'FIT'
    
    return None


def validate_analysis_structure(analysis_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    분석 항목의 구조를 검증하고 품질 점검
    """
    validation_result = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'statistics': {}
    }
    
    # 기본 통계
    total_items = len(analysis_items)
    category_distribution = {cat: 0 for cat in VALID_CATEGORIES}
    
    for item in analysis_items:
        category = item.get('category', '')
        if category in VALID_CATEGORIES:
            category_distribution[category] += 1
    
    validation_result['statistics'] = {
        'total_items': total_items,
        'category_distribution': category_distribution,
        'target_items_per_category': 4,
        'target_total_items': 17
    }
    
    # 구조 검증 - 17개 기준
    if total_items != 17:
        validation_result['warnings'].append(
            f"총 분석 항목 수가 17개가 아닙니다. (현재: {total_items}개)"
        )
    
    # 차원별 항목 수 검증 - 현실적인 목표치 적용
    target_counts = {
        'CAPABILITY': 6,
        'PERSONALITY': 4,
        'FIT': 3,
        'PERFORMANCE': 2,
        'POTENTIAL': 2
    }
    
    for category, count in category_distribution.items():
        expected_count = target_counts.get(category, 4)
        if count != expected_count:
            validation_result['warnings'].append(
                f"{category} 차원의 항목 수가 {expected_count}개가 아닙니다. (현재: {count}개)"
            )
    
    # 필수 필드 검증
    for i, item in enumerate(analysis_items):
        for field in ['category', 'title', 'analysis', 'evidence', 'score']:
            if field not in item or not item[field]:
                validation_result['errors'].append(
                    f"항목 {i+1}번의 '{field}' 필드가 누락되었습니다."
                )
    
    if validation_result['errors']:
        validation_result['valid'] = False
    
    return validation_result


def parse_llm_response(response_text: str) -> Union[ReportData, Dict[str, Any]]:
    """
    LLM 응답을 파싱하고 새로운 5대 차원 구조로 검증
    """
    logger.info("LLM 응답 파싱 시작")
    
    try:
        # 1. 인용 마커 제거
        cleaned_text = remove_citation_markers(response_text)
        logger.info("인용 마커 제거 완료")
        
        # 2. JSON 파싱
        json_data = safe_json_parse(cleaned_text)
        if not json_data:
            raise ValueError("JSON 파싱 실패")
        
        # 3. 분석 항목 보정
        if 'analysis_items' in json_data:
            json_data['analysis_items'] = fix_analysis_item_categories(
                json_data['analysis_items']
            )
        
        # 4. 데이터 구조 매핑 (기존 구조를 새로운 스키마에 맞게 변환)
        json_data = map_data_to_schema(json_data)
        
        # 5. 구조 검증
        if 'analysis_items' in json_data:
            validation_result = validate_analysis_structure(json_data['analysis_items'])
            logger.info(f"구조 검증 완료: {validation_result['statistics']}")
            
            if validation_result['warnings']:
                for warning in validation_result['warnings']:
                    logger.warning(warning)
            
            if validation_result['errors']:
                for error in validation_result['errors']:
                    logger.error(error)
        
        # 6. Pydantic 모델 검증
        try:
            report_data = ReportData(**json_data)
            logger.info("Pydantic 모델 검증 완료")
            return report_data
        except ValidationError as e:
            logger.error(f"Pydantic 검증 실패: {e}")
            # 검증 실패 시에도 데이터 반환 (UI에서 표시 가능)
            # ValidationError 발생 시에도 ReportData 객체 생성 시도
            try:
                # 필수 필드만 있는 최소한의 ReportData 객체 생성
                minimal_data = {
                    'candidate_info': json_data.get('candidate_info', {}),
                    'material_analysis': json_data.get('material_analysis', []),
                    'comprehensive_report': json_data.get('comprehensive_report', {}),
                    'analysis_items': json_data.get('analysis_items', []),
                    'executive_insights': json_data.get('executive_insights', []),
                    'hr_points': json_data.get('hr_points', []),
                    'overall_reliability': json_data.get('overall_reliability', {})
                }
                return ReportData(**minimal_data)
            except Exception as inner_e:
                logger.error(f"최소 ReportData 객체 생성 실패: {inner_e}")
                # 마지막 수단으로 dict 반환
                return json_data
        
    except Exception as e:
        logger.error(f"파싱 중 오류 발생: {str(e)}")
        return {
            'error': str(e),
            'raw_response': response_text[:500] + '...' if len(response_text) > 500 else response_text
        }


def map_data_to_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    기존 데이터 구조를 새로운 스키마에 맞게 변환
    """
    logger.info("데이터 구조 매핑 시작")
    
    # executive_insights 변환 (역방향 호환성 포함)
    if 'executive_insights' in data:
        mapped_insights = []
        for item in data['executive_insights']:
            if isinstance(item, dict):
                # 기존 구조: {"title": "...", "analysis": "...", "evidence": "..."}
                # 새로운 구조: {"insight": "...", "impact": "..."} + 호환성 속성
                mapped_item = {
                    'insight': item.get('analysis', item.get('title', '')),
                    'impact': item.get('evidence', item.get('title', '')),
                    # UI 호환성을 위한 추가 속성
                    'title': item.get('title', item.get('analysis', '')),
                    'analysis': item.get('analysis', item.get('title', '')),
                    'evidence': item.get('evidence', item.get('title', ''))
                }
                mapped_insights.append(mapped_item)
        data['executive_insights'] = mapped_insights
        logger.info(f"executive_insights 변환 완료: {len(mapped_insights)}개 항목")
    
    # hr_points 변환 (역방향 호환성 포함)
    if 'hr_points' in data:
        mapped_points = []
        for item in data['hr_points']:
            if isinstance(item, dict):
                # 기존 구조: {"title": "...", "analysis": "...", "evidence": "..."}
                # 새로운 구조: {"insight": "...", "impact": "..."} + 호환성 속성
                mapped_item = {
                    'insight': item.get('analysis', item.get('title', '')),
                    'impact': item.get('evidence', item.get('title', '')),
                    # UI 호환성을 위한 추가 속성
                    'title': item.get('title', item.get('analysis', '')),
                    'analysis': item.get('analysis', item.get('title', '')),
                    'evidence': item.get('evidence', item.get('title', ''))
                }
                mapped_points.append(mapped_item)
        data['hr_points'] = mapped_points
        logger.info(f"hr_points 변환 완료: {len(mapped_points)}개 항목")
    
    # overall_reliability 변환
    if 'overall_reliability' in data:
        reliability_data = data['overall_reliability']
        if isinstance(reliability_data, dict):
            # 기존 구조: {"title": "...", "reliability": "..."}
            # 새로운 구조: {"consistency": "...", "completeness": "...", "objectivity": "..."}
            reliability_value = reliability_data.get('reliability', '보통')
            mapped_reliability = {
                'consistency': reliability_value,
                'completeness': reliability_value,
                'objectivity': reliability_value
            }
            data['overall_reliability'] = mapped_reliability
            logger.info(f"overall_reliability 변환 완료: {reliability_value}")
    
    logger.info("데이터 구조 매핑 완료")
    return data


def calculate_weighted_score(analysis_items: List[Dict[str, Any]]) -> float:
    """
    5대 차원별 가중평균 점수 계산
    """
    weights = {
        'CAPABILITY': 0.25,
        'PERFORMANCE': 0.25,
        'POTENTIAL': 0.20,
        'PERSONALITY': 0.15,
        'FIT': 0.15
    }
    
    category_scores = {}
    
    # 차원별 평균 점수 계산
    for category in VALID_CATEGORIES:
        category_items = [item for item in analysis_items if item.get('category') == category]
        if category_items:
            category_avg = sum(item.get('score', 0) for item in category_items) / len(category_items)
            category_scores[category] = category_avg
        else:
            category_scores[category] = 0
    
    # 가중평균 계산
    weighted_score = sum(
        category_scores[category] * weights[category] 
        for category in VALID_CATEGORIES
    )
    
    logger.info(f"차원별 점수: {category_scores}")
    logger.info(f"가중평균 점수: {weighted_score:.2f}")
    
    return round(weighted_score, 2)


def generate_summary_report(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    파싱된 데이터를 기반으로 요약 보고서 생성
    """
    analysis_items = parsed_data.get('analysis_items', [])
    
    # 가중평균 점수 계산
    weighted_score = calculate_weighted_score(analysis_items)
    
    # 차원별 통계
    dimension_stats = {}
    for category in VALID_CATEGORIES:
        category_items = [item for item in analysis_items if item.get('category') == category]
        if category_items:
            scores = [item.get('score', 0) for item in category_items]
            dimension_stats[category] = {
                'count': len(category_items),
                'avg_score': round(sum(scores) / len(scores), 2),
                'min_score': min(scores),
                'max_score': max(scores)
            }
    
    summary = {
        'total_items': len(analysis_items),
        'weighted_score': weighted_score,
        'dimension_statistics': dimension_stats,
        'parsing_timestamp': None  # 필요시 추가
    }
    
    return summary


# ImportError 해결을 위한 함수 별칭 추가
# 기존 코드에서 parse_llm_report를 import하려고 하는데, 
# 실제로는 parse_llm_response가 정의되어 있어서 발생하는 문제를 해결
parse_llm_report = parse_llm_response
