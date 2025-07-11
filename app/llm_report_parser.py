import json
from .report_schema import ReportData

def parse_llm_report(json_string: str) -> ReportData:
    """
    LLM이 생성한 JSON 문자열을 파싱하고 ReportData 스키마로 검증합니다.

    Args:
        json_string: LLM으로부터 받은 원시 JSON 문자열.

    Returns:
        검증된 ReportData 객체.

    Raises:
        ValueError: JSON 파싱 또는 스키마 검증에 실패할 경우 발생합니다.
    """
    try:
        # JSON 문자열을 Python 딕셔너리로 변환
        data = json.loads(json_string)
        
        # Pydantic 모델을 사용하여 데이터 검증 및 객체 생성
        report_data = ReportData.model_validate(data)
        
        return report_data
    except json.JSONDecodeError as e:
        # JSON 형식이 잘못된 경우
        raise ValueError(f"LLM 응답이 유효한 JSON 형식이 아닙니다. 오류: {e}")
    except Exception as e:
        # Pydantic 검증 실패 또는 기타 오류
        raise ValueError(f"LLM 응답이 ReportData 스키마와 일치하지 않습니다. 오류: {e}")
