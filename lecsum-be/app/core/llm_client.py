# GPT-4o-mini 호출 래퍼
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable

# 환경변수 로드
load_dotenv()

# API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

chatOpenAI = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

# 챗봇용 LLM (temperature 약간 높여서 자연스러운 대화)
chatbot_llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4o-mini",
)

def build_llm_chain(llm, prompt, output) -> Runnable:
    # 구조화된 출력(Structured Output) 설정
    structured_llm = llm.with_structured_output(output)
    chain = prompt | structured_llm
    return chain
