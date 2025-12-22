# 문서 요약 프롬프트 템플릿 (NLP 강의 기준)
from langchain_core.prompts import ChatPromptTemplate

def get_summary_prompt(summary_type: str) -> ChatPromptTemplate:
    # -------------------------------
    # System Prompt (Mode-dependent)
    # -------------------------------
    if summary_type == "lecture":
        system_prompt = """
        당신은 '대학 수준의 NLP 강의 전용 요약 전문가'입니다.
        당신의 목표는 주어진 [강의 내용]을 학습자가 한 번에 이해할 수 있도록
        정확하고 구조화된 형태로 요약하는 것입니다.

        [요약 목적: Lecture Summary]
        - 학습자 복습 중심
        - 개념 정의 + 처리 흐름 + 핵심 원리 중심
        """
    elif summary_type == "bullet":
        system_prompt = """
        당신은 '핵심 개념만 빠르게 추출하는 전문 요약 도우미'입니다.

        [요약 목적: Bullet Summary]
        - 불릿 포인트 중심
        - 중요 개념, 핵심 용어, 메커니즘만 포함
        """
    elif summary_type == "exam":
        system_prompt = """
        당신은 '시험 대비 전용 요약 전문가'입니다.

        [요약 목적: Exam Summary]
        - 정의/구조/핵심 개념 위주
        - 교수자가 출제할 가능성이 높은 요소 중심 요약
        """
    else:
        system_prompt = """
        당신은 문서 내용을 간단히 요약하는 도우미입니다.
        """

    # -------------------------------
    # Few-shot Examples (Multiple Styles)
    # -------------------------------

    # Example A: Standard Lecture Summary
    exA_context = """
        자연어 처리(NLP)는 인간의 언어를 컴퓨터가 이해하도록 만드는 AI 분야이다.
        NLP는 형태소 분석, 구문 분석, 의미 분석과 같은 처리 단계를 거치며,
        최근에는 Transformer 기반 모델이 성능 향상에 핵심 역할을 한다.
        """

    exA_output = """
        ## 📌 핵심 요약

        ### 1. NLP 개요
        - 인간 언어를 컴퓨터가 이해하도록 만드는 AI 분야
        - 텍스트 의미 분석이 주된 목적

        ### 2. NLP 처리 파이프라인
        - **형태소 분석**: 단어의 최소 의미 단위 분리
        - **구문 분석**: 문장 구조 파악
        - **의미 분석**: 문장 의미 해석

        ### 3. 최신 기술 트렌드
        - 딥러닝 기반 접근이 주류
        - **Transformer** 구조가 핵심 성능 향상 요인
        """

    # Example B: Bullet Summary
    exB_context = """
        머신러닝은 데이터 패턴을 학습하여 예측을 수행하는 기술이다.
        대표 알고리즘은 회귀 분석, SVM, 결정 트리, 랜덤 포레스트 등이 있다.
        """

    exB_output = """
        - 머신러닝: 데이터 패턴 학습 기반 예측 기술
        - 주요 알고리즘: 회귀 분석, SVM, 결정 트리, 랜덤 포레스트
        - 목적: 분류, 회귀, 패턴 분석
        """

    # Example C: Exam Summary
    exC_context = """
        딥러닝은 인공신경망을 기반으로 하는 학습 기술이다.
        CNN은 이미지 처리에 강하며 RNN은 시계열에 적합하다.
        Transformer는 Attention 메커니즘을 활용해 병렬 처리가 가능하다.
        """

    exC_output = """
        ## 시험 대비 핵심 정리

        ### 1. 딥러닝 정의
        - 인공신경망 기반 학습 알고리즘

        ### 2. 모델 구조별 특징
        - **CNN**: 이미지 처리에 최적화
        - **RNN**: 순차/시계열 데이터 처리
        - **Transformer**: Attention 기반, 병렬 처리 가능

        ### 3. 출제 포인트
        - CNN vs RNN 비교
        - Transformer의 Attention 개념
        """

    # -------------------------------
    # Template Construction
    # -------------------------------
    return ChatPromptTemplate.from_messages([
        (
            "system",
            system_prompt + """

            [전체 요약 규칙]
            1. **구조화 mandatory**: 제목(##), 소제목(###), 불릿 유지.
            2. **핵심 중심**: 정의, 구조, 처리 흐름, 기술만 요약.
            3. **예시 남용 금지**: 부연 설명·서술형 예시 제거.
            4. **전문 용어 정확성 유지**.
            5. **과도한 분량 금지**: A4 1페이지 이내.
            6. **출력은 요약만 포함** (여분 텍스트, 시스템 문구 금지).

            =================================
            [Few-shot Example A — Lecture Summary]
            """
        ),

        # Few-shot A
        ("human", f"강의 내용:\n{exA_context}"),
        ("ai", exA_output),

        # Few-shot B
        ("system", "\n=================================\n[Few-shot Example B — Bullet Summary]"),
        ("human", f"강의 내용:\n{exB_context}"),
        ("ai", exB_output),

        # Few-shot C
        ("system", "\n=================================\n[Few-shot Example C — Exam Summary]"),
        ("human", f"강의 내용:\n{exC_context}"),
        ("ai", exC_output),

        # Actual Input
        ("system", "\n=================================\n[실제 요청 입력]"),
        ("human", "강의 내용:\n{context}")
    ])