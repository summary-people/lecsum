# GPT-4o-mini 호출 래퍼
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from app.core.prompt_templates.quiz_prompt import *
from app.db.quiz_schemas import *

chatOpenAI = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

def build_llm_chain_structured(llm, prompt, output) -> Runnable:
    # 구조화된 출력(Structured Output) 설정
    structured_llm = llm.with_structured_output(output)
    chain = prompt | structured_llm
    return chain

def build_llm_chain(llm, prompt) -> Runnable:
    chain = prompt | llm | StrOutputParser()
    return chain

quiz_chain = build_llm_chain_structured(chatOpenAI, get_quiz_prompt(), QuizGenerationOutput)
critic_chain = build_llm_chain(chatOpenAI, get_critic_prompt())
refiner_chain = build_llm_chain_structured(chatOpenAI, get_refiner_prompt(), QuizGenerationOutput)

grade_chain = build_llm_chain_structured(chatOpenAI, get_grading_prompt(), GradeResultList)

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

def build_reflection_chain():
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

final_reflection_chain = build_reflection_chain()