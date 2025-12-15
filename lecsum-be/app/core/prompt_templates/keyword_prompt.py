# 키워드 추출 프롬프트 템플릿
from langchain_core.prompts import ChatPromptTemplate

def get_keyword_prompt() -> ChatPromptTemplate:
    example_context = """
    자연어 처리(NLP)는 인간의 언어를 컴퓨터가 이해하고 처리할 수 있도록 하는 인공지능 분야이다.
    형태소 분석, 구문 분석, 의미 분석 등의 처리 단계를 포함한다.
    최근에는 Transformer 기반 딥러닝 모델이 NLP 성능을 크게 향상시켰다.
    """

    example_output = """
    자연어 처리, NLP, 형태소 분석, 구문 분석, 의미 분석, 딥러닝, Transformer
    """

    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 강의 자료에서 핵심 키워드를 추출하는 전문가다.
        주어진 [텍스트]에서 학습 및 검색에 중요한 키워드를 추출하라.

        [키워드 추출 규칙]
        1. **개념 중심**: 이론, 기술, 모델 이름 위주로 추출
        2. **중복 제거**
        3. **불필요한 일반 단어 제외**
        4. **10개 이내 키워드**
        5. **쉼표(,)로 구분된 한 줄 출력**

        출력에는 키워드만 포함해야 한다.
        """),

        # Few-shot
        ("human", f"텍스트:\n{example_context}"),
        ("ai", example_output),

        # 실제 요청
        ("human", "텍스트:\n{context}")
    ])