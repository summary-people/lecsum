import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from app.core.prompt_templates.summary_prompt import get_summary_prompt
from app.core.prompt_templates.keyword_prompt import get_keyword_prompt
from app.core.prompt_templates.quiz_prompt import (
    get_quiz_prompt,
    get_grading_prompt,
)

from app.db.quiz_schemas import QuizResponse, GradeResultList

# 환경변수 로드
load_dotenv()

# API 키 검증
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# 공통 LLM 인스턴스
chatOpenAI = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# -----------------------------
# 자유 텍스트 출력 체인
# -----------------------------
summary_chain: Runnable = (
    get_summary_prompt()
    | chatOpenAI
    | StrOutputParser()
)

keyword_chain: Runnable = (
    get_keyword_prompt()
    | chatOpenAI
    | StrOutputParser()
)

# -----------------------------
# 구조화 출력 체인
# -----------------------------
def build_structured_chain(
    llm: ChatOpenAI,
    prompt,
    output_schema,
) -> Runnable:
    """
    Structured Output(JSON Schema) 기반 체인 생성
    """
    structured_llm = llm.with_structured_output(output_schema)
    return prompt | structured_llm


quiz_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_quiz_prompt(),
    QuizResponse,
)

grade_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_grading_prompt(),
    GradeResultList,
)
