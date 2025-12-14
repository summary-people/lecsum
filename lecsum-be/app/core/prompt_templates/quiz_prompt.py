# 문제 생성 / 채점 프롬프트 템플릿
from langchain_core.prompts import ChatPromptTemplate

def get_quiz_prompt() -> ChatPromptTemplate:
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
        ("human", "강의 내용: {context}"),
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
    
    # JSON 포맷에 type과 options 추가
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

def get_refiner_prompt() -> ChatPromptTemplate:
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

        # --- Few-shot Example ---
        ("human", f"""
        [학습 자료]
        {example_context}
        
        [퀴즈 초안]
        {example_initial_quiz}
        
        [비평]
        {example_critique}
        """),        
        ("ai", example_final_quiz),        


        ("human", """
        [학습 자료]
        {context}
        
        [퀴즈 초안]
        {initial_quiz}
        
        [비평]
        {critique}
        """)
    ])







# 채점 프롬프트

def get_grading_prompt() -> ChatPromptTemplate:
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
    - 사용자 답: http

    [문제 5]
    - 유형: multiple_choice
    - 문제: 다음 중 스택(Stack) 자료구조의 특징으로 올바른 것은?
    - 실제 정답: LIFO (Last In First Out)
    - 기존 해설: 스택은 나중에 들어온 데이터가 먼저 나가는 후입선출 구조입니다.
    - 사용자 답: FIFO (First In First Out)
    """

    example_output = """
    {{
        "results": [
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 한글 '바이트코드' 대신 영문 'Byte Code'로 적어주셨지만, 의미가 정확하므로 정답으로 인정됩니다. JVM이 이해하는 중간 단계 코드입니다."
            }},
            {{
                "is_correct": false,
                "feedback": "아쉽게도 틀렸습니다. 정답은 '기본키'입니다. \\n\\n해설: 작성하신 '외래키(Foreign Key)'는 다른 테이블을 참조할 때 사용하는 키입니다. 유일성을 보장하는 것은 '기본키'입니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 서술형으로 작성해주셨지만, 핵심 키워드인 '캡슐화'가 포함되어 있고 설명 또한 정확합니다."
            }},
            {{
                "is_correct": true,
                "feedback": "정답입니다! \\n\\n해설: 대소문자 구분 없이 'http'도 정답으로 인정됩니다. 웹 통신의 기본이 되는 프로토콜입니다."
            }},
            {{
                "is_correct": false,
                "feedback": "틀렸습니다. 정답은 'LIFO'입니다. \\n\\n해설: 선택하신 FIFO는 큐(Queue)의 특징입니다. 스택은 '후입선출(Last In First Out)' 구조라는 점을 기억해주세요!"
            }}
        ]
    }}
    """
    return ChatPromptTemplate.from_messages([
        ("system", """
        당신은 친절하고 정확한 AI 튜터다. 사용자가 제출한 5개의 퀴즈 답안을 채점해야 한다.

        [채점 기준]
        **단답형(short_answer) / 빈칸 채우기(fill_in_blank)**:
           - **유연한 채점(Fuzzy Matching)**을 적용해라.
           - 오타, 띄어쓰기 차이, 대소문자 차이는 무시하고 정답으로 인정해라.
           - 핵심 의미가 통하는 동의어도 정답으로 인정해라. (예: '객체 지향' == '객체지향 프로그래밍')
           - 사용자가 문장으로 답하더라도 핵심 키워드가 포함되어 있으면 정답으로 간주해라.

        [피드백 가이드]
        - **정답일 때**: 칭찬과 함께 기존 해설(explanation)을 요약해서 덧붙여라.
        - **오답일 때**: "아쉽네요, 틀렸습니다." 같은 말보다는, 왜 틀렸는지 설명하고 정답이 무엇인지 기존 해설을 바탕으로 친절하게 설명해라.
        - 한국어로 자연스럽게 작성해라.
        """),

        # Few-shot
        ("human", example_input),
        ("ai", example_output),

        # 실제 요청
        ("human", "{formatted_quiz_block}")       
    ])