# 문서 요약 프롬프트 템플릿 (NLP 강의 기준)
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPTS = {
    "lecture": """
        당신은 대학 수준의 자연어 처리(NLP) 강의를 요약하는 전문 학습 도우미다.
        주어진 [강의 내용]을 바탕으로 학생이 빠르게 복습할 수 있도록 요약을 작성하라.

        [요약 작성 규칙]
        1. **구조화 필수**: 제목, 소제목, 불릿 포인트를 사용해라.
        2. **핵심 위주**: 정의, 개념, 처리 흐름, 핵심 기술만 정리해라.
        3. **불필요한 예시 제거**: 설명용 장황한 예시는 생략해라.
        4. **명확한 용어 사용**: NLP 표준 용어를 사용해라.
        5. **분량 제한**: 전체 요약은 A4 1페이지 이내.
        6. **마크다운 형식 유지**: 제목은 ##, 소제목은 ### 사용.

        출력은 반드시 요약 결과만 포함해야 한다.
        """,
    "bullet": """
        당신은 주어진 텍스트를 간결한 불릿 포인트로만 요약하는 전문 도우미다.
        문단은 사용하지 말고, 각 섹션당 최대 5개의 불릿만 작성하라.
        핵심 정보만 포함하고 불필요한 설명이나 예시는 생략해라.
        마크다운 형식의 불릿 리스트로 작성하라.

        출력은 반드시 요약 결과만 포함해야 한다.
        """,
    "exam": """
        당신은 주어진 강의 내용을 정의, 핵심 개념, 그리고 예상 시험 문제 중심으로 요약하는 전문 도우미다.
        Q&A 형식의 제목과 소제목을 사용하여 작성하라.
        시험에 나올 가능성이 높은 질문과 답변을 포함하라.
        마크다운 형식을 유지하라.

        출력은 반드시 요약 결과만 포함해야 한다.
        """
}

def get_summary_prompt(summary_type: str):
    if summary_type == "lecture":
        return ChatPromptTemplate.from_template("""
        다음 강의 자료를 강의 노트 형태로 체계적으로 요약하라.
        - 제목, 소제목 구조 유지
        - 정의 → 설명 → 예시 순서
        - 마크다운 사용
        {context}
        """)

    if summary_type == "bullet":
        return ChatPromptTemplate.from_template("""
        다음 문서를 핵심 위주 불릿 포인트로 요약하라.
        - 중요 개념만
        - 간결한 문장
        {context}
        """)

    if summary_type == "exam":
        return ChatPromptTemplate.from_template("""
        다음 문서를 시험 대비 요약으로 정리하라.
        - 암기 포인트 강조
        - 용어 정의 명확히
        {context}
        """)
    
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

    system_prompt = SYSTEM_PROMPTS.get(summary_type, SYSTEM_PROMPTS["lecture"])

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),

        # Few-shot
        ("human", f"강의 내용:\n{example_context}"),
        ("ai", example_output),

        # 실제 요청
        ("human", "강의 내용:\n{context}")
    ])