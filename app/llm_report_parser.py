import json
from .report_schema import ReportData
import re
from typing import Dict, Any


class ReportParsingError(Exception):
    """LLM 보고서 파싱 중 발생하는 모든 오류에 대한 사용자 정의 예외"""
    pass


def convert_legacy_schema_to_new(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    이전 스키마 데이터를 새로운 ReportData 스키마로 변환합니다.
    """
    try:
        # 이미 새로운 스키마이거나 변환할 데이터가 없으면 그대로 반환
        if "candidate_info" not in data:
            return data
            
        new_data = {}
        
        # CandidateInfo 변환
        old_candidate_info = data.get("candidate_info", {})
        new_data["candidate_info"] = {
            "name": old_candidate_info.get("name", ""),
            "organization": old_candidate_info.get("organization", ""),
            "position": old_candidate_info.get("position", ""),
            "career_summary": old_candidate_info.get("career_summary", ""),
            "salary_info": old_candidate_info.get("salary_info", ""),
            "interview_date": old_candidate_info.get("interview_date", "")
        }
        
        # MaterialAnalysis 변환
        material_list = [
            {
                "material_name": material.get("material_name", ""),
                "summary": material.get("summary", ""),
                "analysis_points": material.get("analysis_points", "")
            }
            for material in data.get("material_analysis", [])
        ]
        new_data["material_analysis"] = material_list
        
        # ComprehensiveReport 변환
        old_report = data.get("comprehensive_report", {})
        new_data["comprehensive_report"] = {
            "summary": old_report.get("summary", ""),
            "recommendation": old_report.get("recommendation", "보류"),
            "score": float(old_report.get("score", 0.0))
        }
        
        # AnalysisItem 변환
        analysis_list = [
            {
                "category": item.get("category", "CAREER"),
                "title": item.get("title", ""),
                "analysis": item.get("analysis", ""),
                "evidence": item.get("evidence", ""),
                "score": float(item.get("score", 0.0))
            }
            for item in data.get("analysis_items", [])
        ]
        new_data["analysis_items"] = analysis_list
        
        # executive_insights, hr_points 변환 (InsightItem)
        new_data["executive_insights"] = [
            {
                "title": ins.get("title", ""), 
                "analysis": ins.get("analysis", ""), 
                "evidence": ins.get("evidence", "")
            }
            for ins in data.get("executive_insights", [])
        ]
        new_data["hr_points"] = [
            {
                "title": p.get("title", ""), 
                "analysis": p.get("analysis", ""), 
                "evidence": p.get("evidence", "")
            }
            for p in data.get("hr_points", [])
        ]
        
        # OverallReliability 변환
        old_reliability = data.get("overall_reliability", {})
        new_data["overall_reliability"] = {
            "title": old_reliability.get("title", "전체 분석 신뢰도"),
            "reliability": old_reliability.get("reliability", "보통")
        }
        
        return new_data
    
    except (ValueError, TypeError) as e:
        raise ReportParsingError(
            f"데이터 타입 변환 중 오류 발생 (예: score를 float으로 변환 실패). 오류: {e}"
        )
    except Exception as e:
        raise ReportParsingError(
            f"이전 스키마 변환 중 예기치 않은 오류 발생: {e}"
        )


def parse_llm_report(text: str) -> ReportData:
    """
    LLM이 생성한 텍스트에서 JSON 객체만 추출하여 파싱하고 
    ReportData 스키마로 검증합니다.
    이전 스키마와의 하위 호환성을 지원합니다.
    """
    print(f"[DEBUG] parse_llm_report 호출됨")
    print(f"[DEBUG] 텍스트 길이: {len(text) if text else 0}")
    print(f"[DEBUG] 텍스트 시작 300자: {text[:300] if text else 'None'}")
    
    try:
        # 텍스트에서 JSON 부분만 추출 (더 강력한 파싱)
        json_text = text.strip()
        
        # 1. Markdown 코드 블록 처리 (```json ... ```)
        match = re.search(r"```json\s*([\s\S]+?)\s*```", text)
        if match:
            json_text = match.group(1).strip()
            print("[DEBUG] 마크다운 코드 블록에서 JSON 추출됨")
        
        # 2. "JSON" 키워드 다음의 내용 추출
        elif text.strip().startswith("JSON"):
            json_text = text.strip()[4:].strip()  # "JSON" 제거
            print("[DEBUG] 'JSON' 키워드 다음 내용 추출됨")
        
        # 3. LLM이 생성한 잘못된 마크업 제거
        # [cite_start] 같은 잘못된 JSON 키 제거
        json_text = re.sub(r'\[cite_start\]', '', json_text)
        print("[DEBUG] 잘못된 마크업 제거 완료")
        
        # JSON 파싱 시도 (3단계 접근)
        data = None
        
        # 1차 시도: raw_decode로 부분 파싱
        try:
            start_index = json_text.find('{')
            if start_index != -1:
                data, _ = json.JSONDecoder().raw_decode(
                    json_text[start_index:])
                print("[DEBUG] 1차 시도 성공: raw_decode")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[DEBUG] 1차 시도 실패: {e}")
            # 2차 시도: 중괄호 범위 추출
            try:
                start_index = json_text.find('{')
                end_index = json_text.rfind('}')
                if (start_index != -1 and end_index != -1 and 
                        start_index < end_index):
                    extracted_json = json_text[start_index: end_index + 1]
                    data = json.loads(extracted_json)
                    print("[DEBUG] 2차 시도 성공: 중괄호 범위 추출")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[DEBUG] 2차 시도 실패: {e}")
                # 3차 시도: 전체 텍스트 파싱
                try:
                    data = json.loads(json_text)
                    print("[DEBUG] 3차 시도 성공: 전체 텍스트 파싱")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[DEBUG] 3차 시도 실패: {e}")
                    print(f"[DEBUG] 파싱 실패한 텍스트 일부: "
                          f"{json_text[:200]}...")
                    raise ReportParsingError(
                        "유효한 JSON 객체를 찾을 수 없습니다.")
        
        if data is None:
            raise ReportParsingError("JSON 파싱에 모두 실패했습니다.")
        
        data_keys = list(data.keys()) if isinstance(data, dict) else 'not dict'
        print(f"[DEBUG] JSON 파싱 성공! 데이터 키: {data_keys}")
        
        # 이전 스키마인지 확인하고 변환
        if ("candidate_info" in data and 
                isinstance(data["candidate_info"], dict)):
            # 이전 스키마 -> 새로운 스키마 변환
            data = convert_legacy_schema_to_new(data)
            print("[DEBUG] 이전 스키마 -> 새로운 스키마 변환 완료")
        
        report_data = ReportData.model_validate(data)
        print("[DEBUG] ReportData 스키마 검증 성공")
        return report_data

    except json.JSONDecodeError as e:
        msg = f"LLM 응답이 유효한 JSON 형식이 아닙니다. 오류: {e}"
        print(f"[DEBUG] JSONDecodeError: {msg}")
        raise ReportParsingError(msg)
    except Exception as e:
        # Pydantic의 ValidationError 등 다른 모든 예외를 포함
        msg = f"LLM 응답이 ReportData 스키마와 일치하지 않습니다. 오류: {e}"
        print(f"[DEBUG] 기타 오류: {msg}")
        raise ReportParsingError(msg)
