# GPT-4o-mini 호출 래퍼
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from app.core.prompt_templates.quiz_prompt import *
from app.db.quiz_schemas import *

chatOpenAI = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

def build_llm_chain(llm, prompt, output) -> Runnable:
    # 구조화된 출력(Structured Output) 설정
    structured_llm = llm.with_structured_output(output)
    chain = prompt | structured_llm
    return chain

quiz_chain = build_llm_chain(chatOpenAI, get_quiz_prompt(), QuizResponse)
grade_chain = build_llm_chain(chatOpenAI, get_grading_prompt(), GradeResultList)