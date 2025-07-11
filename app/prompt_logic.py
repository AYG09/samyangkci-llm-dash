from typing import List
from .components.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def generate_custom_prompt(
    name: str,
    organization: str,
    position: str,
    interview_date: str,
    salary: str,
    career_year: str,
    uploaded_materials_list: List[str],
    extra_instructions: str
) -> str:
    """
    사용자 입력을 기반으로 LLM에 전달할 최종 프롬프트를 생성합니다.
    시스템 프롬프트와 사용자 프롬프트를 결합합니다.
    """
    if uploaded_materials_list:
        materials_str = "\n".join([f"- {m}" for m in uploaded_materials_list])
    else:
        materials_str = "- (선택/입력된 자료 없음)"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        name=name or "미입력",
        organization=organization or "미입력",
        position=position or "미입력",
        interview_date=interview_date or "미입력",
        salary=salary or "미입력",
        career_year=career_year or "미입력",
        uploaded_materials=materials_str,
        extra_instructions=extra_instructions or "특별한 추가 지시사항 없음."
    )

    # 시스템 프롬프트와 사용자 프롬프트를 결합하여 최종 프롬프트 생성
    final_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    
    return final_prompt