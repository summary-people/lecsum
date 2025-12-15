from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from app.core.prompt_templates.summary_prompt import get_summary_prompt
from app.core.prompt_templates.keyword_prompt import get_keyword_prompt
from app.core.prompt_templates.quiz_prompt import (get_quiz_prompt, get_grading_prompt)
from app.core.prompt_templates.retry_quiz_prompt import get_retry_quiz_prompt

from app.db.quiz_schemas import QuizResponse, GradeResultList

chatOpenAI = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 자유 텍스트 체인 (요약, 키워드)
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

# 정형 출력 체인 (퀴즈, 채점)
def build_structured_chain(llm, prompt, output_schema) -> Runnable:
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

# 오답 재시험 체인
retry_quiz_chain: Runnable = build_structured_chain(
    chatOpenAI,
    get_retry_quiz_prompt(),
    QuizResponse,
)