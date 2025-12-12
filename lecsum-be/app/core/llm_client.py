# GPT-4o-mini 호출 래퍼
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable

chatOpenAI = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

def build_llm_chain(llm, prompt, output) -> Runnable:
    # 구조화된 출력(Structured Output) 설정
    structured_llm = llm.with_structured_output(output)
    chain = prompt | structured_llm
    return chain
