# 문서 요약 프롬프트 템플릿 (NLP 강의 기준)
from langchain_core.prompts import ChatPromptTemplate

def get_summary_prompt(summary_type: str) -> ChatPromptTemplate:
    if summary_type == "lecture":
        system_prompt = """당신은 대학 수준의 자연어 처리(NLP) 강의를 요약하는 전문 학습 도우미다.
        주어진 [강의 내용]을 바탕으로 학생이 빠르게 복습할 수 있도록 요약을 작성하라."""
    elif summary_type == "bullet":
        system_prompt = """당신은 문서의 핵심만을 불릿 포인트로 정리하는 요약 도우미다.
        중요한 개념과 키워드 위주로 간결하게 요약하라."""
    elif summary_type == "exam":
        system_prompt = """당신은 시험 대비 요약을 생성하는 도우미다.
        정의, 핵심 개념, 출제 가능 포인트 위주로 요약하라."""
    else:
        system_prompt = """당신은 문서를 간단히 요약하는 도우미다."""

    example_context = """
    자연어 처리(NLP)는 인간의 언어를 컴퓨터가 이해하고 처리할 수 있도록 하는 인공지능 분야이다.
    NLP는 형태소 분석, 구문 분석, 의미 분석 등의 단계를 거쳐 텍스트를 구조적으로 해석한다.
    최근에는 딥러닝 기반 모델, 특히 Transformer 구조가 NLP 성능을 크게 향상시켰다.
    """

    example_output = """
    ## 📌 핵심 요약

    ### 1. 자연어 처리(NLP) 개요
    - 인간의 언어를 컴퓨터가 이해하고 처리하도록 하는 인공지능 분야
    - 텍스트 데이터 분석 및 의미 해석이 핵심 목적

    ### 2. NLP 처리 단계
    - **형태소 분석**: 문장을 의미 단위로 분리
    - **구문 분석**: 문장 구조 파악
    - **의미 분석**: 문장의 의미 해석

    ### 3. 최신 NLP 트렌드
    - 딥러닝 기반 접근 방식이 주류
    - **Transformer 구조**가 성능 향상에 핵심 역할
    """

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt + """

        [요약 작성 규칙]
        1. **구조화 필수**: 제목, 소제목, 불릿 포인트를 사용해라.
        2. **핵심 위주**: 정의, 개념, 처리 흐름, 핵심 기술만 정리해라.
        3. **불필요한 예시 제거**: 설명용 장황한 예시는 생략해라.
        4. **명확한 용어 사용**: NLP 표준 용어를 사용해라.
        5. **분량 제한**: 전체 요약은 A4 1페이지 이내.
        6. **마크다운 형식 유지**: 제목은 ##, 소제목은 ### 사용.

        출력은 반드시 요약 결과만 포함해야 한다.
        """),

        # Few-shot
        ("human", f"강의 내용:\n{example_context}"),
        ("ai", example_output),

        # 실제 요청
        ("human", "강의 내용:\n{context}")
    ])