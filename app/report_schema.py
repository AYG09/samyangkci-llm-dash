# -*- coding: utf-8 -*-
"""
보고서 데이터 모델 정의
- Pydantic 모델을 사용하여 데이터 검증 및 구조화
- LLM 응답 파싱 및 UI 표시에 사용
"""

from typing import List, Literal
from pydantic import BaseModel, Field


class CandidateInfo(BaseModel):
    name: str = Field(..., description="후보자 이름")
    organization: str = Field(..., description="지원 조직")
    position: str = Field(..., description="지원 직급")
    career_summary: str = Field(..., description="경력 요약")
    salary_info: str = Field(..., description="연봉 정보")
    interview_date: str = Field(..., description="면접 일자")


class MaterialAnalysis(BaseModel):
    material_name: str = Field(..., description="자료명")
    summary: str = Field(..., description="요약")
    analysis_points: str = Field(..., description="분석 포인트")


class ComprehensiveReport(BaseModel):
    summary: str = Field(
        ..., description="후보자에 대한 종합적인 평가 및 핵심 요약"
    )
    recommendation: Literal[
        '강력 추천', '추천', '고려', '보류', '비추천'
    ] = Field(..., description="채용 추천 여부")
    score: float = Field(
        ..., description="종합 평점 (100점 만점)", ge=0, le=100
    )


class AnalysisItem(BaseModel):
    category: Literal[
        'CAPABILITY', 'PERFORMANCE', 'POTENTIAL', 'PERSONALITY', 'FIT'
    ] = Field(..., description="통합 인재 평가 모델의 5대 차원")
    title: str = Field(..., description="분석 항목의 제목")
    analysis: str = Field(..., description="분석 내용")
    evidence: str = Field(..., description="분석의 근거")
    score: float = Field(
        ..., description="항목별 점수 (100점 만점)", ge=0, le=100
    )


class DecisionPointItem(BaseModel):
    title: str = Field(..., description="강점 또는 리스크의 제목")
    analysis: str = Field(..., description="상세 분석 내용")
    evidence: str = Field(..., description="분석의 근거")


class DecisionPoints(BaseModel):
    strengths: List[DecisionPointItem] = Field(
        ..., description="후보자의 강점 및 기회 요인"
    )
    risks: List[DecisionPointItem] = Field(
        ..., description="후보자의 리스크 및 우려 사항"
    )


class OverallReliability(BaseModel):
    consistency: str = Field(..., description="일관성")
    completeness: str = Field(..., description="완전성")
    objectivity: str = Field(..., description="객관성")


class ReportData(BaseModel):
    candidate_info: CandidateInfo = Field(..., alias='candidate_info')
    material_analysis: List[MaterialAnalysis] = Field(
        ..., alias='material_analysis'
    )
    comprehensive_report: ComprehensiveReport = Field(
        ..., alias='comprehensive_report'
    )
    analysis_items: List[AnalysisItem] = Field(..., alias='analysis_items')
    decision_points: DecisionPoints = Field(..., alias='decision_points')
    overall_reliability: OverallReliability = Field(
        ..., alias='overall_reliability'
    )

    class Config:
        populate_by_name = True
