# 문제 생성 / 채점 프롬프트 템플릿
from langchain_core.prompts import ChatPromptTemplate

## 퀴즈 생성 - 비평 - 수정 MultiChain 프롬프트
# 퀴즈 생성
def get_quiz_prompt() -> ChatPromptTemplate:
    # Few-shot
    example_context = """
    객체 지향 프로그래밍(OOP)은 프로그램을 수많은 '객체(Object)'라는 기본 단위로 나누고 이들의 상호작용으로 로직을 구성하는 방식이다. 
    OOP의 4대 특징은 캡슐화, 상속, 다형성, 추상화이다.
    클래스(Class)는 객체를 만들기 위한 설계도이며, 인스턴스(Instance)는 그 설계도에 따라 실제 메모리에 생성된 실체를 의미한다.
    상속을 통해 부모 클래스의 속성과 메서드를 자식 클래스가 물려받아 재사용성을 높일 수 있다.
    """
    
    example_output = """
    {{
        "quizzes": [
            {{
                "type": "multiple_choice",
                "question": "다음 중 객체 지향 프로그래밍(OOP)의 4대 특징에 포함되지 않는 것은?",
                "options": ["캡슐화", "상속", "절차지향", "다형성"],
                "correct_answer": "절차지향",
                "explanation": "OOP의 4대 특징은 캡슐화, 상속, 다형성, 추상화입니다. 절차지향은 OOP와 대비되는 프로그래밍 패러다임입니다."
            }},
            {{
                "type": "true_false",
                "question": "Java의 Garbage Collector는 개발자가 직접 메모리를 해제해야 작동한다.",
                "options": ["O", "X"],
                "correct_answer": "X",
                "explanation": "Java는 GC가 자동으로 사용하지 않는 메모리를 해제해줍니다."
            }},
            {{
                "type": "fill_in_blank",
                "question": "부모 클래스의 기능을 자식 클래스가 물려받아 사용하는 개념을 _____ 이라고 한다.",
                "options": [],
                "correct_answer": "상속",
                "explanation": "상속(Inheritance)을 사용하면 코드의 재사용성을 높이고 유지보수를 용이하게 할 수 있습니다."
            }},
            {{
                "type": "multiple_choice",
                "question": "클래스와 인스턴스에 대한 설명으로 올바른 것은?",
                "options": [
                    "클래스는 실제로 메모리에 할당된 실체다.",
                    "하나의 클래스로는 하나의 인스턴스만 만들 수 있다.",
                    "인스턴스는 설계도이고 클래스는 실체다.",
                    "인스턴스는 클래스를 바탕으로 구현된 구체적인 실체다."
                ],
                "correct_answer": "인스턴스는 클래스를 바탕으로 구현된 구체적인 실체다.",
                "explanation": "클래스는 추상적인 설계도이고, 인스턴스는 그 설계도를 바탕으로 실제 메모리에 구현된 것입니다."
            }},
            {{
                "type": "short_answer",
                "question": "OOP에서 '객체'란 무엇을 의미하는가?",
                "options": [],
                "correct_answer": "프로그램의 기본 단위이자 로직을 구성하는 주체",
                "explanation": "객체는 데이터와 기능을 하나로 묶은 단위로, 객체 간의 상호작용을 통해 프로그램이 동작합니다."
            }}
        ]
    }}
    """

    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 베테랑 강사다. 주어진 [강의 내용]을 꼼꼼히 분석하여 학생들의 이해도를 평가할 수 있는 퀴즈를 5개 생성해라.
         
        [중복 방지 지침]
        아래 **[최근 생성된 퀴즈 목록]**을 반드시 확인하라.
        이 목록에 있는 문제들과 **동일하거나 의도가 겹치는 문제는 절대 다시 출제하지 마라.**
        이미 다룬 개념이라면 다른 측면을 묻거나, 난이도를 다르게 하거나, 전혀 다른 개념을 찾아 출제하라.
         
        [문제 유형 가이드]
        1. **multiple_choice**: 4지 선다형. 정답 1개.
        2. **true_false**: 사실 관계를 묻는 O/X 퀴즈.
        3. **short_answer**: 핵심 용어나 개념을 묻는 단답형.
        4. **fill_in_blank**: 문맥상 들어갈 알맞은 단어를 채우는 빈칸 채우기.

        [지시사항]
        1. **내용 선정**: 강의 내용 중 학습자가 반드시 알아야 할 핵심 개념(Key Concepts) 위주로 문제를 출제해라.
        2. **유형 배분**: 위 [문제 유형 가이드]의 4가지 유형을 모두 최소 1문제씩 포함하여 다양하게 구성해라.
        3. **오답 구성**: 오답(Distractor)은 정답과 헷갈릴 수 있는 매력적인 내용이어야 한다.
        4. **해설 작성**: 정답인 이유와 오답인 이유를 명확히 설명해라.
        """),
        # Few-shot
        ("human", f"강의 내용: {example_context}"),
        ("ai", example_output),

        # 실제 요청
        ("human", """
        [강의 내용]
        {context}
        
        [최근 생성된 퀴즈 목록 (출제 금지)]
        {recent_quizzes}
        """),
    ])

# 비평
def get_critic_prompt() -> ChatPromptTemplate:
    # ------------------------------------------------------------------
    # Few-shot 1: [혼합 케이스] 
    # 상황: 5문제 중 2개 정상, 3개 오류(사실오류, 환각)
    # 유형: 객관식, OX, 단답형 혼합
    # ------------------------------------------------------------------
    example_mixed_context = """
    [파이썬 자료구조]
    1. 리스트(List): 대괄호 []를 사용하며, 요소를 수정할 수 있는 가변(Mutable) 객체다.
    2. 튜플(Tuple): 소괄호 ()를 사용하며, 한 번 생성하면 수정할 수 없는 불변(Immutable) 객체다.
    3. 딕셔너리(Dict): 중괄호 {{}}를 사용하여 Key-Value 쌍으로 저장한다. Key는 중복될 수 없다.
    """
    
    example_mixed_quiz = """
    {{
      "quizzes": [
        {{
          "id": 0,
          "type": "multiple_choice",
          "question": "파이썬에서 리스트를 생성할 때 사용하는 기호는?",
          "options": ["중괄호 {{}}", "소괄호 ()", "대괄호 []", "꺽쇠 <>"],
          "correct_answer": "대괄호 []",
          "explanation": "리스트는 대괄호 []로 선언합니다."
        }},
        {{
          "id": 1,
          "type": "multiple_choice",
          "question": "다음 중 튜플(Tuple)의 특징으로 올바른 것은?",
          "options": ["내부 요소를 자유롭게 수정할 수 있다.", "소괄호를 사용한다.", "Key-Value 쌍이다.", "가변 객체이다."],
          "correct_answer": "내부 요소를 자유롭게 수정할 수 있다.",
          "explanation": "튜플은 가변 객체이므로 값 변경이 가능합니다."
        }},
        {{
          "id": 2,
          "type": "short_answer",
          "question": "딕셔너리(Dictionary)는 어떤 형태의 쌍으로 데이터를 저장하는가?",
          "options": [],
          "correct_answer": "Key와 Value",
          "explanation": "딕셔너리는 키와 값의 쌍으로 데이터를 저장합니다."
        }},
        {{
          "id": 3,
          "type": "true_false",
          "question": "C++의 Vector는 파이썬의 리스트보다 메모리 사용량이 적다.",
          "options": ["O", "X"],
          "correct_answer": "O",
          "explanation": "C++은 메모리 효율이 좋습니다."
        }},
        {{
          "id": 4,
          "type": "true_false",
          "question": "딕셔너리의 Key는 중복해서 설정할 수 있다.",
          "options": ["O", "X"],
          "correct_answer": "O",
          "explanation": "Key는 중복이 허용됩니다."
        }}
      ]
    }}
    """

    # 비평 내용은 그대로 유지 (오류가 있는 1, 3, 4번만 지적)
    example_mixed_critique = """
    - **Index 1 수정 제안**: 사실 관계 오류. 튜플은 '불변(Immutable)' 객체이므로 수정할 수 없다. 정답을 '소괄호를 사용한다'로 변경하고 해설을 바로잡아라.
    - **Index 3 수정 제안**: Hallucination(환각). [학습 자료]에는 'C++ Vector'에 대한 내용이 전혀 없다. 해당 문제는 삭제하거나 파이썬 딕셔너리 관련 문제로 교체하라.
    - **Index 4 수정 제안**: 사실 관계 오류. 딕셔너리의 Key는 '중복될 수 없다'. 정답을 'X'로 수정하고 해설을 'Key는 고유해야 하므로 중복될 수 없습니다'로 고쳐라.
    """

    # ------------------------------------------------------------------
    # Few-shot 2: [완벽한 케이스]
    # 상황: 5문제 모두 정상
    # ------------------------------------------------------------------
    example_good_context = """
    [광합성]
    식물은 빛 에너지를 이용하여 이산화탄소와 물을 포도당과 산소로 변환한다. 
    이 과정을 광합성이라고 한다. 광합성은 주로 잎의 엽록체에서 일어난다.
    """
    
    example_good_quiz = """
    {{
      "quizzes": [
        {{ 
            "id": 0, 
            "type": "short_answer", 
            "question": "식물이 양분을 만드는 과정을 무엇이라 하는가?", 
            "options": [], 
            "correct_answer": "광합성", 
            "explanation": "..." 
        }},
        {{ 
            "id": 1, 
            "type": "multiple_choice", 
            "question": "광합성에 필요한 재료가 아닌 것은?", 
            "options": ["이산화탄소", "물", "빛 에너지", "소금"], 
            "correct_answer": "소금", 
            "explanation": "..." 
        }},
        {{ 
            "id": 2, 
            "type": "fill_in_blank", 
            "question": "광합성 결과 생성되는 물질은 포도당과 _____ 이다.", 
            "options": [], 
            "correct_answer": "산소", 
            "explanation": "..." 
        }},
        {{ 
            "id": 3, 
            "type": "multiple_choice", 
            "question": "광합성이 주로 일어나는 장소는?", 
            "options": ["뿌리", "줄기", "엽록체", "꽃"], 
            "correct_answer": "엽록체", 
            "explanation": "..." 
        }},
        {{ 
            "id": 4, 
            "type": "true_false", 
            "question": "광합성은 밤에만 일어난다.", 
            "options": ["O", "X"], 
            "correct_answer": "X", 
            "explanation": "..." 
        }}
      ]
    }}
    """
    
    example_good_critique = "수정 사항 없음"

    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 꼼꼼하고 논리적인 '교육 콘텐츠 품질 관리자(QA Specialist)'다.
        강사가 생성한 [퀴즈 초안]을 [학습 자료]와 대조하여 정밀 검수를 수행하라.

        다음의 **평가 체크리스트**를 기준으로 엄격하게 분석하라:

        1. **Fact Check (사실 검증)**: 
           - 모든 문제와 정답은 오직 [학습 자료]에 근거해야 한다. 
           - 자료에 없는 내용(Hallucination)이나, 자료와 상충되는 정답이 있다면 지적하라.
        
        2. **Logical & Unambiguous (논리적 명확성)**:
           - 정답은 하나여야 하며, 오답(Distractor)이 정답으로 해석될 여지가 없어야 한다.
           - 해설(Explanation)이 정답의 근거를 논리적으로 설명하고 있는지 확인하라.

        3. **Quality & Redundancy (품질 및 중복)**:
           - 단순한 말장난 문제는 지양하라.
           - 앞의 문제와 내용이 겹치거나 똑같은 문제는 없는가?
           - 빈칸 채우기나 단답형의 정답이 너무 길거나 모호하지 않은가?

        [출력 형식 가이드]
        - 수정이 필요한 문제가 있다면, 해당 문제의 **번호(Index)**와 **수정 제안(구체적인 이유와 대안)**을 글머리 기호로 명시하라.
        - 만약 모든 문제가 완벽하다면, 오직 **"수정 사항 없음"**이라고만 출력하라.
        """),

        # Few-shot
        ("human", f"[학습 자료]\n{example_mixed_context}\n\n[퀴즈 초안]\n{example_mixed_quiz}"),
        ("ai", example_mixed_critique),
        
        ("human", f"[학습 자료]\n{example_good_context}\n\n[퀴즈 초안]\n{example_good_quiz}"),
        ("ai", example_good_critique),

        # 실제 입력
        ("human", """
        [학습 자료]
        {context}
        
        [퀴즈 초안]
        {initial_quiz}
        """)
    ])

