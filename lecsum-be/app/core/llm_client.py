import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.core.prompt_templates.quiz_prompt import *
from app.db.quiz_schemas import *

from app.core.prompt_templates.summary_prompt import get_summary_prompt
from app.core.prompt_templates.keyword_prompt import get_keyword_prompt
from app.core.prompt_templates.quiz_prompt import (get_quiz_prompt, get_grading_prompt)
from app.core.prompt_templates.retry_quiz_prompt import get_retry_quiz_prompt
from app.db.quiz_schemas import QuizResponse, GradeResultList
from langchain_core.output_parsers import JsonOutputParser

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

chatbot_llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4o-mini",
)

# -----------------------------
# 자유 텍스트 출력 체인
# -----------------------------
def route_summary_prompt(inputs: dict):
    """
    summary_type에 따라 요약 프롬프트를 분기한다.
    inputs = {
        "context": str,
        "summary_type": str
    }
    """
    summary_type = inputs.get("summary_type", "lecture")
    return {
        "context": inputs["context"],
        "prompt": get_summary_prompt(summary_type)
    }

summary_chain: Runnable = (
    RunnableLambda(route_summary_prompt)
    | RunnablePassthrough.assign(context=lambda x: x["context"])
    | (lambda x: x["prompt"])
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

def build_llm_chain(llm, prompt) -> Runnable:
    chain = prompt | llm | StrOutputParser()
    return chain


quiz_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_quiz_prompt(),
    QuizGenerationOutput,
)
critic_chain: Runnable = build_llm_chain(
    chatOpenAI,
    get_critic_prompt()
)
refiner_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_refiner_prompt(), 
    QuizGenerationOutput
)

def route_quiz_generation(info):
    critique = info["critique"]
    
    # 비평 로그 출력
    print("\n[👀 Critic's Review]\n", critique)
    print("-" * 50)

    if "수정 사항 없음" in critique:
        print("✅ 검수 통과: 초안을 그대로 확정합니다.")
        return info["initial_quiz"]
    else:
        print("⚠️ 수정 필요: Refiner를 가동합니다.")
        return refiner_chain

def build_quiz_multichain():
    return (
        # Step 1: 초안 생성
        RunnablePassthrough.assign(
            initial_quiz=quiz_chain
        )
        # Step 2: 비평 생성 (Critic에게는 JSON 문자열로 변환해서 전달)
        .assign(
            critique=RunnablePassthrough.assign(
                initial_quiz=lambda x: x["initial_quiz"].model_dump_json(indent=2)
            ) | critic_chain
        )
        # Step 3: Refiner를 위한 데이터 전처리 (Pydantic -> JSON String)
        # Refiner 프롬프트에 들어갈 {initial_quiz}가 문자열이어야 잘 인식함
        .assign(
            initial_quiz=lambda x: x["initial_quiz"].model_dump_json(indent=2) 
            if "수정 사항 없음" not in x["critique"] else x["initial_quiz"]
        )
        # Step 4: 라우팅 (수정 필요하면 Refiner, 아니면 Pass)
        | RunnableLambda(route_quiz_generation)
    )

# MultiChain
quiz_critic_refiner_chain = build_quiz_multichain()

# 채점 - 해설 보강 Chain
grade_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_grading_prompt(),
    GradeResultList,
)
enrich_chain: Runnable = build_llm_chain(
    ChatOpenAI(model="gpt-4o-mini", temperature=0.7),
    get_enrichment_prompt()
)

# 오답 재시험 체인
retry_quiz_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_retry_quiz_prompt(),
    QuizResponse, # 퀴즈 생성과 동일한 방식으로 재시험 생성
)

top_sentence_chain: Runnable = (
    ChatPromptTemplate.from_template("""
    다음 문서에서 가장 중요한 문장 {k}개를 추출하라.
    JSON 배열로 반환하라.

    {context}
    """)
    | chatOpenAI
    | JsonOutputParser()
)
