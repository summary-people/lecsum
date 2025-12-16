# 오답 재시험 문제 생성 프롬프트 (Few-shot)
from langchain_core.prompts import ChatPromptTemplate

def get_retry_quiz_prompt():
    """
    ChatPromptTemplate을 사용한 오답 재시험 문제 생성 프롬프트
    Few-shot 예시를 user-assistant 대화 형식으로 구성
    """
    return ChatPromptTemplate.from_messages([
        ("system", """당신은 교육 전문가입니다. 학생이 틀린 문제를 기반으로 유사한 문제를 생성하여 복습을 도와주세요.

# 생성 가이드라인
1. **개념 유지**: 원본 문제와 동일한 핵심 개념을 다루되, 표현과 예시는 다르게
2. **난이도 유사**: 원본과 비슷한 수준의 난이도 유지
3. **유형 다양화**: 가능하면 다양한 문제 유형 사용 (객관식, 단답형, O/X 등)
4. **실용적**: 학습에 도움이 되는 실질적인 문제
5. **명확한 해설**: 각 문제마다 상세한 해설 포함

# 문제 유형
- multiple_choice: 4지선다 (options에 4개 보기)
- true_false: O/X 문제 (options에 ["O", "X"])
- short_answer: 단답형 (options 빈 리스트)
- fill_in_blank: 빈칸 채우기 (options 빈 리스트)"""),

        # Few-shot 예시 1: 머신러닝 - 과적합
        ("user", """원본 문제:
```
문제 유형: short_answer
질문: 머신러닝의 과적합이란 무엇인가?
정답: 훈련 데이터에 과도하게 맞춰져 새로운 데이터에 대한 성능이 떨어지는 현상
해설: 과적합은 모델이 훈련 데이터의 노이즈까지 학습하여 일반화 성능이 낮아지는 문제입니다.
```

위 문제를 기반으로 유사한 문제 3개를 생성해주세요."""),

        ("assistant", """{{
  "quiz_set_id": 0,
  "quizzes": [
    {{
      "question": "과적합을 방지하는 방법으로 적절하지 않은 것은?",
      "type": "multiple_choice",
      "options": ["정규화", "데이터 증강", "학습률 증가", "드롭아웃"],
      "correct_answer": "학습률 증가",
      "explanation": "학습률 증가는 과적합 방지와 관계없으며, 오히려 학습 불안정을 야기할 수 있습니다. 정규화, 데이터 증강, 드롭아웃은 모두 과적합 방지 기법입니다."
    }},
    {{
      "question": "과적합이 발생하면 훈련 데이터 손실은 낮지만 검증 데이터 손실은 높다.",
      "type": "true_false",
      "options": ["O", "X"],
      "correct_answer": "O",
      "explanation": "과적합 시 훈련 데이터에는 잘 맞지만 새로운 데이터(검증 데이터)에는 성능이 떨어지므로, 훈련 손실과 검증 손실의 차이가 크게 벌어집니다."
    }},
    {{
      "question": "과적합을 진단하기 위해 훈련 손실과 비교해야 할 지표는 무엇인가?",
      "type": "short_answer",
      "options": [],
      "correct_answer": "검증 손실",
      "explanation": "과적합은 훈련 손실과 검증 손실의 차이가 클 때 발생하므로, 검증 데이터의 손실을 모니터링해야 합니다."
    }}
  ]
}}"""),

        # Few-shot 예시 2: 데이터베이스 - 정규화
        ("user", """원본 문제:
```
문제 유형: multiple_choice
질문: 데이터베이스 정규화의 주된 목적은?
보기: ["데이터 중복 최소화", "쿼리 속도 향상", "저장 공간 증가", "복잡도 증가"]
정답: 데이터 중복 최소화
해설: 정규화는 데이터 중복을 줄여 이상 현상을 방지하는 것이 주된 목적입니다.
```

위 문제를 기반으로 유사한 문제 3개를 생성해주세요."""),

        ("assistant", """{{
  "quiz_set_id": 0,
  "quizzes": [
    {{
      "question": "정규화를 통해 방지할 수 있는 이상 현상이 아닌 것은?",
      "type": "multiple_choice",
      "options": ["삽입 이상", "삭제 이상", "갱신 이상", "조회 이상"],
      "correct_answer": "조회 이상",
      "explanation": "정규화는 삽입, 삭제, 갱신 이상을 방지합니다. 조회 이상은 정규화와 관련 없는 개념입니다."
    }},
    {{
      "question": "제3정규형을 만족하려면 ____ 종속성을 제거해야 한다.",
      "type": "fill_in_blank",
      "options": [],
      "correct_answer": "이행적 함수",
      "explanation": "제3정규형(3NF)은 이행적 함수 종속성을 제거하여 모든 속성이 기본키에만 종속되도록 하는 것입니다."
    }},
    {{
      "question": "정규화 수준이 높을수록 항상 쿼리 성능이 향상된다.",
      "type": "true_false",
      "options": ["O", "X"],
      "correct_answer": "X",
      "explanation": "정규화 수준이 높으면 데이터 무결성은 향상되지만, 조인이 많아져 오히려 쿼리 성능이 저하될 수 있습니다. 이 경우 반정규화를 고려합니다."
    }}
  ]
}}"""),

        # Few-shot 예시 3: 네트워크 - TCP
        ("user", """원본 문제:
```
문제 유형: true_false
질문: TCP는 비연결형 프로토콜이다.
보기: ["O", "X"]
정답: X
해설: TCP는 연결 지향형 프로토콜이며, 3-way handshake를 통해 연결을 수립합니다. 비연결형은 UDP입니다.
```

위 문제를 기반으로 유사한 문제 3개를 생성해주세요."""),

        ("assistant", """{{
  "quiz_set_id": 0,
  "quizzes": [
    {{
      "question": "TCP가 연결을 수립할 때 사용하는 방식은?",
      "type": "multiple_choice",
      "options": ["2-way handshake", "3-way handshake", "4-way handshake", "handshake 없음"],
      "correct_answer": "3-way handshake",
      "explanation": "TCP는 SYN, SYN-ACK, ACK 세 단계로 이루어진 3-way handshake를 통해 연결을 수립합니다."
    }},
    {{
      "question": "TCP 연결 종료 시 사용되는 handshake 단계 수는?",
      "type": "short_answer",
      "options": [],
      "correct_answer": "4",
      "explanation": "TCP 연결 종료는 FIN, ACK, FIN, ACK의 4단계(4-way handshake)로 이루어집니다."
    }},
    {{
      "question": "TCP와 달리 ____ 프로토콜은 비연결형이며 신뢰성을 보장하지 않는다.",
      "type": "fill_in_blank",
      "options": [],
      "correct_answer": "UDP",
      "explanation": "UDP는 비연결형 프로토콜로 빠르지만 신뢰성을 보장하지 않으며, TCP와 대비되는 특성을 가집니다."
    }}
  ]
}}"""),

        # 실제 요청
        ("user", """원본 문제:
```
{original_quiz}
```

위 문제를 기반으로 유사한 문제 3개를 생성해주세요. JSON 형식으로 반환하며, 각 문제는 원본 문제의 핵심 개념을 다루되 다양한 유형과 표현을 사용하세요.""")
    ])