# 수정
def get_refiner_prompt() -> ChatPromptTemplate:
    # Few-shot
    # 1. 학습 자료 (Context)
    example_context = """
    [파이썬 자료구조 핵심]
    1. 리스트(List): 대괄호 [] 사용. 순서가 있고 수정 가능(Mutable)하다.
    2. 튜플(Tuple): 소괄호 () 사용. 순서가 있지만 수정 불가능(Immutable)하다.
    3. 세트(Set): 중괄호 {{}} 사용. 순서가 없고 중복을 허용하지 않는다.
    4. 딕셔너리(Dict): Key-Value 쌍 구조. Key는 고유해야 한다.
    """

    # 2. 퀴즈 초안 (Initial Quiz) - 5문제 (오류 포함)
    example_initial_quiz = """
    {{
      "quizzes": [
        {{
          "id": 0,
          "type": "multiple_choice",
          "question": "파이썬 리스트의 선언 기호는?",
          "options": ["[]", "()", "{{}}"],
          "correct_answer": "[]",
          "explanation": "리스트는 대괄호를 사용합니다."
        }},
        {{
          "id": 1,
          "type": "true_false",
          "question": "튜플은 생성 후 내부 요소를 자유롭게 수정할 수 있다.",
          "options": ["O", "X"],
          "correct_answer": "O", 
          "explanation": "튜플은 가변 객체이므로 수정 가능합니다."
        }},
        {{
          "id": 2,
          "type": "short_answer",
          "question": "Key와 Value의 쌍으로 이루어진 자료구조는?",
          "options": [],
          "correct_answer": "딕셔너리",
          "explanation": "딕셔너리는 키-값 쌍으로 저장됩니다."
        }},
        {{
          "id": 3,
          "type": "true_false",
          "question": "세트(Set)는 데이터의 중복 저장을 허용한다.",
          "options": ["O", "X"],
          "correct_answer": "O",
          "explanation": "세트는 중복을 허용하는 자료구조입니다."
        }},
        {{
          "id": 4,
          "type": "multiple_choice",
          "question": "자바(Java)의 배열 선언 방식과 가장 유사한 것은?",
          "options": ["List", "Set", "Dict"],
          "correct_answer": "List",
          "explanation": "자바 배열과 리스트는 유사합니다."
        }}
      ]
    }}
    """

    # 3. 비평 (Critique) - 1, 3, 4번 지적
    example_critique = """
    - **Index 1 수정 제안**: 사실 관계 오류. 튜플은 '불변(Immutable)'이므로 수정할 수 없다. 정답을 'X'로 바꾸고 해설을 '튜플은 불변 객체입니다'로 수정하라.
    - **Index 3 수정 제안**: 사실 관계 오류. 세트(Set)는 '중복을 허용하지 않는다'. 정답을 'X'로 바꾸고 해설을 바로잡아라.
    - **Index 4 수정 제안**: Hallucination(환각). [학습 자료]에 '자바' 내용은 없다. 이 문제를 삭제하고 '세트의 괄호 기호'를 묻는 문제로 교체하라.
    """

    # 4. 최종 결과 (Final Quiz)
    example_final_quiz = """
    {{
      "quizzes": [
        {{
          "id": 0, "type": "multiple_choice",
          "question": "파이썬 리스트의 선언 기호는?",
          "options": ["[]", "()", "{{}}"],
          "correct_answer": "[]",
          "explanation": "리스트는 대괄호를 사용합니다."
        }},
        {{
          "id": 1, "type": "true_false",
          "question": "튜플은 생성 후 내부 요소를 자유롭게 수정할 수 있다.",
          "options": ["O", "X"],
          "correct_answer": "X",
          "explanation": "튜플은 불변(Immutable) 객체이므로 생성 후 수정할 수 없습니다."
        }},
        {{
          "id": 2, "type": "short_answer",
          "question": "Key와 Value의 쌍으로 이루어진 자료구조는?",
          "options": [],
          "correct_answer": "딕셔너리",
          "explanation": "딕셔너리는 키-값 쌍으로 저장됩니다."
        }},
        {{
          "id": 3, "type": "true_false",
          "question": "세트(Set)는 데이터의 중복 저장을 허용한다.",
          "options": ["O", "X"],
          "correct_answer": "X",
          "explanation": "세트(Set)는 중복된 값을 허용하지 않는 자료구조입니다."
        }},
        {{
          "id": 4, "type": "multiple_choice",
          "question": "파이썬에서 세트(Set)를 선언할 때 사용하는 기호는?",
          "options": ["()", "[]", "{{}}"],
          "correct_answer": "{{}}",
          "explanation": "세트는 중괄호 {{}}를 사용하여 선언합니다."
        }}
      ]
    }}
    """

    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 꼼꼼한 '최종 퀴즈 편집자(Final Editor)'다.
        [비평] 내용을 바탕으로 [퀴즈 초안]을 수정하여 완성도 높은 퀴즈 세트를 확정하라.
        
        [필수 지시사항]
        1. **지적된 문제 수정**: [비평]에서 구체적으로 지적한 문제(Index)를 찾아 올바르게 수정하라.
        2. **해설 동기화**: 정답을 변경할 경우, 반드시 **해설(Explanation)**도 변경된 정답에 맞게 논리적으로 다시 작성하라.
        3. **보존 원칙**: 비평에서 언급되지 않은(문제가 없는) 퀴즈는 절대 내용을 변경하지 말고 그대로 유지하라.
        """),

        # Few-shot
        ("human", f"""
        [학습 자료]
        {example_context}
        
        [퀴즈 초안]
        {example_initial_quiz}
        
        [비평]
        {example_critique}
        """),        
        ("ai", example_final_quiz),        


        # 실제 입력
        ("human", """
        [학습 자료]
        {context}
        
        [퀴즈 초안]
        {initial_quiz}
        
        [비평]
        {critique}
        """)
    ])







## 채점 - 해설 보강 MultiChain 프롬프트
# 채점 프롬프트
def get_grading_prompt() -> ChatPromptTemplate:
    """
    1차 채점용 프롬프트
    - 목적: 정답/오답 여부 판별 (Strict Grading)
    - 오답 처리: 상세 설명을 생략하고 "틀렸습니다."만 출력 (2차 Enrichment 단계에서 검색 후 보강하기 위함)
    - 정답 처리: 기존 해설을 요약하여 칭찬과 함께 제공
    """

    # 1. Few-shot Input (다양한 케이스: 정답, 오답, 오타, 문장형 답안 포함)
    example_input = """
    다음 5개의 퀴즈 답안을 채점해줘.

    [문제 1]
    - 유형: short_answer
    - 문제: 자바 소스 코드를 컴파일하면 생성되는 중간 코드는 무엇인가?
    - 실제 정답: 바이트코드
    - 기존 해설: 자바 컴파일러는 소스(.java)를 JVM이 이해할 수 있는 바이트코드(.class)로 변환합니다.
    - 사용자 답: Byte Code

    [문제 2]
    - 유형: fill_in_blank
    - 문제: 데이터베이스에서 중복을 허용하지 않는 유일한 키를 _____ (이)라고 한다.
    - 실제 정답: 기본키
    - 기존 해설: 기본키(Primary Key)는 테이블 내에서 각 행을 식별하는 고유한 값입니다.
    - 사용자 답: 외래키

    [문제 3]
    - 유형: short_answer
    - 문제: OOP의 특징 중 하나로, 구현 세부 사항을 숨기고 인터페이스만 제공하는 것을 무엇이라 하는가?
    - 실제 정답: 캡슐화
    - 기존 해설: 캡슐화는 데이터와 메서드를 하나로 묶고 외부에서의 접근을 제어하여 정보 은닉을 수행합니다.
    - 사용자 답: 캡슐화는 정보를 은닉하는 것입니다.

    [문제 4]
    - 유형: short_answer
    - 문제: 웹 브라우저와 서버 간의 통신을 위해 사용되는 프로토콜의 약자는?
    - 실제 정답: HTTP
    - 기존 해설: HyperText Transfer Protocol의 약자로, 웹에서 데이터를 주고받는 규칙입니다.
    - 사용자 답: h t t p

    [문제 5]
    - 유형: multiple_choice
    - 문제: 다음 중 스택(Stack) 자료구조의 특징으로 올바른 것은?
    - 실제 정답: LIFO (Last In First Out)
    - 기존 해설: 스택은 나중에 들어온 데이터가 먼저 나가는 후입선출 구조입니다.
    - 사용자 답: FIFO (First In First Out)
    """

    # 2. Few-shot Output (JSON 포맷)
    # 핵심: 오답인 2번, 5번은 피드백을 매우 짧게 가져감.
    example_output = """
    {{
        "results": [
            {{
                "is_correct": true,
                "feedback": "정답입니다! 영문으로 'Byte Code'라고 적으셨지만 의미가 정확하므로 정답입니다. 이는 JVM이 이해하는 중간 코드입니다."
            }},
            {{
                "is_correct": false,
                "feedback": "틀렸습니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! 문장으로 설명하셨지만 핵심 키워드인 '캡슐화'가 포함되어 있어 정답입니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! 띄어쓰기가 포함되어 있지만 'HTTP'를 의미하므로 정답 처리되었습니다."
            }},
            {{
                "is_correct": false,
                "feedback": "틀렸습니다."
            }}
        ]
    }}
    """

    return ChatPromptTemplate.from_messages([
        ("system", """
        너는 정확한 'AI 채점관'이다. 사용자가 제출한 5개의 퀴즈 답안을 채점해라.

        [채점 기준]
        1. **유연한 채점(Fuzzy Matching)**: 오타, 대소문자, 띄어쓰기 차이는 무시하고 정답으로 인정해라.
        2. **핵심 키워드**: 문장형 답안이라도 핵심 키워드가 포함되면 정답이다.

        [피드백 가이드]
        - **정답일 때**: "정답입니다!"와 함께 기존 해설을 요약해서 1~2문장으로 적어라.
        - **오답일 때**: 오직 "틀렸습니다."라고만 적어라. (절대 정답을 미리 알려주거나 해설하지 마라. 이는 다음 단계에서 처리할 것이다.)
        """),
        
        # Few-shot 적용
        ("human", example_input),
        ("ai", example_output),

        # 실제 데이터 입력
        ("human", "{formatted_quiz_block}")
    ])


# 해설 보강 프롬프트
def get_enrichment_prompt() -> ChatPromptTemplate:
    """
    [Phase 2] 오답 심화 해설용 프롬프트 (RAG)
    - 특징: '강의 내용'과 '웹 검색 결과'를 시각적으로 명확히 분리하여 제공
    """
    
    # ------------------------------------------------------------------
    # 1. Few-shot Example 1: 데이터베이스 (Foreign Key vs Primary Key)
    # ------------------------------------------------------------------
    example_input_1 = """
    [문제]: 관계형 데이터베이스에서 행(Row)을 유일하게 식별하는 키는?
    [학생의 오답]: 외래키(Foreign Key)
    [실제 정답]: 기본키(Primary Key)
    [기존 해설]: 기본키는 테이블 내에서 중복될 수 없는 고유한 값입니다. 외래키는 다른 테이블을 참조하는 키입니다.
    
    [웹 검색 결과]:
    [자료 1]
    - 제목: DB 기초: PK와 FK의 차이점
    - 내용: Primary Key(기본키)는 주민등록번호처럼 유일해야 합니다. Foreign Key는 테이블 간 연결 고리입니다.
    - 출처(URL): https://example.com/db-basics
    """
    
    example_output_1 = """
    아, **외래키**와 혼동하셨군요! 처음 배우면 용어가 비슷해서 충분히 헷갈릴 수 있어요. 😉
    
    **📘 강의 포인트**
    정답은 **기본키(Primary Key)**입니다.
    기존 해설에 따르면, 기본키는 테이블 안에서 데이터를 식별하는 '유일하고 고유한 값'을 의미해요. 반면 작성하신 외래키는 다른 테이블과 연결할 때 사용하는 참조용 키입니다.

    **🔎 웹 심화 학습**
    검색 결과를 통해 더 쉬운 예시를 찾아봤어요.
    우리의 **주민등록번호**나 **지문**이 대표적인 기본키라고 합니다. 세상에 나와 똑같은 번호를 가진 사람은 없으니까요! 이렇게 '유일무이한 값'이라고 기억하면 절대 잊지 않으실 거예요.
    
    👉 **더 알아보기**: [DB 기초: PK와 FK의 차이점](https://example.com/db-basics)
    """

    # ------------------------------------------------------------------
    # 2. Few-shot Example 2: 자료구조 (Stack vs Queue)
    # ------------------------------------------------------------------
    example_input_2 = """
    [문제]: 스택(Stack)의 입출력 방식은?
    [학생의 오답]: FIFO
    [실제 정답]: LIFO
    [기존 해설]: 스택은 나중에 들어간 것이 먼저 나오는 후입선출(LIFO) 구조입니다.
    
    [웹 검색 결과]:
    [자료 1]
    - 제목: 자료구조 스택(Stack) 완벽 정리
    - 내용: 스택은 LIFO 구조입니다. 웹 브라우저의 '뒤로 가기' 버튼이나 문서 작성 프로그램의 '실행 취소(Undo)'가 대표적입니다.
    - 출처(URL): https://dev-blog.com/stack-structure
    """
    
    example_output_2 = """
    아쉽네요! 반대로 생각하셨어요. 😅
    
    **📘 강의 포인트**
    정답은 **LIFO (Last In, First Out)**, 즉 '후입선출' 구조입니다.
    강의 내용에서 강조했듯이, 스택은 나중에 들어온 데이터가 가장 먼저 나가는 구조예요. 선택하신 FIFO는 줄 서기처럼 먼저 온 사람이 먼저 나가는 '큐(Queue)'의 특징이랍니다.

    **🔎 웹 심화 학습**
    이해를 돕기 위해 최신 활용 사례를 찾아봤어요.
    우리가 매일 쓰는 웹 브라우저의 **'뒤로 가기' 버튼**이 바로 스택이에요. 가장 마지막에 본 페이지가 제일 먼저 나오잖아요?
    
    더 자세한 내용은 아래 링크를 참고해보세요!
    👉 **출처**: [자료구조 스택(Stack) 완벽 정리](https://dev-blog.com/stack-structure)
    """

    # ------------------------------------------------------------------
    # 3. Prompt Construction
    # ------------------------------------------------------------------
    return ChatPromptTemplate.from_messages([
        ("system", """
        너는 학생의 학습을 돕는 따뜻하고 통찰력 있는 'AI 튜터'다.
        학생이 문제를 틀렸으므로, 기존 해설에 더해 **명확한 출처가 있는 심화 설명**을 작성해라.

        [입력 데이터]
        1. 퀴즈 정보 (문제, 정답, 기존 해설)
        2. 학생의 오답 (오답의 원인 추론)
        3. Google 검색 결과 (URL이 포함된 포맷팅된 텍스트)

        [작성 지침]
        1. **공감과 격려**: "틀렸습니다" 대신 "아쉽네요!", "헷갈릴 수 있어요" 등 부드러운 존댓말(해요체)로 시작해라.
        2. **구조화된 출력 (반드시 지킬 것)**:
           - **📘 강의 포인트**: '기존 해설(강의 자료)'을 요약하여 정답의 핵심 정의를 설명해라.
           - **🔎 웹 심화 학습**: 'Google 검색 결과'를 활용하여 최신 사례, 비유, 심화 정보를 덧붙여라.
        3. **URL 출처 표기**:
           - 웹 검색 내용을 인용할 때는, 반드시 제공된 URL을 포함해라.
           - 형식: `👉 **출처**: [글 제목](URL)` 또는 `[글 제목](URL)` 링크 형식 사용.
        4. **팩트 체크**: 제공된 [웹 검색 결과] 목록에 없는 URL은 절대 생성하지 마라. (Hallucination 방지)
        5. **길이**: 가독성을 위해 500자 이내로 핵심만 전달해라.
        """),
        
        # Few-shot
        ("human", example_input_1),
        ("ai", example_output_1),
        ("human", example_input_2),
        ("ai", example_output_2),

        # 실제 응답
        ("human", """
        [문제]: {question}
        [학생의 오답]: {user_answer}
        [실제 정답]: {correct_answer}
        [기존 해설]: {explanation}
        
        [웹 검색 결과]:
        {search_results}
        
        위 내용을 바탕으로 출처가 명확히 구분된 피드백을 작성해라.
        """)
    ])