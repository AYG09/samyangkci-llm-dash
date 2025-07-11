from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class CandidateInfo(BaseModel):
    name: str = Field(..., description="후보자 이름")
    organization: Optional[str] = Field(default="", description="지원 조직")
    position: str = Field(..., description="지원 직무")
    career_summary: str = Field(
        ..., description="총 경력, 핵심 전문 분야 등 요약"
    )
    salary_info: str = Field(
        ..., description="희망 연봉 또는 현재 연봉 정보"
    )
    interview_date: str = Field(..., description="면접 일자")


class MaterialAnalysis(BaseModel):
    material_name: str = Field(..., description="분석한 자료의 파일명")
    summary: str = Field(..., description="해당 자료의 핵심 내용 요약")
    analysis_points: str = Field(
        ..., description="이 자료에서 주목해야 할 주요 분석 포인트"
    )


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
        'CAREER', 'CHARACTER', 'COMPETENCY', 'METHODOLOGY',
        'MOTIVATION', 'POTENTIAL', 'FIT', 'SIMULATION'
    ] = Field(..., description="분석 항목의 대분류")
    title: str = Field(..., description="분석 항목의 제목")
    analysis: str = Field(..., description="분석 내용")
    evidence: str = Field(..., description="분석의 근거")
    score: float = Field(
        ..., description="항목별 점수 (100점 만점)", ge=0, le=100
    )


class InsightItem(BaseModel):
    title: str = Field(..., description="인사이트 항목의 제목")
    analysis: str = Field(..., description="분석 내용")
    evidence: str = Field(..., description="분석의 근거")


class OverallReliability(BaseModel):
    title: str = Field(..., description="전체 분석 신뢰도 제목")
    reliability: Literal[
        '매우 높음', '높음', '보통', '낮음'
    ] = Field(..., description="분석 결과의 신뢰도")


class ReportData(BaseModel):
    candidate_info: CandidateInfo = Field(..., alias='candidate_info')
    material_analysis: List[MaterialAnalysis] = Field(
        ..., alias='material_analysis'
    )
    comprehensive_report: ComprehensiveReport = Field(
        ..., alias='comprehensive_report'
    )
    analysis_items: List[AnalysisItem] = Field(..., alias='analysis_items')
    executive_insights: List[InsightItem] = Field(
        ..., alias='executive_insights'
    )
    hr_points: List[InsightItem] = Field(..., alias='hr_points')
    overall_reliability: OverallReliability = Field(
        ..., alias='overall_reliability'
    )

    class Config:
        populate_by_name = True
